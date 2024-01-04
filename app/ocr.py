from google.oauth2 import service_account
from google.cloud import vision
import io

credentials = service_account.Credentials.from_service_account_file(
	filename="app/google_cloud_creds.json",
	scopes=["https://www.googleapis.com/auth/cloud-platform"])
client = vision.ImageAnnotatorClient(credentials=credentials)

def perform_ocr(image):
    with io.open(image, "rb") as f:
        byteImage = f.read()  
    print("[INFO] making request to Google Cloud Vision API...")
    image = vision.Image(content=byteImage)
    response = client.text_detection(image=image)
    if response.error.message:
        raise Exception(
		"{}\nFor more info on errors, check:\n"
		"https://cloud.google.com/apis/design/errors".format(
			response.error.message))
    ocr_texts = []
    for text in response.text_annotations[1::]:
        ocr_texts.append(text.description)
    ocr_texts = [ocr.lower() for ocr in ocr_texts]
    ocr_texts = " ".join(ocr_texts)
    return ocr_texts