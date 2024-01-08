# Document ID classification

This repository contains the code for the internship task for classification of Document ID.

## Setup

Install docker on your machine and run the following commands to setup the docker container from the root folder of this directory:
* `docker build -t idclassifier .`
This builds a docker image.

* `docker run -d --name classifiercontainer -p 80:80 idclassifier`
This runs the docker image with the container name: `classifiercontainer` on port `80`.

Setup the google ocr credentials and paste the json in the app directory with the name: `google_cloud_creds.json`. 
Or you can change the name of the json and refactorize the name in the `ocr.py` file.

## Post requests to the API

We can access the swagger ui from the docker image and send post requests to the api.

Additionally there's a `send.py` script which can be used to send post requests programmatically to the api.


Run the following command to run the `send.py` file with your image path:
`python3 send.py --image_paths images/wring.jpeg --fastapi-url http://127.0.0.1:80/upload/ images`