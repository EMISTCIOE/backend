import requests
import json

URL = "http://localhost:8000/api/notice/notices"

def get_data(id=None):
    data = {}
    if id is not None:
        data = {'id': id}
    json_data = json.dumps(data)
    headers = {'content-Type': 'application/json'}
    r = requests.get(url=URL, headers=headers, data=json_data)
    data = r.json()
    print(data)

get_data()

def post_data():
    data = {
        'title': 'New Notice',
        'description': 'This is a new notice',
        'notice_type': 'Department',
        'department_id': '10a3469f-58c7-4223-a85a-43278356e398'
    }
    headers = {'content-Type': 'application/json'}
    json_data = json.dumps(data)
    r = requests.post(url=URL, headers=headers, data=json_data)
    data = r.json()
    print(data)

post_data()