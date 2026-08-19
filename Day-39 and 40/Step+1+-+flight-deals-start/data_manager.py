from urllib import response

import requests
import os
from dotenv import load_dotenv
load_dotenv()

SHEETY_PRICES_ENDPOINT = os.environ["SHEETY_PRICES_ENDPOINT"]


class DataManager:
    #This class is responsible for talking to the Google Sheet.
    def __init__(self):
        self.users_endpoint = os.environ["SHEETY_USERS_ENDPOINT"]
        self.destination_data = {}
        self.customer_emails = {}

    def get_destination_data(self):
        response = requests.get(url=SHEETY_PRICES_ENDPOINT)
        data = response.json()
        print(data)
        self.destination_data = data["prices"]
        return self.destination_data

    def update_lowest_price(self,row_id,new_price):
        new_data = {
            "price":{
                "lowest_price":new_price
            }
        }
        requests.put(
            url=f"{SHEETY_PRICES_ENDPOINT}/{row_id}",
            json=new_data,
        )

    def get_customer_emails(self):
            response = requests.get(url=self.users_endpoint)
            data = response.json()
            self.customer_emails = data["users"]
            return self.customer_emails



