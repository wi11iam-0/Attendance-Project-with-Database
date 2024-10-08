import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("Attendance Project with Database/ServiceAccountKey.json")   # path to access key to the database
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://attendance-project-48fde-default-rtdb.firebaseio.com/"   # location of the database
})

ref = db.reference("Students")  # create a section student section in the database

data = {
    '321654':
        {
            'name': 'Murtaza Hassan',
            'major': 'Robotics',
            'starting_year': 2020,
            'total_attendance': 6,
            'standing': 'G',
            'year': 4,
            'last_attendance_time': '2022-12-11 00:54:34'
        },
    '573744':
        {
            'name': 'William Coneac',
            'major': 'Electrical Engineering',
            'starting_year': 2023,
            'total_attendance': 10,
            'standing': 'G',
            'year': 2,
            'last_attendance_time': '2022-12-10 00:45:43'
        },
    '852741':
        {
            'name': 'Emily Blunt',
            'major': 'English Literature',
            'starting_year': 2020,
            'total_attendance': 25,
            'standing': 'G',
            'year': 4,
            'last_attendance_time': '2022-12-09 00:54:34'
        },
    '963852':
        {
            'name': 'Elon Musk',
            'major': 'Rocket Science',
            'starting_year': 2019,
            'total_attendance': 30,
            'standing': 'G',
            'year': 5,
            'last_attendance_time': '2022-12-11 00:54:34'
        }
}


for key, value in data.items():     # sends the data to the database
    ref.child(key).set(value)   
    