from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from app.ocr import perform_ocr
from typing import List

app = FastAPI()

def classify_text(text, doc_keywords):
    matching_types = []
    for key, keywords_list in doc_keywords.items():
        for keyword in keywords_list:
            if keyword in text:
                matching_types.append(key)

    if not matching_types:
        return ["Unclassified"]
    
    return list(set(matching_types))


def classify_document_side(document_type, text, doc_keywords, side):
    classified_side = []
    if document_type not in side or document_type not in doc_keywords:
        classified_side.append("Invalid document type")
        return classified_side

    front_keywords = side[document_type]["front"]
    back_keywords = side[document_type]["back"]

    front_present = any(keyword in text for keyword in front_keywords)
    back_present = any(keyword in text for keyword in back_keywords)

    if front_present and back_present:
        classified_side.append("Front")
        classified_side.append("Back")
        return classified_side
    elif front_present:
        classified_side.append("Front")
        return classified_side
    elif back_present:
        classified_side.append("Back")
        return classified_side
    else:
        classified_side.append("Not identified")
        return classified_side


# @app.post("/upload/image")
# async def upload_image(file: UploadFile = File(...)):
#     doc_keywords = {"aadhar": ["government of india", "unique identification authority", "uidai", "help@uidai.gov.in"],
#                 "pan": ["income tax department", "permanent account number", "income tax pan services unit"],
#                 "passport": ["nationality", "republic of india", "country code"],
#                 "voter": ["election commission of india", "epic", "elector", "elector's", "electoral registration officer"]}
#     side = {
#     "voter": 
#     {
#         "front": ["election commission of india", "elector"],
#         "back": ["electoral registration officer"]
#     },
#     "aadhar":
#     {
#         "front": ["government of india"],
#         "back": ["unique identification authority"]
#     },
#     "pan":
#     {
#         "front": ["income tax department"],
#         "back": ["income tax pan services unit", "nsdl"]
#     },
#     "passport":
#     {
#         "front": ["nationality", "republic of india"],
#         "back": [""]
#     }}
#     try:
#         # Save the uploaded image temporarily
#         with open(file.filename, "wb") as image_file:
#             image_file.write(file.file.read())

#         # Perform OCR on the image
#         ocr_text = perform_ocr(file.filename)
#         print(ocr_text)

#         # Classify document type based on OCR text
#         document_type = classify_text(ocr_text, doc_keywords=doc_keywords)

#         # Classify document side based on OCR text and document type
#         response = {}
#         for doc in document_type:
#             doc_side = classify_document_side(doc, ocr_text, doc_keywords, side)
#             try:
#                 response[doc].extend(doc_side)
#             except:
#                 response[doc] = doc_side

#         # return JSONResponse(content={"document_type": document_type, "document_side": document_side})
#         return JSONResponse(content=response)
#     finally:
#         # Remove the temporary image file
#         import os
#         os.remove(file.filename)

@app.post("/upload/images")
async def upload_images(files: List[UploadFile] = File(...)):
    doc_keywords = {
        "aadhar": ["government of india", "unique identification authority", "uidai", "help@uidai.gov.in"],
        "pan": ["income tax department", "permanent account number", "income tax pan services unit"],
        "passport": ["nationality", "republic of india", "country code"],
        "voter": ["election commission of india", "epic", "elector", "elector's", "electoral registration officer"]
    }

    side = {
        "voter": {
            "front": ["election commission of india", "elector"],
            "back": ["electoral registration officer"]
        },
        "aadhar": {
            "front": ["government of india"],
            "back": ["unique identification authority"]
        },
        "pan": {
            "front": ["income tax department"],
            "back": ["income tax pan services unit", "nsdl"]
        },
        "passport": {
            "front": ["nationality", "republic of india"],
            "back": [""]
        }
    }

    response = {}

    for file in files:
        try:
            # Save the uploaded image temporarily
            with open(file.filename, "wb") as image_file:
                image_file.write(file.file.read())

            # Perform OCR on the image
            ocr_text = perform_ocr(file.filename)
            print(ocr_text)

            # Classify document type based on OCR text
            document_types = classify_text(ocr_text, doc_keywords=doc_keywords)

            # Classify document side based on OCR text and document type
            classification_results = {}
            for doc_type in document_types:
                doc_side = classify_document_side(doc_type, ocr_text, doc_keywords, side)
                classification_results[doc_type] = doc_side

            # Store the classification results in the response dictionary with the filename as the key
            response[file.filename] = classification_results

        finally:
            # Remove the temporary image file
            import os
            os.remove(file.filename)

    return JSONResponse(content=response)


