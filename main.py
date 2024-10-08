import cv2
import os
import pickle
import face_recognition
import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

# providing the credentials to the database and storage
cred = credentials.Certificate("Attendance Project with Database/ServiceAccountKey.json")   # path to access key to the database
firebase_admin.initialize_app(cred,{
    'databaseURL': "https://attendance-project-48fde-default-rtdb.firebaseio.com/",   # location of the database
    'storageBucket': "attendance-project-48fde.appspot.com"
})

bucket = storage.bucket()

camera = cv2.VideoCapture(0)
camera.set(3, 640)
camera.set(4, 480)

background = cv2.imread('Attendance Project with Database/Resources/background.png')

# importing mode images and storing them in a list
folder_path = 'Attendance Project with Database/Resources/Modes'
modes_name_list = os.listdir(folder_path)
modes_list = []

for path in modes_name_list:
    modes_list.append(cv2.imread(os.path.join(folder_path, path)))

# load encoding file and extract data
file = open('Attendance Project with Database/Encode_file.p', 'rb')
data_encodings_with_ID = pickle.load(file)
# split data into the encoding and ID components
data_encodings, student_ID = data_encodings_with_ID
file.close()

#print(student_ID)

mode_type = 0
counter = 0

while True:
    _, frame = camera.read()
    
    # sclaing the frame to 1/4 of its original size (prevents processing issues)
    frame_small = cv2.resize(frame, (0,0), None, 0.25, 0.25)
    frame_small = cv2.cvtColor(frame_small, cv2.COLOR_BGR2RGB)

    face_location = face_recognition.face_locations(frame_small)
    face_encoding = face_recognition.face_encodings(frame_small, face_location)

    # placing the frame on the background
    background[162:162+480, 55:55+640] = frame
    # placing the mode on the background
    background[44:44+633, 808:808+414] = modes_list[mode_type]

    if face_location:
        # loop through data encodings and check for any matches in the current frame
        for encoding, location in zip(face_encoding, face_location):
            matches = face_recognition.compare_faces(data_encodings, encoding)
            distance = face_recognition.face_distance(data_encodings, encoding)
            # mathes is a list of True/False elements indicating the position of the detected face
            # face_distance is a list of floats representing how likely/unlikely the frame is to be the data images

            #print('matches:', matches)
            #print('distance:', distance)

            # getting the index of the match
            match_index = np.argmin(distance)

            if matches[match_index]:    # if element with smallest distane is also 'True' in the match list
                
                id = student_ID[match_index]    # take the student's ID
                #print(ID)

                y1, x2, y2, x1 = location
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4     # resize the coordinates to fit the original frame
                cv2.rectangle(frame, (x1,y1), (x2, y2), (0,0,255), 2)

                #cv2.rectangle(frame, (x1, y2-35), (x2, y2), (255, 0, 0), cv2.FILLED)
                #cv2.putText(frame, ID, (x1+6, y2-6), cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,255), 2)
                
                if counter == 0:
                    counter = 1
                    mode_type = 1
        
        if counter!=0:
            if counter == 1:
                # taking data from database
                student_info = db.reference(f'Students/{id}').get()
                print(student_info)
                
                # taking image from storage
                blob = bucket.get_blob(f'Images/{id}.png') 
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                image_student = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

                # update and check last attendance time
                date_time_object = datetime.strptime(student_info['last_attendance_time'],
                                                    '%Y-%m-%d %H:%M:%S')
                seconds_elapsed = (datetime.now() - date_time_object).total_seconds()

                #updating the attendace data
                if seconds_elapsed >= 30:
                    ref = db.reference(f'Students/{id}')
                    student_info['total_attendance'] += 1
                    ref.child('total_attendance').set(student_info['total_attendance'])

                    student_info['last_attendance_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ref.child('last_attendance_time').set(student_info['last_attendance_time']) 
                else:
                    # update mode type to display 'already marked'
                    mode_type = 3
                    counter = 0
                    background[44:44+633, 808:808+414] = modes_list[mode_type]

            if mode_type != 3:

                # only update the display with the images if student has not been already marked
                if 10<counter<20:
                    mode_type = 2
                    background[44:44+633, 808:808+414] = modes_list[mode_type]

                if counter <= 10:

                    # displaying all the student info on the user interface
                    cv2.putText(background,str(student_info['total_attendance']), (861,125), cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,255), 1)
                    cv2.putText(background,str(student_info['major']), (1006,550), cv2.FONT_HERSHEY_COMPLEX, 0.5, (100,100,100), 1)
                    cv2.putText(background,str(id), (1006,494), cv2.FONT_HERSHEY_COMPLEX, 0.5, (100,100,100), 1)
                    cv2.putText(background,str(student_info['standing']), (910,625), cv2.FONT_HERSHEY_COMPLEX, 0.6, (100,100,100), 1)
                    cv2.putText(background,str(student_info['year']), (1025,625), cv2.FONT_HERSHEY_COMPLEX, 0.6, (100,100,100), 1)
                    cv2.putText(background,str(student_info['starting_year']), (1125,625), cv2.FONT_HERSHEY_COMPLEX, 0.6, (100,100,100), 1)

                    # centering the name text
                    (w, h), _ = cv2.getTextSize(student_info['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414-w)//2     # 414 is the width of the mode image
                    cv2.putText(background,str(student_info['name']), (808+offset,445), cv2.FONT_HERSHEY_COMPLEX, 1, (100,100,100), 1)

                    # displaying the student's image
                    background[175:175+216, 909:909+216] = image_student

              
            counter+=1

            if counter >= 20:       # if counter is 20 or above, reset all the modes and student variables
                counter = 0
                mode_type = 0
                student_info = []
                image_student = []
                background[44:44+633, 808:808+414] = modes_list[mode_type]

    else:
        mode_type = 0
        counter = 0  

    cv2.imshow("Webcam", background)

    
    if cv2.waitKey(1) == ord("q"):
        break
    

