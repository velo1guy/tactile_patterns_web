# Tactile Image Web App:

## What is this?:
This is a version of the CLI application viewable [here](https://github.com/wwu-webtech/Tactile_Patterns). This project is currently under my personal github account but will be moved to the WWU account when they are ready.

## Installation:

Start by installing python, which can be found [here](https://www.python.org/downloads/) or by running `sudo apt install python`. Next run `git clone https://github.com/velo1guy/tactile_patterns_web.git`. Once this has been done succsessfully, enter this directory, and in the `azure_tactile` subdirectory, run `python -m venv venv` and your virtual enviornment should be set up. Once in the venv, run `pip install -r requirements.txt`, and your requirments should be installed. If not already installed, you can do so by running `npm create astro@latest`. Finally, run n`pm install -g azure-functions-core-tools@4 --unsafe-perm true` to install the necessary azure function tools.


## Setting up Locally:

As the azure portion needs to use blob storage inorder to function, it's necessary to set this up remotely or replace it with a local directory. To set up the frontend, go into the tactile_astro directory and run `npm run dev`. This will serve the content to a port that will be given. Note that the post in index.astro will need to be reconfigured to the URL of your azure content (this should be `http://localhost:7071/function_app/main`). Once this is done, the azure component can be set up by going into the azure_tactile directory and making sure the venv is set up as outlined above, run `source venv/bin/activate`. Once this is done, replace the blob_connection_string in function_app.py with your given blob connection string. Once this is done, you will need to configure your local settings json in the azure_tactile directory with your given values. If you are running locally, the only thing needing changing will be the blob storage string. Finally, run `func start`. You should see the url entered into the astro component printed out once this is done. If it is different, change the url in the astro component to the one printed out.