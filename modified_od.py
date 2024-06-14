import sqlite3
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import hashlib
from PIL import Image, ImageTk

border_color = "royal blue4"
border_width = 4

def connect_db():
    return sqlite3.connect('odm.db')

class DatabaseManager:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS users (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    username TEXT NOT NULL UNIQUE,
                                    password TEXT NOT NULL
                                );''')
            self.conn.execute('''CREATE TABLE IF NOT EXISTS odm (
                                    rollno INTEGER NOT NULL,
                                    student_name TEXT NOT NULL,
                                    date TEXT NOT NULL,
                                    reason TEXT,
                                    hours INTEGER DEFAULT 0
                                );''')

    def add_user(self, username, password):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        with self.conn:
            self.conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))

    def check_credentials(self, username, password):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        cursor = self.conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_password))
        return cursor.fetchone() is not None

    def add_update_on_duty(self, rollno, student_name, date, reason, hours):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM odm WHERE rollno = ? AND date = ?', (rollno, date))
        existing_record = cursor.fetchone()
        
        if existing_record:
            cursor.execute('UPDATE odm SET reason = ?, hours = ? WHERE rollno = ? and date=?',
                           (reason, hours, rollno, date))
            messagebox.showinfo("Success", f"Updated on duty hours for rollno {rollno} on {date}. Hours: {hours}.")
        else:
            cursor.execute('INSERT INTO odm (rollno, student_name, date, reason, hours) VALUES (?, ?, ?, ?, ?)',
                           (rollno, student_name, date, reason, hours))
            messagebox.showinfo("ADD RECORDS", f"Ready to add on duty record for rollno {rollno} on {date} with {hours} hours.")
        self.conn.commit()

    def view_on_duty(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM odm')
        return cursor.fetchall()

    def get_cumulative_hours(self, rollno):
        cursor = self.conn.cursor()
        cursor.execute('SELECT SUM(hours) FROM odm WHERE rollno = ?', (rollno,))
        result = cursor.fetchone()
        return result[0] if result[0] is not None else 0

    def delete_on_duty(self, rollno, date):
        with self.conn:
            self.conn.execute('DELETE FROM odm WHERE rollno = ? and date=?', (rollno, date))
            messagebox.showinfo("DELETE", "Are you sure to delete.")

class LoginSignupApp:
    def __init__(self, root, db_manager):
        self.root = root
        self.root.title("Login / Signup")
        self.db_manager = db_manager
        self.create_widgets()

    def create_widgets(self):
        self.tl=tk.Label(self.root,text="KONGU ENGINEERING COLLEGE",font=("Arial",20))
        self.tl.pack(pady=10)
        
        self.tit=tk.Label(self.root,text="OD MANAGEMENT",font=("Arial",15))
        self.tit.pack(pady=10)
        
        self.image = Image.open(r"C:\Users\sunda\OneDrive\Documents\kec.jpeg") 
        self.image = self.image.resize((1000, 400), Image.Resampling.LANCZOS)  
        self.photo = ImageTk.PhotoImage(self.image)

        self.image_label = tk.Label(self.root, image=self.photo, bg="white")
        self.image_label.pack(pady=10)

        self.login_button = tk.Button(self.root, text="Login", command=self.open_login_window, bg="limegreen", bd=3, highlightbackground="black", highlightcolor="black", highlightthickness=3)
        self.login_button.pack(pady=10)

        self.signup_button = tk.Button(self.root, text="Signup", command=self.open_signup_window, bg="red", bd=3, highlightbackground="black", highlightcolor="black", highlightthickness=3)
        self.signup_button.pack(pady=10)

    def open_login_window(self):
        login_window = tk.Toplevel(self.root)
        LoginWindow(login_window, self.db_manager, self.root)

    def open_signup_window(self):
        signup_window = tk.Toplevel(self.root)
        SignupWindow(signup_window, self.db_manager)

class LoginWindow:
    def __init__(self, root, db_manager, parent):
        self.root = root
        self.db_manager = db_manager
        self.parent = parent
        self.root.title("Login")
        self.create_widgets()

    def create_widgets(self):
        
        self.log=tk.Label(self.root,text="LOG IN",font=("Arial",10))
        self.log.pack(pady=5)
        self.image = Image.open(r"C:\Users\sunda\OneDrive\Documents\login-img.jpg") 
        self.image = self.image.resize((1000, 400), Image.Resampling.LANCZOS)  
        self.photo = ImageTk.PhotoImage(self.image)

        self.image_label = tk.Label(self.root, image=self.photo, bg="white")
        self.image_label.pack(pady=10)

        self.username_label = tk.Label(self.root, text="Username:",font=("Arial", 12), highlightbackground=border_color, highlightcolor=border_color, highlightthickness=border_width)
        self.username_label.pack(pady=10)

        self.username_entry = tk.Entry(self.root,bd=3, highlightbackground="black", highlightcolor="black", highlightthickness=2)
        self.username_entry.pack(pady=10)

        self.password_label = tk.Label(self.root, text="Password:",font=("Arial", 12), highlightbackground=border_color, highlightcolor=border_color, highlightthickness=border_width)
        self.password_label.pack(pady=10)

        self.password_entry = tk.Entry(self.root, show="*",bd=3, highlightbackground="black", highlightcolor="black", highlightthickness=2)
        self.password_entry.pack(pady=10)

        self.login_button = tk.Button(self.root, text="Login", command=self.login,bg="limegreen", bd=3, highlightbackground="black", highlightcolor="black", highlightthickness=3)
        self.login_button.pack(pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if self.db_manager.check_credentials(username, password):
            messagebox.showinfo("Login Successful", "Welcome!")
            self.root.destroy()
            self.parent.destroy()
            self.open_main_window()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def open_main_window(self):
        root = tk.Tk()
        root.title("OD MANAGEMENT SYSTEM")
        root.config(bg='aqua')
        app = OnDutyApp(root, self.db_manager)

class SignupWindow:
    def __init__(self, root, db_manager):
        self.root = root
        self.db_manager = db_manager
        self.root.title("Signup")
        self.create_widgets()

    def create_widgets(self):
        
        self.sig=tk.Label(self.root,text="SIGN UP",font=("Arial",10))
        self.sig.pack(pady=5)
        self.image = Image.open(r"C:\Users\sunda\OneDrive\Documents\signup.jpg")  
        self.image = self.image.resize((1000, 400), Image.Resampling.LANCZOS)  
        self.photo = ImageTk.PhotoImage(self.image)

        self.image_label = tk.Label(self.root, image=self.photo, bg="white")
        self.image_label.pack(pady=10)

        self.username_label = tk.Label(self.root, text="Username:",font=("Arial", 12), highlightbackground=border_color, highlightcolor=border_color, highlightthickness=border_width)
        self.username_label.pack(pady=10)

        self.username_entry = tk.Entry(self.root,bd=3, highlightbackground="black", highlightcolor="black", highlightthickness=2)
        self.username_entry.pack(pady=10)

        self.password_label = tk.Label(self.root, text="Password:",font=("Arial", 12), highlightbackground=border_color, highlightcolor=border_color, highlightthickness=border_width)
        self.password_label.pack(pady=10)

        self.password_entry = tk.Entry(self.root, show="*",bd=3, highlightbackground="black", highlightcolor="black", highlightthickness=2)
        self.password_entry.pack(pady=10)

        self.signup_button = tk.Button(self.root, text="Signup", command=self.signup,bg="limegreen", bd=3, highlightbackground="black", highlightcolor="black", highlightthickness=3)
        self.signup_button.pack(pady=10)

    def signup(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username and password:
            self.db_manager.add_user(username, password)
            messagebox.showinfo("Signup Successful", "Account created successfully!")
            self.root.destroy()
        else:
            messagebox.showerror("Signup Failed", "Please enter both username and password")

class OnDutyApp:
    def __init__(self, root, db_manager):
        self.conn = connect_db()
        self.db_manager = db_manager
        self.root = root
        self.root.title("On Duty Manager")
        self.create_widgets()
        self.populate_records()

    def create_widgets(self):
        self.frame = tk.Frame(self.root, bg='aqua')
        self.frame.pack(pady=20, padx=20)
        
        self.rollno_label = tk.Label(self.frame, text="Student RollNO:", font=("Arial", 12), highlightbackground=border_color, highlightcolor=border_color, highlightthickness=border_width)
        self.rollno_label.grid(row=0, column=0, padx=10, pady=10)
        self.rollno_entry = tk.Entry(self.frame, bd=3, highlightbackground="black", highlightcolor="black", highlightthickness=2)
        self.rollno_entry.grid(row=0, column=1, padx=10, pady=10)

        self.name_label = tk.Label(self.frame, text="Student Name:", font=("Arial", 12), highlightbackground=border_color, highlightcolor=border_color, highlightthickness=border_width)
        self.name_label.grid(row=1, column=0, padx=10, pady=10)
        self.name_entry = tk.Entry(self.frame, bd=3, highlightbackground="black", highlightcolor="black", highlightthickness=2)
        self.name_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(self.frame, text="Date (YYYY-MM-DD):", font=("Arial", 12), highlightbackground=border_color, highlightcolor=border_color, highlightthickness=border_width).grid(row=2, column=0, padx=10, pady=10)
        self.date_entry = tk.Entry(self.frame, bd=3, highlightbackground="black", highlightcolor="black", highlightthickness=2)
        self.date_entry.grid(row=2, column=1, padx=10, pady=10)

        tk.Label(self.frame, text="Reason:", font=("Arial", 12), highlightbackground=border_color, highlightcolor=border_color, highlightthickness=border_width).grid(row=3, column=0, padx=10, pady=10)
        self.reason_entry = tk.Entry(self.frame, bd=3, highlightbackground="black", highlightcolor="black", highlightthickness=2)
        self.reason_entry.grid(row=3, column=1, padx=10, pady=10)

        tk.Label(self.frame, text="Hours:", font=("Arial", 12), highlightbackground=border_color, highlightcolor=border_color, highlightthickness=border_width).grid(row=4, column=0, padx=10, pady=10)
        self.hours_entry = tk.Entry(self.frame, bd=3, highlightbackground="black", highlightcolor="black", highlightthickness=2)
        self.hours_entry.grid(row=4, column=1, padx=10, pady=10)

        tk.Button(self.frame, text="Add/Update On Duty", font=("Arial", 12), command=self.add_record, bg="lime green", bd=3, highlightbackground="black", highlightcolor="black", highlightthickness=3).grid(row=5, column=0, columnspan=1, pady=10)

        tk.Button(self.frame, text="Reset", font=("Arial", 12), command=self.reset_fields, bg="orange", bd=3, highlightbackground="black", highlightcolor="black", highlightthickness=3).grid(row=5, column=1, columnspan=1, pady=10)
        
        self.tree = ttk.Treeview(self.frame, columns=("rollno", "Name", "Date", "Reason", "Hours"), show='headings')
        self.tree.heading("rollno", text="ROLLNO")
        self.tree.heading("Name", text="STUDENT NAME")
        self.tree.heading("Date", text="DATE")
        self.tree.heading("Reason", text="REASON")
        self.tree.heading("Hours", text="HOURS")
        self.tree.grid(row=2, column=2, pady=10)

        tk.Button(self.frame, text="Delete Selected", command=self.delete_record, bg="red", bd=3, highlightbackground="black", highlightcolor="black", highlightthickness=3).grid(row=5, column=2, columnspan=1, pady=10)

        tk.Label(self.frame, text="Query RollNo:", font=("Arial", 12), highlightbackground=border_color, highlightcolor=border_color, highlightthickness=border_width).grid(row=6, column=0, padx=10, pady=10)
        self.query_rollno_entry = tk.Entry(self.frame, bd=3, highlightbackground="black", highlightcolor="black", highlightthickness=2)
        self.query_rollno_entry.grid(row=6, column=1, padx=10, pady=10)

        tk.Button(self.frame, text="Get Cumulative Hours", command=self.get_cumulative_hours, font=("Arial", 12), bg="coral", bd=3, highlightbackground="black", highlightcolor="black", highlightthickness=3).grid(row=7, column=0, columnspan=2, pady=10)

    def populate_records(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for row in self.db_manager.view_on_duty():
            self.tree.insert("", "end", values=row)

    def add_record(self):
        rollno = self.rollno_entry.get()
        student_name = self.name_entry.get()
        date = self.date_entry.get()
        reason = self.reason_entry.get()
        hours = self.hours_entry.get()

        if rollno and date and hours.isdigit():
            self.db_manager.add_update_on_duty(rollno, student_name, date, reason, int(hours))
            self.populate_records()
            self.reset_fields()
        else:
            messagebox.showwarning("Input Error", "Please fill in all required fields correctly.")

    def delete_record(self):
        selected_item = self.tree.selection()
        if selected_item:
            record_id = self.tree.item(selected_item)["values"][0]
            date = self.tree.item(selected_item)["values"][2]
            self.db_manager.delete_on_duty(record_id, date)
            self.populate_records()
        else:
            messagebox.showwarning("Selection Error", "Please select a record to delete.")

    def get_cumulative_hours(self):
        roll = self.query_rollno_entry.get()
        if roll:
            total_hours = self.db_manager.get_cumulative_hours(roll)
            messagebox.showinfo("Cumulative Hours", f"Total hours of on duty for rollno {roll}: {total_hours}")
        else:
            messagebox.showwarning("Input Error", "Please enter a student roll number.")

    def reset_fields(self):
        self.name_entry.delete(0, tk.END)
        self.rollno_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.reason_entry.delete(0, tk.END)
        self.hours_entry.delete(0, tk.END)
        self.query_rollno_entry.delete(0, tk.END)

def main():
    db_manager = DatabaseManager('odm.db')
    root = tk.Tk()
    app = LoginSignupApp(root, db_manager)
    root.mainloop()

if __name__ == "__main__":
    main()
