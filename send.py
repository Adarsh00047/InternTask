import requests
import argparse
from PIL import Image
import os
from pdf2image import convert_from_path
import tempfile
import shutil

def convert_pdf_to_images(pdf_path, tmp_dir):
    # Convert PDF to images
    images = convert_from_path(pdf_path, 500)

    # Save images to the temporary folder
    image_paths = []
    for count, image in enumerate(images):
        image_path = f'{tmp_dir}/out{count}.jpg'
        image.save(image_path, 'JPEG')
        image_paths.append(image_path)
    
    return image_paths


def convert_tiff_to_jpg(image_path):
    if image_path.lower().endswith(".tiff") or image_path.lower().endswith(".tif"):
        # Convert .tiff to .jpg
        img = Image.open(image_path)
        jpg_path = f'{image_path.replace(".tiff", ".jpg").replace(".tif", ".jpg")}'
        img.convert("RGB").save(jpg_path, "JPEG")
        img.close()
        return jpg_path
    else:
        return image_path

def post_image_to_fastapi(image_file_path, fastapi_url):
    tmp_dir = None
    converted_path = None
    try:
        if image_file_path.lower().endswith(".pdf"):
            tmp_dir = tempfile.mkdtemp()
            image_paths = convert_pdf_to_images(image_file_path, tmp_dir)
        else:
            # Convert .tiff to .jpg if needed
            converted_path = convert_tiff_to_jpg(image_file_path)
            image_paths = [converted_path]
        # Create a list of files to send in the request
        files = [("files", (image_path.split("/")[-1], open(image_path, "rb"), "image/jpeg")) for image_path in image_paths]
        # Send a POST request to the FastAPI server
        response = requests.post(fastapi_url, files=files)

        # Print the response content
        if response.status_code != 500:
            print(response.json())
            if converted_path: 
                for file in files:
                    file[1][1].close()
                os.remove(converted_path)
        else:
            print("Internal Server Error")
        for file in files:
            file[1][1].close()
    finally:
        # Remove the temporary folder
        if tmp_dir:
            shutil.rmtree(tmp_dir)

    

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Upload images to FastAPI server.")
    parser.add_argument("--image_paths", nargs="+", help="Paths to image files to upload")
    parser.add_argument("--fastapi-url", default="http://127.0.0.1:8000/upload/images", help="URL of your FastAPI server")
    args = parser.parse_args()

    # Iterate through provided image paths and post each image to the FastAPI server
    for image_path in args.image_paths:
        post_image_to_fastapi(image_path, args.fastapi_url)
