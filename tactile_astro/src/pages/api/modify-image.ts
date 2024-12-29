// Form submit handler in TypeScript

export async function handleFormSubmit(event: SubmitEvent) {
  event.preventDefault();

  const form = event.target as HTMLFormElement;
  const formData = new FormData(form);

  try {
    // sends post to azure func, currently locally.. still needs capabilities to upload to blob 
    const response = await fetch('http://localhost:7071/api/process-image', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Failed to process the image');
    }

    const data: { processedImageUrl: string } = await response.json();
    const processedImageUrl = data.processedImageUrl;
    // Update the image URL on success
    const imageElement = document.getElementById('processed-image') as HTMLImageElement;
    imageElement.src = processedImageUrl;
  } catch (err) {
    console.error('Error:', err);
    alert('An error occurred while processing the image');
  }
}
