from pip._internal import models


def add(*args):
    sum =0
    for arg in args:
        sum += arg
    return sum


#print(add(2,3,4,56,7))

def calculate(n,**kwargs):
    #print(kwargs)
    #for key,value in kwargs.items():
    #    print(key,value)
    n += kwargs["add"]
    n *= kwargs["multiply"]
    print(n)

calculate(2,add=3,multiply=4)


class Car:
    def __init__(self,**kw):
        self.make = kw.get("make")
        self.model = kw.get("model")


my_car = Car(make="Mercedes")
print(my_car.model)
print(my_car.make)


