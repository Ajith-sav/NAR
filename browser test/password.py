from tkinter import *
import tkinter.messagebox as box
from subprocess import *
from matplotlib.pyplot import show

def dialog1():
    username=entry1.get()
    password = entry2.get()
    if (username == 'Ajith' and  password == 'Aji'):
         p = Popen(['python', 'Browser/test.py'])
         exit()
         
    else:
        box.showinfo('info','Invalid Login')
# Run python file        
#def open():
    #p = Popen('test.py', shell=True)
    # or
    #p = Popen(['python', 'test.py'])
    #print('Enter')        

window = Tk()
window.title('Password')
frame = Frame(window)

Label1 = Label(window,text = 'Username:')
Label1.pack(padx=15,pady= 5)

entry1 = Entry(window,bd =5)
entry1.pack(padx=15, pady=5)

Label2 = Label(window,text = 'Password:')
Label2.pack(padx = 15,pady=6)

entry2 = Entry(window, show='*', bd=5)
entry2.pack(padx = 15,pady=7)

def show_password():
    if entry2.cget('show') == '*':
        entry2.config(show='')
    else:
        entry2.config(show="*")   

check_button = Checkbutton(window, text='Show password', command=show_password)
check_button.place(x= 70, y= 135)

btn = Button(frame, text = 'Login',command = dialog1)
btn.pack(side = RIGHT , padx =5)

frame.pack(padx=100,pady = 19)
window.mainloop()