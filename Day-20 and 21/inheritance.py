class Animal:
    def __init__(self):
        self.num_eyes = 2

    def breathe(self):
        print("Inhale","Exhale")

class Fish(Animal):
    def __init__(self):
        super().__init__()

    def swim(self):
        super().breathe()
        print("Moving in water")


stake_fish = Fish()
stake_fish.swim()