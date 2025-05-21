# canvas - nelbren@nelbren.com @ 2025-02-14 - v1.2

import os
import json
import yaml
import requests


def getConfig():
    config = None
    try:
        with open("config.yml", "r") as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
            config = {
                "INSTRUCTURE_URL": data['INSTRUCTURE_URL'],
                "API_KEY": data['API_KEY'],
                "COURSE_ID": data['COURSE_ID'],
                # "ASSIGNMENT_ID": data['ASSIGNMENT_ID']
            }
    except IOError:
        print("Please make config.yml! ( ./config.bash )")
        exit(1)

    # print(data)
    return config


def getStudents_from_canvas():
    config = getConfig()
    base_url = config['INSTRUCTURE_URL']
    base_url += "/api/v1"
    api_key = config['API_KEY']
    course_id = config['COURSE_ID']
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {"enrollment_type[]": "student",
              "include[]": "enrollments", "per_page": "999"}
    response = requests.get(f'{base_url}/courses/{course_id}/users',
                            headers=headers, params=params)
    students = {}
    row = 0
    if response.status_code == 200:
        for student in response.json():
            row += 1
            id = student['integration_id']
            name = student['name'].upper()
            students[id] = {
                "row": row,
                "name": name,
                "last_update": 0,
                # "status": "❌",
                # "ip": "N/A"
                "color": "yellow",
                "ignored": False
            }
            # if row == 1:
            #     break
    return students


def createCSV(students):
    with open('students.json', 'w') as outfile:
        json.dump(students, outfile, indent=4)


def getStudents_from_json():
    students = {}
    with open('students.json', 'r') as openfile:
        students = json.load(openfile)
    return students


def addStudentsCounts(students):
    for key, value in students.items():
        # print('student->', key, value)
        value['countTimeout'] = 0
        value['countInternet'] = 0
        value['countIA'] = 0
        # print(value)
        students[key] = value
    return students


def getStudents():
    if not os.path.exists("students.json"):
        print("Getting students from Canvas...")
        students = getStudents_from_canvas()
        createCSV(students)
    print("Getting students from students.json...")
    students = getStudents_from_json()
    print(students)
    students = addStudentsCounts(students)
    return students


def dspStudents(students):
    for key, value in students.items():
        print(key, value)


if __name__ == "__main__":
    students = getStudents()
    dspStudents(students)
