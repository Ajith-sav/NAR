from doctest import master
from logging import root
from tkinter import *
import tkinter.messagebox as box
from subprocess import *
from turtle import color, width
from PIL import ImageTk,Image
from matplotlib.pyplot import show
from numpy import imag

def dialog1():
    username=entry1.get()
    password = entry2.get()
    if (username == 'Ajith' and  password == 'Aji'):
         p = Popen(['python', 'Browser/main.py'])
         exit()
               
    else:
        box.showinfo('Error','Invalid Login')      

window = Tk()
window.title('NAR Password')
frame = Frame(window)

# Create an object of tkinter ImageTk
img = ImageTk.PhotoImage(Image.open("icon/NAR 3.png"))
Label3= Label(window, image = img, width= 280, height= 270)
Label3.pack(padx=40)

Label4 = Label(window, text="Wellcome to NAR", font=('Comic Sans MS',"25"), fg='blue')
Label4.pack() 

Label1 = Label(window,text = 'Username:', font=('Times','12'), fg='red')
Label1.pack(padx=15,pady= 5)

entry1 = Entry(window,bd =5)
entry1.pack(padx=15, pady=1)

Label2 = Label(window,text = 'Password:', font=('Times','12'), fg='red')
Label2.pack(padx = 15,pady=2)

entry2 = Entry(window, show='*', bd=5)
entry2.pack(padx = 15,pady=1)

def show_password():
    if entry2.cget('show') == '*':
        entry2.config(show='')
    else:
        entry2.config(show="*")   

check_button = Checkbutton(window, text='Show password', fg='#05ab29', command=show_password)
check_button.place(x= 125, y= 445)

btn = Button(frame, text = 'Login', fg='#0b03ff',command = dialog1)
btn.pack(side = RIGHT , padx =10)

frame.pack(padx=100,pady = 19)
window.mainloop()