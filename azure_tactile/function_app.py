import logging
import os
import json
from azure.storage.blob import BlobServiceClient
import azure.functions as func
from io import BytesIO
from PIL import Image
import base64
import cv2

#TODO: seems good, needs to be tested though

# Initialize the BlobServiceClient, need to enter blob_connection_string and container_name
blob_connection_string = "azure_storage_string"
blob_service_client = BlobServiceClient.from_connection_string(blob_connection_string)
container_name = "tactile_images"

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing image upload request.')

    # Check if an image was uploaded
    if 'image' not in req.files:
        return func.HttpResponse(
            json.dumps({"error": "No file part"}),
            status_code=400,
            mimetype="application/json"
        )

    image = req.files['image']
    if image.filename == '':
        return func.HttpResponse(
            json.dumps({"error": "No selected file"}),
            status_code=400,
            mimetype="application/json"
        )

    # Save the uploaded image temporarily
    filename = image.filename
    file_path = os.path.join('/tmp', filename)  # Azure Functions have a temporary file system at /tmp

    with open(file_path, 'wb') as f:
        f.write(image.read())

    # Process the image using process_img function
    tactile_image_path = process_img(file_path)

    # Upload the processed image to Azure Blob Storage
    processed_filename = os.path.basename(tactile_image_path)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=processed_filename)
    with open(tactile_image_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    
    # Construct URL to the processed image
    processed_image_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{processed_filename}"

    # Return the URL of the processed image for download
    # TODO: is this enough for the astro to show/ allow download of?
    return func.HttpResponse(
        json.dumps({"processedImageUrl": processed_image_url}),
        status_code=200,
        mimetype="application/json"
    )



# TODO: Add err handling
def process_img(image_path):

    image = cv2.imread(image_path)

    # Check if image was loaded correctly
    if image is None:
        raise ValueError(f"Error loading image: {image_path}")

    # Edited to just take file_path as image and work off of that
    image_grayscaled = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image_equalized = cv2.equalizeHist(image_grayscaled)

    """
    Fine-grained saliency detection from
    Sebastian Montabone and Alvaro Soto.
    Human detection using a mobile platform and novel features derived from a visual saliency mechanism.
    In Image and Vision Computing, Vol. 28 Issue 3, pages 391–402. Elsevier, 2010.
    Source: https://docs.opencv.org/3.4.3/da/dd0/classcv_1_1saliency_1_1StaticSaliencyFineGrained.html
    """
    fine_saliency = cv2.saliency.StaticSaliencyFineGrained_create()
    _, fine_saliency_map = fine_saliency.computeSaliency(image_equalized)

    # Scale the values to [0, 255]
    fine_saliency_map = (fine_saliency_map * 255).astype('uint8')

    # Compute binary threshold map
    threshold_map = cv2.threshold(
        fine_saliency_map.astype('uint8'), 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    # Invert the binary threshold map so it is Swell Paper Tactile Printer friendly
    inverse_threshold_map = cv2.bitwise_not(threshold_map)

    # Should save to be /tmp/tactile_image.ext, tmp being azures temp file tree
    # Ensure the output path is correct for your environment (e.g., Azure)
    # Added some err handling because I could see this causing issues. I dont want it to make a new dir if it doesn't 
    # exist because I could see that cousing issues with the cloud..
    output_dir = "azure_tactile/tmp"  
    if not os.path.exists(output_dir):
        raise FileNotFoundError(f"The directory '{output_dir}' does not exist. Please ensure the directory exists before saving the image.")
    output_filename = "tactile_" + os.path.basename(image_path)
    output_path = os.path.join(output_dir, output_filename)

    # Save image
    cv2.imwrite(output_path, inverse_threshold_map)


    return output_path