#with open("weather_data.csv") as weather_data:
#    data= weather_data.readlines()
#    print(data)

#import csv

#with open("weather_data.csv") as weather_data:
#    data = csv.reader(weather_data)
#    temperature = []
#    for row in data:
#        if row[1] != "temp":
#            temperature.append(int(row[1]))

#    print(temperature)

import pandas

weather_data= pandas.read_csv("weather_data.csv")
#print(weather_data["temp"])

data_dict=weather_data.to_dict()
#print(data_dict)

temp_list = weather_data["temp"].to_list()
#print(temp_list)

average =sum(temp_list)/len(temp_list)
#print(average)

max_temp=weather_data["temp"].max()
#print(max_temp)

#Get data in columns
#print(weather_data["temp"])
#print(weather_data.temp)

#get data in rows

#print(weather_data[weather_data.day == "Monday"])

#print(weather_data[weather_data.temp==weather_data.temp.max()])

#monday = weather_data[weather_data.day == "Monday"]
#monday_tem =monday.temp[0]
#f= monday_tem*9/5+32
#print(f)

#create a dataframe from strach

#data_dict = {
#    "Students": ["Amy","James","Anglea"],
#    "Scores": [76,87,98]
#}

#data = pandas.DataFrame(data_dict)
#data.to_csv("new_data.csv")

data = pandas.read_csv("2018_Central_Park_Squirrel_Census_-_Squirrel_Data.csv")
grey_squirrels_count=len(data[data["Primary Fur Color"] == "Gray"])
red_squirrels_count=len(data[data["Primary Fur Color"] == "Cinnamon"])
black_squirrels_count=len(data[data["Primary Fur Color"] == "Black"])
print(grey_squirrels_count)
print(red_squirrels_count)
print(black_squirrels_count)

data_dict = {
    "Fur Color": ["Gray", "Cinnamon", "Black"],
    "Count": [grey_squirrels_count,red_squirrels_count,black_squirrels_count]
}
df=pandas.DataFrame(data_dict)
df.to_csv("squirrel_counts.csv")