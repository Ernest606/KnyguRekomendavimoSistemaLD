import pandas as pd
from tkinter import *
import subprocess

# Designing window for registration


def register():
    global register_screen
    register_screen = Toplevel(main_screen)
    register_screen.title("Register")
    register_screen.geometry("300x250")

    global username
    global password
    global username_entry
    global password_entry
    username = StringVar()
    password = StringVar()

    Label(register_screen, text="Please enter details below", bg="blue").pack()
    Label(register_screen, text="").pack()
    username_lable = Label(register_screen, text="Username * ")
    username_lable.pack()
    username_entry = Entry(register_screen, textvariable=username)
    username_entry.pack()
    password_lable = Label(register_screen, text="Password * ")
    password_lable.pack()
    password_entry = Entry(register_screen, textvariable=password, show='*')
    password_entry.pack()
    Label(register_screen, text="").pack()
    Button(register_screen, text="Register", width=10,
           height=1, bg="blue", command=register_user).pack()


# Designing window for login

def login():
    global login_screen
    login_screen = Toplevel(main_screen)
    login_screen.title("Login")
    login_screen.geometry("300x250")
    Label(login_screen, text="Please enter details below to login").pack()
    Label(login_screen, text="").pack()

    global username_verify
    global password_verify

    username_verify = StringVar()
    password_verify = StringVar()

    global username_login_entry
    global password_login_entry

    Label(login_screen, text="Username * ").pack()
    username_login_entry = Entry(login_screen, textvariable=username_verify)
    username_login_entry.pack()
    Label(login_screen, text="").pack()
    Label(login_screen, text="Password * ").pack()
    password_login_entry = Entry(
        login_screen, textvariable=password_verify, show='*')
    password_login_entry.pack()
    Label(login_screen, text="").pack()
    Button(login_screen, text="Login", width=10,
           height=1, command=login_verify).pack()

# Implementing event on register button


def register_user():

    username_info = username.get()
    password_info = password.get()

    usersDB = pd.read_csv('DataBase/Users.csv', sep=',')
    ratingsDB = pd.read_csv('DataBase/ratings.csv', sep=',')
    if not username_info:
        Label(register_screen, text="Username entry is empty",
              fg="red", font=("calibri", 11)).pack()
    elif not password_info:
        Label(register_screen, text="Password entry is empty",
              fg="red", font=("calibri", 11)).pack()
    elif username_info not in str(usersDB['Username']):
        newUserID = int(ratingsDB["user_id"].max())+1
        del usersDB
        data = {
            'UserID': [newUserID],
            'Username': [username_info],
            'Password': [password_info]
        }
        df = pd.DataFrame(data)
        df.to_csv('DataBase/Users.csv', mode='a',
                  index=False, header=False, sep=',')
        delete_registration_screen()
        Label(main_screen, text="Registration Success",
              fg="green", font=("calibri", 11)).pack()
    else:
        Label(register_screen, text="User already exists",
              fg="red", font=("calibri", 11)).pack()

# Implementing event on login button


def login_verify():
    username1 = username_verify.get()
    password1 = password_verify.get()
    username_login_entry.delete(0, END)
    password_login_entry.delete(0, END)

    usersDB = pd.read_csv('DataBase/Users.csv', sep=',')
    if not username1:
        Label(login_screen, text="Username entry is empty",
              fg="red", font=("calibri", 11)).pack()
    elif not password1:
        Label(login_screen, text="Password entry is empty",
              fg="red", font=("calibri", 11)).pack()
    elif username1 in str(usersDB['Username']):
        if password1 == usersDB.loc[usersDB['Username'] == username1]['Password'].item():
            delete_login_screen()
            delete_main_app_screen()
            userID = str(usersDB.loc[usersDB['Username']
                         == username1]['UserID'].item())
            subprocess.run(['python', 'userProfile.py', userID], text=FALSE)
        else:
            Label(login_screen, text="Password not recognized",
                  fg="red", font=("calibri", 11)).pack()
    else:
        Label(login_screen, text="User not found",
              fg="red", font=("calibri", 11)).pack()
    del usersDB


# Deleting popups

def delete_login_screen():
    login_screen.destroy()


def delete_registration_screen():
    register_screen.destroy()


def delete_main_app_screen():
    main_screen.destroy()

# Designing Main(first) window


def main_app_screen():
    global main_screen
    main_screen = Tk()
    main_screen.geometry("300x250")
    main_screen.title("Account Login")
    Label(text="Select Your Choice", bg="blue", width="300",
          height="2", font=("Calibri", 13)).pack()
    Label(text="").pack()
    Button(text="Login", height="2", width="30", command=login).pack()
    Label(text="").pack()
    Button(text="Register", height="2", width="30", command=register).pack()

    main_screen.mainloop()


main_app_screen()
