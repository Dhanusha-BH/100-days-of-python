import  requests
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()


GENDER = "female"
WEIGHT_KG = 54
AGE = 21

APP_ID = os.environ["APP_ID"]
API_KEY =  os.environ["API_KEY"]




exercise_endpoint = "https://app.100daysofpython.dev/v1/nutrition/natural/exercise"
sheet_endpoint = "https://api.sheety.co/0d5209dae71bae72742e1bb8ec0c6300/myWorkoutSpreadSheet/workouts"

exercise_text = input("Tell me which exercises you did: ")

headers = {
    "x-app-id": APP_ID,
    "x-app-key": API_KEY,

}

data_parameters = {
    "query": exercise_text,
    "gender": GENDER,
    "weight": WEIGHT_KG,
    "age": AGE,

}
print(headers)
reponse = requests.post(url=exercise_endpoint, json=data_parameters, headers=headers)
result = reponse.json()

print(result)


today_date = datetime.now().strftime("%d/%m/%Y")
now_time = datetime.now().strftime("%X")

for exercise in result["exercises"]:
    sheet_inputs = {
        "workout": {
            "date": today_date,
            "time": now_time,
            "exercise": exercise["name"].title(),
            "duration": exercise["duration_min"],
            "calories": exercise["nf_calories"]
        }
    }

    sheet_response = requests.post(
        sheet_endpoint,
        json=sheet_inputs,

    )



    print(sheet_response.text)






