# this code takes the encodngs of face in the images and stores it in a seperate file. These can then be accessed from the main when running the face recognition
# this code also takes each image and uploads it to the storage of the real-time database

import cv2
import face_recognition
import os
import pickle
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

# providing the credentials to the database and storage
cred = credentials.Certificate("Attendance Project with Database/ServiceAccountKey.json")   # path to access key to the database
firebase_admin.initialize_app(cred,{
    'databaseURL': "https://attendance-project-48fde-default-rtdb.firebaseio.com/",   # location of the database
    'storageBucket': "attendance-project-48fde.appspot.com"
})


def find_encodings(images_list):
    encoding_list = []
    for image in images_list:
        # convert colour to RGB and face detection library requires this
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # the [0] at the end is because we need the first face detected in the image (image anyway should only have 1 face)
        encode = face_recognition.face_encodings(image)[0]
        
        encoding_list.append(encode)
    
    return encoding_list


# import the data images and store each image in a list
folder_path = 'Attendance Project with Database/Images'
image_name_list = os.listdir(folder_path)   # creates list of the image names, including the '.png' at the end
images_list = []
student_ID = []

for image in image_name_list:
    images_list.append(cv2.imread(os.path.join(folder_path, image)))    # stores each image in a list
    student_ID.append(os.path.splitext(image)[0])   # [0] is there as only the ID part of the name is required, not the 'png'

    # this following section is for uploading the images to the storage of the real-time database
    file_path = f'{folder_path}/{image}'     # path to each image
    storage_path = f'Images/{image}'
    bucket = storage.bucket()
    blob = bucket.blob(storage_path)    # blob of data to be sent to the storage. This is where you decide the path of the data in the storage
    blob.upload_from_filename(file_path)    # uploads the blob to the storage 
    # file_path is the path of the images in pc and storage_path is the path they will have once stored in the storage

print("Encoding Started")
data_encodings = find_encodings(images_list)
print("Encoding Complete")


# save encodings in a file to import when running the main
data_encodings_with_ID = [data_encodings, student_ID]

# open the file (or create it if it hasn't already been) . 'wb' means writing is enabled but only in binary mode (binary data)
file = open("Attendance Project with Database/Encode_file.p", "wb")
# store the list of encodings with IDs in the file
pickle.dump(data_encodings_with_ID, file)
# close the file
file.close()
print("File saved")

