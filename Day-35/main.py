import  requests


API_KEY = "24706cb9812a5f31f6c8aac77cdef468"
MY_LAT = 12.308440
MY_LONG = 76.653931





parameters = {
    "lat" : MY_LAT,
    "lon" : MY_LONG,
    "appid" : API_KEY,
    "cnt": 4,
}

response = requests.get(url="https://api.openweathermap.org/data/2.5/forecast",params=parameters)
response.raise_for_status()
weather_data= response.json()

#print(weather_data["list"][0]["weather"][0]["id"])

will_rain=False
for hour_data in weather_data["list"]:
    condition_code= hour_data["weather"][0]["id"]
    if int(condition_code) < 700:
        will_rain=True
if will_rain:
       print("It's going to rain today.Remember to bring an umbrella☔")
