import cv2

def detect_faces(img):
    img = cv2.imread(img)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_detector = cv2.CascadeClassifier("app\haarcascade_frontalface_alt.xml")
    results = face_detector.detectMultiScale(gray, scaleFactor=1.15,minNeighbors=5,minSize=(34, 35), flags=cv2.CASCADE_SCALE_IMAGE)
    return results

def classify_side(img):
    results = detect_faces(img)
    if len(results) > 0:
        return ["Front"]
    else:
        return ["Back"]