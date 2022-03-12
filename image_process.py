# from deepface.commons import functions
from keras_facenet import FaceNet
from arcface import ArcFace
from cv2 import cv2
import numpy as np
from PIL import Image
import insightface
from math import sqrt

arcface_model = ArcFace.ArcFace()
facenet_model = FaceNet()
insightface_model = insightface.model_zoo.get_model('retinaface_r50_v1')
insightface_model.prepare(ctx_id = -1, nms=0.4)

def get_face(image):
    # Detect Face (Fist round)
    bbox, landmark = insightface_model.detect(image, threshold=0.95, scale=1.0)
    # Check face profile
    # A face was found
    if len(bbox) == 1 and bbox.any() and landmark.any():
        # Align face (First round)
        first_align = insightface.utils.face_align.norm_crop(image, landmark[0])
        # Detect face (Second round)
        bbox, landmark = insightface_model.detect(first_align, threshold=0.7, scale=1.0)
        if not bbox.any():
            return np.array([-3])
        # Align face (Second round)
        second_align = insightface.utils.face_align.norm_crop(first_align, landmark[0])
        # Detect face (Third round)
        bbox, landmark = insightface_model.detect(second_align, threshold=0.7, scale=1.0)
        if not bbox.any():
            return np.array([-3])
        # Check face profile
        (startX, startY, endX, endY) = bbox[0][:4].astype("int")
        eye1, eye2 = landmark[0][0], landmark[0][1]
        bbox_side = abs(startX - endX)
        eye_distance = sqrt(pow((eye1[0]-eye2[0]), 2) + pow((eye1[1]-eye2[1]), 2))
        eye_ratio = float(eye_distance/bbox_side)
        # if face si not frontal enough
        # print("EYE RATIO: ", eye_ratio)
        if eye_ratio < 0.38:
            return np.array([-4])
        # Get final face box
        if bbox.any():
            (startX, startY, endX, endY) = [0 if n<0  else n for n in bbox[0][:4].astype("int")]
            final_face = second_align[startY:endY, startX:endX]
            return final_face
        else:
            return np.array([-3])
    # Multiple faces where found    
    elif len(bbox) > 1:
        return np.array([-1])
    # No face was found    
    else:
        return np.array([-2])

def calc_emb(image):

    arcface_emb = arcface_model.calc_emb(cv2.resize(image, (112,112)))
    facenet_emb = facenet_model.embeddings([cv2.resize(image, (160,160))])[0]

    return [arcface_emb, facenet_emb]

def process(image):
    temp_im = image.rotate(0)
    for i in range (90, 360, 90):
        # Try to get a face
        face = get_face(np.asarray(temp_im))
        # A face was found / multiple where found / photo is not adecuate / face is not aligned-> break
        if len(face) > 1 or face[0] == -1 or face[0] == -3 or face[0] == -4:
            break
        # No face found -> countinue trying (rotate)
        else:
            # print(f"No face found -> Rotating {i}...")
            temp_im = image.rotate(i)
            # temp_im.show()

    if len(face) <= 1 or not face.any():
        # print("ERROR in face detection", face)
        return face
    else:
        # print('face detected', face.shape)
        # Image.fromarray(un_norm_face.astype(np.uint8)).show()
        # Image.fromarray(face.astype(np.uint8)).show()
        # Calculate arcface and facenet embeddings for image
        embeddings = calc_emb(face.astype(np.uint8))
        # Print embeddings shapes
        # print(f'Arcface embedding shape: {embeddings[0].shape}\nFacenet embedding shape: {embeddings[1].shape}')
        # add new embeddings to chat data

        return np.array(embeddings)