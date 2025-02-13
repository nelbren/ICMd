# canvas - nelbren@nelbren.com @ 2025-02-05 - v1.1

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


def getStudents():
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


def dspStudents(students):
    for key, value in students.items():
        print(key, value)


if __name__ == "__main__":
    students = getStudents()
    dspStudents(students)
