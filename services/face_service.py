import face_recognition_models
import face_recognition
import numpy as np

def encode_face(file):
    image = face_recognition.load_image_file(file)
    encodings = face_recognition.face_encodings(image)

    if len(encodings) == 0:
        return None

    return encodings[0]


def verify_face(file, stored_encoding):
    image = face_recognition.load_image_file(file)
    encodings = face_recognition.face_encodings(image)

    if len(encodings) == 0:
        return False

    unknown_encoding = encodings[0]

    # 🔥 STRICT MATCH
    result = face_recognition.compare_faces(
        [np.array(stored_encoding)],
        unknown_encoding,
        tolerance=0.6   # 🔥 more strict (default is 0.6)
    )

    return result[0]