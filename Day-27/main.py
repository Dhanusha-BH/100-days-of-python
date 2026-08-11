from  tkinter import *
from idlelib import window

def button_clicked():
    new_word = input.get()
    my_label["text"] = new_word


window = Tk()
window.title("My First GUI program")
window.minsize(width =500,height= 300)
window.config(padx = 100, pady = 200)

#label
my_label= Label(text = "I am a Label",font = ("Arial",25,"bold"))
my_label["text"] = "New text"
my_label.grid(column = 0,row = 0)
my_label.config(padx = 50, pady = 50)

#button
button =Button(text="Click Me",command=button_clicked)
button.grid(column = 1,row = 1)


#new button
second_Button = Button(text="Click Me")
second_Button.grid(column = 2,row = 0)



#Entry
input = Entry(width=10)
input.grid(column = 3,row = 2)



















window.mainloop()