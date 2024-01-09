from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from app.ocr import perform_ocr
from typing import List
from PIL import Image
from timeit import default_timer as timer
import tempfile
from pdf2image import convert_from_path
import shutil
from app.face import classify_side

app = FastAPI()

def classify_text(text, doc_keywords):
    matching_types = []
    for key, keywords_list in doc_keywords.items():
        for keyword in keywords_list:
            if keyword in text:
                matching_types.append(key)
    print(matching_types)

    if not matching_types:
        return ["Unclassified"]
    
    return list(set(matching_types))

@app.post("/upload/images")
async def upload_images(files: List[UploadFile] = File(...)):
    doc_keywords = {
        "aadhar": ["government of india", "unique identification authority", "uidai", "help@uidai.gov.in"],
        "pan": ["income tax department", "permanent account number", "income tax pan services unit", "govt of india", "tax"],
        "passport": ["nationality", "republic of india", "country code"],
        "voter": ["election commission of india", "epic", "elector", "elector's", "electoral registration officer", "clector's"]
    }

    response = {}

    for file in files:
        start = timer()
        print(file.content_type)
        if file.content_type == "application/pdf":
            tmp_dir = tempfile.mkdtemp()
            try:
                with open(file.filename, "wb") as pdf_file:
                    pdf_file.write(file.file.read())
                pages = convert_from_path(file.filename, 500)
                for count, page in enumerate(pages):
                    page.save(f'{tmp_dir}/out{count}.jpg', 'JPEG')
                import os
                image_files = os.listdir(tmp_dir)
                image_files = [f"{tmp_dir}/{image_name}" for image_name in image_files]
                image_files = sorted(image_files, key=lambda x: int(x.split("out")[1].split(".jpg")[0]))
                for image_file in image_files:
                    ocr_text = perform_ocr(image_file)
                    print(ocr_text)
                    document_types = classify_text(ocr_text, doc_keywords=doc_keywords)

                    # Classify document side based on OCR text and document type
                    classification_results = {}
                    for doc_type in document_types:
                        doc_side = classify_side(image_file)
                        classification_results[doc_type] = doc_side

                    # Store the classification results in the response dictionary with the filename as the key
                    response[f"{file.filename}/{image_file}"] = classification_results
                    end = timer()
                    response[f"{file.filename}/{image_file}"]["Time"] = end - start
            finally:
                import os
                os.remove(file.filename)
                shutil.rmtree(tmp_dir)
        else:        
            try:
                if file.content_type == "image/tiff":
                    # Convert .tiff to .jpeg
                    with open(file.filename, "wb") as image_file:
                        image_file.write(file.file.read())
                    with Image.open(file.file) as img:
                        jpeg_path = f"{file.filename.split('.')[0]}.jpeg"
                        img.convert("RGB").save(jpeg_path)
                    ocr_text = perform_ocr(jpeg_path)
                else:
                    # Save the uploaded image temporarily
                    with open(file.filename, "wb") as image_file:
                        image_file.write(file.file.read())
                    ocr_text = perform_ocr(file.filename)

                # Classify document type based on OCR text
                document_types = classify_text(ocr_text, doc_keywords=doc_keywords)

                # Classify document side based on OCR text and document type
                classification_results = {}
                for doc_type in document_types:
                    doc_side = classify_side(file.filename)
                    classification_results[doc_type] = doc_side

                # Store the classification results in the response dictionary with the filename as the key
                response[file.filename] = classification_results
                end = timer()
                response[file.filename]["Time"] = end - start


            finally:
                pass
                # Remove the temporary image file
                # import os
                # if file.content_type == "image/tiff":
                    # os.remove(jpeg_path)
                    # os.remove(file.filename)
                # else:
                    # os.remove(file.filename)

    return JSONResponse(content=response)


