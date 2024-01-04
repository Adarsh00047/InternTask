from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from app.ocr import perform_ocr

app = FastAPI()

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
    
def classify_text(text, doc_keywords):
    for key, keywords_list in doc_keywords.items():
        for keyword in keywords_list:
            if keyword in text:
                print(keyword)
                return key
    return "Unclassified"

@app.post("/upload/image")
async def upload_image(file: UploadFile = File(...)):
    doc_keywords = {"aadhar": ["government of india", "unique identification authority", "uidai", "help@uidai.gov.in"],
                "pan": ["income tax department", "permanent account number", "income tax pan services unit"],
                "passport": ["nationality", "republic of india", "country code"],
                "voter": ["election commission of india", "epic", "elector", "elector's", "electoral registration officer"]}
    side = {
    "voter": 
    {
        "front": ["election commission of india", "elector"],
        "back": ["electoral registration officer"]
    },
    "aadhar":
    {
        "front": ["government of india"],
        "back": ["unique identification authority"]
    },
    "pan":
    {
        "front": ["income tax department"],
        "back": ["income tax pan services unit", "nsdl"]
    },
    "passport":
    {
        "front": ["nationality", "republic of india"],
        "back": [""]
    }}
    try:
        # Save the uploaded image temporarily
        with open(file.filename, "wb") as image_file:
            image_file.write(file.file.read())

        # Perform OCR on the image
        ocr_text = perform_ocr(file.filename)
        print(ocr_text)

        # Classify document type based on OCR text
        document_type = classify_text(ocr_text, doc_keywords=doc_keywords)

        # Classify document side based on OCR text and document type
        document_side = classify_document_side(document_type, ocr_text, doc_keywords, side)

        return JSONResponse(content={"document_type": document_type, "document_side": document_side})

    finally:
        # Remove the temporary image file
        import os
        os.remove(file.filename)


