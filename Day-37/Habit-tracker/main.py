from urllib import response

import requests
import datetime
import os
from dotenv import load_dotenv
load_dotenv()


USERNAME = "dhanusha"
TOKEN = os.environ["TOKEN"]
GRAPH_ID = "graph1"


pixela_endpoint = "https://pixe.la/v1/users"

user_params = {
    "token": TOKEN,
    "username":USERNAME,
    "agreeTermsOfService":"yes",
    "notMinor":"yes",
}

# response=requests.post(url=pixela_endpoint, json=user_params)
# print(response.text)

grap_endpoint = f"{pixela_endpoint}/{USERNAME}/graphs"

graph_config = {
    "id":"graph1",
    "name":"Workout Graph",
    "unit":"calories",
    "type": "int",
    "color":"ajisai"

}

headers = {
    "X-USER-TOKEN": TOKEN,
}

# response=requests.post(url=grap_endpoint, json=graph_config, headers=headers)
# print(response.text)

pixel_creation_endpoint = f"{pixela_endpoint}/{USERNAME}/graphs/{GRAPH_ID}"

today = datetime.datetime.now()


pixel_data = {
    "date":today.strftime("%Y%m%d"),
    "quantity": input("How many Calories you burnt today?"),
}

response=requests.post(url=pixel_creation_endpoint, json=pixel_data, headers=headers)
print(response.text)

update_endpoint =f"{pixela_endpoint}/{USERNAME}/graphs/{GRAPH_ID}/{today.strftime('%Y%m%d')}"

update_data = {
    "quantity":"200"
}

# response=requests.put(url=update_endpoint,json=update_data,headers=headers)
#
# while response.json().get("isRejected"):
#     print("Request rejected, retrying...")
#     response=requests.put(url=update_endpoint,json=update_data,headers=headers)
# print(response.text)

delete_endpoint =f"{pixela_endpoint}/{USERNAME}/graphs/{GRAPH_ID}/{today.strftime('%Y%m%d')}"

# response=requests.delete(url=delete_endpoint,headers=headers)
# print(response.text)
