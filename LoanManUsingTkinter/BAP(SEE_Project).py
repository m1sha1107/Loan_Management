import sqlite3
from tkinter import *
from tkinter import messagebox, ttk

# Database setup
def create_tables():
    conn = sqlite3.connect('loan_management1.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL)''')

    c.execute('''CREATE TABLE IF NOT EXISTS borrowers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    firstname TEXT NOT NULL,
                    lastname TEXT NOT NULL,
                    middlename TEXT,
                    contact_no TEXT NOT NULL,
                    address TEXT NOT NULL)''')

    c.execute('''CREATE TABLE IF NOT EXISTS loan_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type_name TEXT NOT NULL,
                    description TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS loan_plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    months INTEGER NOT NULL,
                    interest_percentage REAL NOT NULL,
                    penalty_rate REAL NOT NULL)''')

    c.execute('''CREATE TABLE IF NOT EXISTS loans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    borrower_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    plan_id INTEGER NOT NULL,
                    status INTEGER NOT NULL,
                    FOREIGN KEY(borrower_id) REFERENCES borrowers(id),
                    FOREIGN KEY(plan_id) REFERENCES loan_plans(id))''')

    c.execute('''CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    loan_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    penalty_amount REAL NOT NULL,
                    date_created TEXT NOT NULL,
                    FOREIGN KEY(loan_id) REFERENCES loans(id))''')

    # Add a default admin user if not exists
    c.execute('''INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)''', ('admin', 'admin'))

    conn.commit()
    conn.close()

# Create tables on first run
create_tables()

# Main application class
class LoanManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Loan Management System")
        self.root.geometry("800x600")

        self.current_frame = None
        self.create_login_frame()

    def switch_frame(self, new_frame):
        if self.current_frame:
            self.current_frame.pack_forget()
        self.current_frame = new_frame
        self.current_frame.pack(fill="both", expand=True)

    def create_login_frame(self):
        self.login_frame = Frame(self.root)
        self.switch_frame(self.login_frame)

        Label(self.login_frame, text="Username").grid(row=0, column=0, padx=10, pady=10)
        self.username_entry = Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)

        Label(self.login_frame, text="Password").grid(row=1, column=0, padx=10, pady=10)
        self.password_entry = Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        Button(self.login_frame, text="Login", command=self.login, bg="light green").grid(row=2, column=0, columnspan=2, pady=10)
        Button(self.login_frame, text="Register", command=self.create_register_frame, bg="light green").grid(row=3, column=0, columnspan=2, pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        conn = sqlite3.connect('loan_management1.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            self.create_dashboard_frame()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def create_dashboard_frame(self):
        self.dashboard_frame = Frame(self.root)
        self.switch_frame(self.dashboard_frame)

        Button(self.dashboard_frame, text="Manage Loan Types", command=self.create_loan_type_frame, bg="light green").pack(pady=10)
        Button(self.dashboard_frame, text="Manage Borrowers", command=self.create_borrower_frame, bg="light green").pack(pady=10)
        Button(self.dashboard_frame, text="Manage Loans", command=self.create_loan_frame, bg="light green").pack(pady=10)
        Button(self.dashboard_frame, text="Manage Payments", command=self.create_payment_frame, bg="light green").pack(pady=10)
        Button(self.dashboard_frame, text="Manage Users", command=self.create_user_frame, bg="light green").pack(pady=10)

    def create_loan_type_frame(self):
        self.loan_type_frame = Frame(self.root)
        self.switch_frame(self.loan_type_frame)
    
        self.loan_type_name_label = Label(self.loan_type_frame, text="Loan Type Name")
        self.loan_type_name_label.pack(pady=10)
        self.loan_type_name_entry = Entry(self.loan_type_frame)
        self.loan_type_name_entry.pack(pady=10)
    
        self.loan_type_description_label = Label(self.loan_type_frame, text="Loan Type Description")
        self.loan_type_description_label.pack(pady=10)
        self.loan_type_description_entry = Entry(self.loan_type_frame)
        self.loan_type_description_entry.pack(pady=10)
    
        Button(self.loan_type_frame, text="Save Loan Type", command=self.save_loan_type, bg="light green").pack(pady=10)
        Button(self.loan_type_frame, text="Delete", command=self.delete_loan_type, bg="light green").pack(pady=10)
        Button(self.loan_type_frame, text="Edit", command=self.edit_loan_type, bg="light green").pack(pady=10)
        Button(self.loan_type_frame, text="Back to Home", command=self.create_dashboard_frame, bg="light green").pack(pady=10)
    
        self.loan_type_tree = ttk.Treeview(self.loan_type_frame, columns=("ID", "Type", "Description"), show="headings")
        self.loan_type_tree.heading("ID", text="ID")
        self.loan_type_tree.heading("Type", text="Type")
        self.loan_type_tree.heading("Description", text="Description")
        self.loan_type_tree.pack(fill="both", expand=True)


    def save_loan_type(self):
        type_name = self.loan_type_name_entry.get()
        description = self.loan_type_description_entry.get()

        conn = sqlite3.connect('loan_management1.db')
        c = conn.cursor()
        c.execute('INSERT INTO loan_types (type_name, description) VALUES (?, ?)', (type_name, description))
        conn.commit()
        conn.close()

        self.loan_type_name_entry.delete(0, END)
        self.loan_type_description_entry.delete(0, END)

        self.load_loan_types()

    def delete_loan_type(self):
        selected_item = self.loan_type_tree.selection()
        if selected_item:
            loan_type_id = self.loan_type_tree.item(selected_item, 'values')[0]
            conn = sqlite3.connect('loan_management1.db')
            c = conn.cursor()
            c.execute('DELETE FROM loan_types WHERE id = ?', (loan_type_id,))
            conn.commit()
            conn.close()
            self.load_loan_types()
        else:
            messagebox.showwarning("Selection Required", "Please select a loan type to delete.")

    def load_loan_types(self):
        for row in self.loan_type_tree.get_children():
            self.loan_type_tree.delete(row)

        conn = sqlite3.connect('loan_management1.db')
        c = conn.cursor()
        c.execute('SELECT * FROM loan_types')
        rows = c.fetchall()
        conn.close()

        for row in rows:
            self.loan_type_tree.insert('', 'end', values=row)

    def create_borrower_frame(self):
        self.borrower_frame = Frame(self.root)
        self.switch_frame(self.borrower_frame)
    
        self.borrower_firstname_label = Label(self.borrower_frame, text="First Name")
        self.borrower_firstname_label.pack(pady=10)
        self.borrower_firstname_entry = Entry(self.borrower_frame)
        self.borrower_firstname_entry.pack(pady=10)
    
        self.borrower_lastname_label = Label(self.borrower_frame, text="Last Name")
        self.borrower_lastname_label.pack(pady=10)
        self.borrower_lastname_entry = Entry(self.borrower_frame)
        self.borrower_lastname_entry.pack(pady=10)
    
        self.borrower_middlename_label = Label(self.borrower_frame, text="Middle Name")
        self.borrower_middlename_label.pack(pady=10)
        self.borrower_middlename_entry = Entry(self.borrower_frame)
        self.borrower_middlename_entry.pack(pady=10)
    
        self.borrower_contact_no_label = Label(self.borrower_frame, text="Contact No")
        self.borrower_contact_no_label.pack(pady=10)
        self.borrower_contact_no_entry = Entry(self.borrower_frame)
        self.borrower_contact_no_entry.pack(pady=10)
    
        self.borrower_address_label = Label(self.borrower_frame, text="Address")
        self.borrower_address_label.pack(pady=10)
        self.borrower_address_entry = Entry(self.borrower_frame)
        self.borrower_address_entry.pack(pady=10)
    
        Button(self.borrower_frame, text="Save Borrower", command=self.save_borrower, bg="light green").pack(pady=10)
        Button(self.borrower_frame, text="Delete", command=self.delete_borrower, bg="light green").pack(pady=10)
        Button(self.borrower_frame, text="Edit", command=self.edit_borrower, bg="light green").pack(pady=10)
        Button(self.borrower_frame, text="Back to Home", command=self.create_dashboard_frame, bg="light green").pack(pady=10)
    
        self.borrower_tree = ttk.Treeview(self.borrower_frame, columns=("ID", "First Name", "Last Name", "Middle Name", "Contact No", "Address"), show="headings")
        self.borrower_tree.heading("ID", text="ID")
        self.borrower_tree.heading("First Name", text="First Name")
        self.borrower_tree.heading("Last Name", text="Last Name")
        self.borrower_tree.heading("Middle Name", text="Middle Name")
        self.borrower_tree.heading("Contact No", text="Contact No")
        self.borrower_tree.heading("Address", text="Address")
        self.borrower_tree.pack(fill="both", expand=True)
    
        self.load_borrowers()


    def save_borrower(self):
        firstname = self.borrower_firstname_entry.get()
        lastname = self.borrower_lastname_entry.get()
        middlename = self.borrower_middlename_entry.get()
        contact_no = self.borrower_contact_no_entry.get()
        address = self.borrower_address_entry.get()

        conn = sqlite3.connect('loan_management1.db')
        c = conn.cursor()
        c.execute('INSERT INTO borrowers (firstname, lastname, middlename, contact_no, address) VALUES (?, ?, ?, ?, ?)', (firstname, lastname, middlename, contact_no, address))
        conn.commit()
        conn.close()

        self.borrower_firstname_entry.delete(0, END)
        self.borrower_lastname_entry.delete(0, END)
        self.borrower_middlename_entry.delete(0, END)
        self.borrower_contact_no_entry.delete(0, END)
        self.borrower_address_entry.delete(0, END)

        self.load_borrowers()

    def delete_borrower(self):
        selected_item = self.borrower_tree.selection()
        if selected_item:
            borrower_id = self.borrower_tree.item(selected_item, 'values')[0]
            conn = sqlite3.connect('loan_management1.db')
            c = conn.cursor()
            c.execute('DELETE FROM borrowers WHERE id = ?', (borrower_id,))
            conn.commit()
            conn.close()
            self.load_borrowers()
        else:
            messagebox.showwarning("Selection Required", "Please select a borrower to delete.")

    def load_borrowers(self):
        for row in self.borrower_tree.get_children():
            self.borrower_tree.delete(row)

        conn = sqlite3.connect('loan_management1.db')
        c = conn.cursor()
        c.execute('SELECT * FROM borrowers')
        rows = c.fetchall()
        conn.close()

        for row in rows:
            self.borrower_tree.insert('', 'end', values=row)

    def create_loan_frame(self):
        self.loan_frame = Frame(self.root)
        self.switch_frame(self.loan_frame)
    
        self.loan_borrower_id_label = Label(self.loan_frame, text="Borrower ID")
        self.loan_borrower_id_label.pack(pady=10)
        self.loan_borrower_id_entry = Entry(self.loan_frame)
        self.loan_borrower_id_entry.pack(pady=10)
    
        self.loan_amount_label = Label(self.loan_frame, text="Amount")
        self.loan_amount_label.pack(pady=10)
        self.loan_amount_entry = Entry(self.loan_frame)
        self.loan_amount_entry.pack(pady=10)
    
        self.loan_plan_id_label = Label(self.loan_frame, text="Plan ID")
        self.loan_plan_id_label.pack(pady=10)
        self.loan_plan_id_entry = Entry(self.loan_frame)
        self.loan_plan_id_entry.pack(pady=10)
    
        self.loan_status_label = Label(self.loan_frame, text="Status")
        self.loan_status_label.pack(pady=10)
        self.loan_status_entry = Entry(self.loan_frame)
        self.loan_status_entry.pack(pady=10)
    
        Button(self.loan_frame, text="Save Loan", command=self.save_loan, bg="light green").pack(pady=10)
        Button(self.loan_frame, text="Delete", command=self.delete_loan, bg="light green").pack(pady=10)
        Button(self.loan_frame, text="Edit", command=self.edit_loan, bg="light green").pack(pady=10)
        Button(self.loan_frame, text="Back to Home", command=self.create_dashboard_frame, bg="light green").pack(pady=10)

        self.loan_tree = ttk.Treeview(self.loan_frame, columns=("ID", "Borrower ID", "Amount", "Plan ID", "Status"), show="headings")
        self.loan_tree.heading("ID", text="ID")
        self.loan_tree.heading("Borrower ID", text="Borrower ID")
        self.loan_tree.heading("Amount", text="Amount")
        self.loan_tree.heading("Plan ID", text="Plan ID")
        self.loan_tree.heading("Status", text="Status")
        self.loan_tree.pack(fill="both", expand=True)
    
        self.load_loans()


    def save_loan(self):
        borrower_id = self.loan_borrower_id_entry.get()
        amount = self.loan_amount_entry.get()
        plan_id = self.loan_plan_id_entry.get()
        status = self.loan_status_entry.get()

        conn = sqlite3.connect('loan_management1.db')
        c = conn.cursor()
        c.execute('INSERT INTO loans (borrower_id, amount, plan_id, status) VALUES (?, ?, ?, ?)', (borrower_id, amount, plan_id, status))
        conn.commit()
        conn.close()

        self.loan_borrower_id_entry.delete(0, END)
        self.loan_amount_entry.delete(0, END)
        self.loan_plan_id_entry.delete(0, END)
        self.loan_status_entry.delete(0, END)

        self.load_loans()

    def delete_loan(self):
        selected_item = self.loan_tree.selection()
        if selected_item:
            loan_id = self.loan_tree.item(selected_item, 'values')[0]
            conn = sqlite3.connect('loan_management1.db')
            c = conn.cursor()
            c.execute('DELETE FROM loans WHERE id = ?', (loan_id,))
            conn.commit()
            conn.close()
            self.load_loans()
        else:
            messagebox.showwarning("Selection Required", "Please select a loan to delete.")

    def load_loans(self):
        for row in self.loan_tree.get_children():
            self.loan_tree.delete(row)

        conn = sqlite3.connect('loan_management1.db')
        c = conn.cursor()
        c.execute('SELECT * FROM loans')
        rows = c.fetchall()
        conn.close()

        for row in rows:
            self.loan_tree.insert('', 'end', values=row)

    def create_payment_frame(self):
        self.payment_frame = Frame(self.root)
        self.switch_frame(self.payment_frame)
    
        self.payment_loan_id_label = Label(self.payment_frame, text="Loan ID")
        self.payment_loan_id_label.pack(pady=10)
        self.payment_loan_id_entry = Entry(self.payment_frame)
        self.payment_loan_id_entry.pack(pady=10)
    
        self.payment_amount_label = Label(self.payment_frame, text="Amount")
        self.payment_amount_label.pack(pady=10)
        self.payment_amount_entry = Entry(self.payment_frame)
        self.payment_amount_entry.pack(pady=10)
    
        self.payment_penalty_amount_label = Label(self.payment_frame, text="Penalty Amount")
        self.payment_penalty_amount_label.pack(pady=10)
        self.payment_penalty_amount_entry = Entry(self.payment_frame)
        self.payment_penalty_amount_entry.pack(pady=10)
    
        self.payment_date_created_label = Label(self.payment_frame, text="Date Created")
        self.payment_date_created_label.pack(pady=10)
        self.payment_date_created_entry = Entry(self.payment_frame)
        self.payment_date_created_entry.pack(pady=10)
    
        Button(self.payment_frame, text="Save Payment", command=self.save_payment, bg="light green").pack(pady=10)
        Button(self.payment_frame, text="Delete", command=self.delete_payment, bg="light green").pack(pady=10)
        Button(self.payment_frame, text="Edit", command=self.edit_payment, bg="light green").pack(pady=10)
        Button(self.payment_frame, text="Back to Home", command=self.create_dashboard_frame, bg="light green").pack(pady=10)
    
        self.payment_tree = ttk.Treeview(self.payment_frame, columns=("ID", "Loan ID", "Amount", "Penalty Amount", "Date Created"), show="headings")
        self.payment_tree.heading("ID", text="ID")
        self.payment_tree.heading("Loan ID", text="Loan ID")
        self.payment_tree.heading("Amount", text="Amount")
        self.payment_tree.heading("Penalty Amount", text="Penalty Amount")
        self.payment_tree.heading("Date Created", text="Date Created")
        self.payment_tree.pack(fill="both", expand=True)
    
        self.load_payments()


    def save_payment(self):
        loan_id = self.payment_loan_id_entry.get()
        amount = self.payment_amount_entry.get()
        penalty_amount = self.payment_penalty_amount_entry.get()
        date_created = self.payment_date_created_entry.get()

        conn = sqlite3.connect('loan_management1.db')
        c = conn.cursor()
        c.execute('INSERT INTO payments (loan_id, amount, penalty_amount, date_created) VALUES (?, ?, ?, ?)', (loan_id, amount, penalty_amount, date_created))
        conn.commit()
        conn.close()

        self.payment_loan_id_entry.delete(0, END)
        self.payment_amount_entry.delete(0, END)
        self.payment_penalty_amount_entry.delete(0, END)
        self.payment_date_created_entry.delete(0, END)

        self.load_payments()

    def delete_payment(self):
        selected_item = self.payment_tree.selection()
        if selected_item:
            payment_id = self.payment_tree.item(selected_item, 'values')[0]
            conn = sqlite3.connect('loan_management1.db')
            c = conn.cursor()
            c.execute('DELETE FROM payments WHERE id = ?', (payment_id,))
            conn.commit()
            conn.close()
            self.load_payments()
        else:
            messagebox.showwarning("Selection Required", "Please select a payment to delete.")

    def load_payments(self):
        for row in self.payment_tree.get_children():
            self.payment_tree.delete(row)

        conn = sqlite3.connect('loan_management1.db')
        c = conn.cursor()
        c.execute('SELECT * FROM payments')
        rows = c.fetchall()
        conn.close()

        for row in rows:
            self.payment_tree.insert('', 'end', values=row)

    def create_user_frame(self):
        self.user_frame = Frame(self.root)
        self.switch_frame(self.user_frame)
    
        self.user_username_label = Label(self.user_frame, text="Username")
        self.user_username_label.pack(pady=10)
        self.user_username_entry = Entry(self.user_frame)
        self.user_username_entry.pack(pady=10)
    
        self.user_password_label = Label(self.user_frame, text="Password")
        self.user_password_label.pack(pady=10)
        self.user_password_entry = Entry(self.user_frame, show="*")
        self.user_password_entry.pack(pady=10)
    
        Button(self.user_frame, text="Save User", command=self.save_user, bg="light green").pack(pady=10)
        Button(self.user_frame, text="Delete", command=self.delete_user, bg="light green").pack(pady=10)
        Button(self.user_frame, text="Edit", command=self.edit_user, bg="light green").pack(pady=10)
        Button(self.user_frame, text="Back to Home", command=self.create_dashboard_frame, bg="light green").pack(pady=10)
    
        self.user_tree = ttk.Treeview(self.user_frame, columns=("ID", "Username"), show="headings")
        self.user_tree.heading("ID", text="ID")
        self.user_tree.heading("Username", text="Username")
        self.user_tree.pack(fill="both", expand=True)
        self.load_users()


    def save_user(self):
        username = self.user_username_entry.get()
        password = self.user_password_entry.get()

        conn = sqlite3.connect('loan_management1.db')
        c = conn.cursor()
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()

        self.user_username_entry.delete(0, END)
        self.user_password_entry.delete(0, END)

        self.load_users()

    def delete_user(self):
        selected_item = self.user_tree.selection()
        if selected_item:
            user_id = self.user_tree.item(selected_item, 'values')[0]
            conn = sqlite3.connect('loan_management1.db')
            c = conn.cursor()
            c.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            conn.close()
            self.load_users()
        else:
            messagebox.showwarning("Selection Required", "Please select a user to delete.")

    def load_users(self):
        for row in self.user_tree.get_children():
            self.user_tree.delete(row)

        conn = sqlite3.connect('loan_management1.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users')
        rows = c.fetchall()
        conn.close()

        for row in rows:
            self.user_tree.insert('', 'end', values=row)

    def create_register_frame(self):
        self.register_frame = Frame(self.root)
        self.switch_frame(self.register_frame)

        Label(self.register_frame, text="Username").grid(row=0, column=0, padx=10, pady=10)
        self.reg_username_entry = Entry(self.register_frame)
        self.reg_username_entry.grid(row=0, column=1, padx=10, pady=10)

        Label(self.register_frame, text="Password").grid(row=1, column=0, padx=10, pady=10)
        self.reg_password_entry = Entry(self.register_frame, show="*")
        self.reg_password_entry.grid(row=1, column=1, padx=10, pady=10)

        Button(self.register_frame, text="Register", command=self.register, bg="light green").grid(row=2, column=0, columnspan=2, pady=10)
        Button(self.register_frame, text="Back to Login", command=self.create_login_frame, bg="light green").grid(row=3, column=0, columnspan=2, pady=10)

    def register(self):
        username = self.reg_username_entry.get()
        password = self.reg_password_entry.get()

        conn = sqlite3.connect('loan_management1.db')
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            messagebox.showinfo("Registration Success", "User registered successfully")
            self.create_login_frame()
        except sqlite3.IntegrityError:
            messagebox.showerror("Registration Failed", "Username already exists")
        finally:
            conn.close()

    
    def edit_loan_type(self):
    # Get the selected item from the Treeview
        selected_item = self.loan_type_tree.selection()
        if selected_item:
            # Extract loan type details
            loan_type_id = self.loan_type_tree.item(selected_item, 'values')[0]
            loan_type_name = self.loan_type_tree.item(selected_item, 'values')[1]
            loan_type_description = self.loan_type_tree.item(selected_item, 'values')[2]
    
            # Create a new window for editing
            edit_window = Toplevel(self.root)
            edit_window.title("Edit Loan Type")
    
            # Create entry fields with existing details pre-filled
            Label(edit_window, text="Type Name").pack()
            type_name_entry = Entry(edit_window)
            type_name_entry.insert(0, loan_type_name)
            type_name_entry.pack()

            Label(edit_window, text="Description").pack()
            description_entry = Entry(edit_window)
            description_entry.insert(0, loan_type_description)
            description_entry.pack()
    
            # Define an update function to save changes
            def update_loan_type():
                new_type_name = type_name_entry.get()
                new_description = description_entry.get()
    
                # Update database
                conn = sqlite3.connect('loan_management1.db')
                c = conn.cursor()
                c.execute('UPDATE loan_types SET type_name=?, description=? WHERE id=?',
                          (new_type_name, new_description, loan_type_id))
                conn.commit()
                conn.close()
    
                # Reload loan types
                self.load_loan_types()
    
                # Close edit window
                edit_window.destroy()
    
            # Add a button to save changes
            Button(edit_window, text="Update", command=update_loan_type).pack()
        else:
            messagebox.showwarning("Selection Required", "Please select a loan type to edit.")

    def edit_borrower(self):
        selected_item = self.borrower_tree.selection()
        if selected_item:
            borrower_id = self.borrower_tree.item(selected_item, 'values')[0]
            conn = sqlite3.connect('loan_management1.db')
            c = conn.cursor()
            c.execute('SELECT * FROM borrowers WHERE id = ?', (borrower_id,))
            borrower = c.fetchone()
            conn.close()
    
            edit_window = Toplevel(self.root)
            edit_window.title("Edit Borrower")
    
            Label(edit_window, text="First Name").grid(row=0, column=0, padx=10, pady=10)
            borrower_firstname_entry = Entry(edit_window)
            borrower_firstname_entry.grid(row=0, column=1, padx=10, pady=10)
            borrower_firstname_entry.insert(0, borrower[1])
    
            Label(edit_window, text="Last Name").grid(row=1, column=0, padx=10, pady=10)
            borrower_lastname_entry = Entry(edit_window)
            borrower_lastname_entry.grid(row=1, column=1, padx=10, pady=10)
            borrower_lastname_entry.insert(0, borrower[2])
    
            Label(edit_window, text="Middle Name").grid(row=2, column=0, padx=10, pady=10)
            borrower_middlename_entry = Entry(edit_window)
            borrower_middlename_entry.grid(row=2, column=1, padx=10, pady=10)
            borrower_middlename_entry.insert(0, borrower[3])
    
            Label(edit_window, text="Contact No").grid(row=3, column=0, padx=10, pady=10)
            borrower_contact_no_entry = Entry(edit_window)
            borrower_contact_no_entry.grid(row=3, column=1, padx=10, pady=10)
            borrower_contact_no_entry.insert(0, borrower[4])
    
            Label(edit_window, text="Address").grid(row=4, column=0, padx=10, pady=10)
            borrower_address_entry = Entry(edit_window)
            borrower_address_entry.grid(row=4, column=1, padx=10, pady=10)
            borrower_address_entry.insert(0, borrower[5])
    
            def update_borrower():
                new_firstname = borrower_firstname_entry.get()
                new_lastname = borrower_lastname_entry.get()
                new_middlename = borrower_middlename_entry.get()
                new_contact_no = borrower_contact_no_entry.get()
                new_address = borrower_address_entry.get()
    
                conn = sqlite3.connect('loan_management1.db')
                c = conn.cursor()
                c.execute('UPDATE borrowers SET firstname=?, lastname=?, middlename=?, contact_no=?, address=? WHERE id=?',
                      (new_firstname, new_lastname, new_middlename, new_contact_no, new_address, borrower_id))
                conn.commit()
                conn.close()
    
                messagebox.showinfo("Update Successful", "Borrower details updated successfully")
                edit_window.destroy()
                self.load_borrowers()
    
            Button(edit_window, text="Update", command=update_borrower).grid(row=5, column=0, columnspan=2, pady=10)
    
        else:
            messagebox.showwarning("Selection Required", "Please select a borrower to edit.")

    def edit_loan(self):
        selected_item = self.loan_tree.selection()
        if selected_item:
            loan_id = self.loan_tree.item(selected_item, 'values')[0]
            conn = sqlite3.connect('loan_management1.db')
            c = conn.cursor()
            c.execute('SELECT * FROM loans WHERE id = ?', (loan_id,))
            loan = c.fetchone()
            conn.close()
    
            edit_window = Toplevel(self.root)
            edit_window.title("Edit Loan")
    
            Label(edit_window, text="Borrower ID").grid(row=0, column=0, padx=10, pady=10)
            loan_borrower_id_entry = Entry(edit_window)
            loan_borrower_id_entry.grid(row=0, column=1, padx=10, pady=10)
            loan_borrower_id_entry.insert(0, loan[1])
    
            Label(edit_window, text="Amount").grid(row=1, column=0, padx=10, pady=10)
            loan_amount_entry = Entry(edit_window)
            loan_amount_entry.grid(row=1, column=1, padx=10, pady=10)
            loan_amount_entry.insert(0, loan[2])
    
            Label(edit_window, text="Plan ID").grid(row=2, column=0, padx=10, pady=10)
            loan_plan_id_entry = Entry(edit_window)
            loan_plan_id_entry.grid(row=2, column=1, padx=10, pady=10)
            loan_plan_id_entry.insert(0, loan[3])
    
            Label(edit_window, text="Status").grid(row=3, column=0, padx=10, pady=10)
            loan_status_entry = Entry(edit_window)
            loan_status_entry.grid(row=3, column=1, padx=10, pady=10)
            loan_status_entry.insert(0, loan[4])
    
            def update_loan():
                new_borrower_id = loan_borrower_id_entry.get()
                new_amount = loan_amount_entry.get()
                new_plan_id = loan_plan_id_entry.get()
                new_status = loan_status_entry.get()
    
                conn = sqlite3.connect('loan_management1.db')
                c = conn.cursor()
                c.execute('UPDATE loans SET borrower_id=?, amount=?, plan_id=?, status=? WHERE id=?',
                          (new_borrower_id, new_amount, new_plan_id, new_status, loan_id))
                conn.commit()
                conn.close()
    
                messagebox.showinfo("Update Successful", "Loan details updated successfully")
                edit_window.destroy()
                self.load_loans()
    
            Button(edit_window, text="Update", command=update_loan).grid(row=4, column=0, columnspan=2, pady=10)
    
        else:
            messagebox.showwarning("Selection Required", "Please select a loan to edit.")

    def edit_payment(self):
        selected_item = self.payment_tree.selection()
        if selected_item:
            payment_id = self.payment_tree.item(selected_item, 'values')[0]
            conn = sqlite3.connect('loan_management1.db')
            c = conn.cursor()
            c.execute('SELECT * FROM payments WHERE id = ?', (payment_id,))
            payment = c.fetchone()
            conn.close()
    
            edit_window = Toplevel(self.root)
            edit_window.title("Edit Payment")
    
            Label(edit_window, text="Loan ID").grid(row=0, column=0, padx=10, pady=10)
            payment_loan_id_entry = Entry(edit_window)
            payment_loan_id_entry.grid(row=0, column=1, padx=10, pady=10)
            payment_loan_id_entry.insert(0, payment[1])
    
            Label(edit_window, text="Amount").grid(row=1, column=0, padx=10, pady=10)
            payment_amount_entry = Entry(edit_window)
            payment_amount_entry.grid(row=1, column=1, padx=10, pady=10)
            payment_amount_entry.insert(0, payment[2])
    
            Label(edit_window, text="Penalty Amount").grid(row=2, column=0, padx=10, pady=10)
            payment_penalty_amount_entry = Entry(edit_window)
            payment_penalty_amount_entry.grid(row=2, column=1, padx=10, pady=10)
            payment_penalty_amount_entry.insert(0, payment[3])

            Label(edit_window, text="Date Created").grid(row=3, column=0, padx=10, pady=10)
            payment_date_created_entry = Entry(edit_window)
            payment_date_created_entry.grid(row=3, column=1, padx=10, pady=10)
            payment_date_created_entry.insert(0, payment[4])
    
            def update_payment():
                new_loan_id = payment_loan_id_entry.get()
                new_amount = payment_amount_entry.get()
                new_penalty_amount = payment_penalty_amount_entry.get()
                new_date_created = payment_date_created_entry.get()
    
                conn = sqlite3.connect('loan_management1.db')
                c = conn.cursor()
                c.execute('UPDATE payments SET loan_id=?, amount=?, penalty_amount=?, date_created=? WHERE id=?',
                          (new_loan_id, new_amount, new_penalty_amount, new_date_created, payment_id))
                conn.commit()
                conn.close()

                messagebox.showinfo("Update Successful", "Payment details updated successfully")
                edit_window.destroy()
                self.load_payments()
    
            Button(edit_window, text="Update", command=update_payment).grid(row=4, column=0, columnspan=2, pady=10)
    
        else:
            messagebox.showwarning("Selection Required", "Please select a payment to edit.")

    def edit_user(self):
        selected_item = self.user_tree.selection()
        if selected_item:
            user_id = self.user_tree.item(selected_item, 'values')[0]
            conn = sqlite3.connect('loan_management1.db')
            c = conn.cursor()
            c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            user = c.fetchone()
            conn.close()
    
            edit_window = Toplevel(self.root)
            edit_window.title("Edit User")
    
            Label(edit_window, text="Username").grid(row=0, column=0, padx=10, pady=10)
            user_username_entry = Entry(edit_window)
            user_username_entry.grid(row=0, column=1, padx=10, pady=10)
            user_username_entry.insert(0, user[1])
    
            Label(edit_window, text="Password").grid(row=1, column=0, padx=10, pady=10)
            user_password_entry = Entry(edit_window, show="*")
            user_password_entry.grid(row=1, column=1, padx=10, pady=10)
            user_password_entry.insert(0, user[2])
    
            def update_user():
                new_username = user_username_entry.get()
                new_password = user_password_entry.get()
    
                conn = sqlite3.connect('loan_management1.db')
                c = conn.cursor()
                c.execute('UPDATE users SET username=?, password=? WHERE id=?',
                          (new_username, new_password, user_id))
                conn.commit()
                conn.close()
    
                messagebox.showinfo("Update Successful", "User details updated successfully")
                edit_window.destroy()
                self.load_users()
    
            Button(edit_window, text="Update", command=update_user).grid(row=2, column=0, columnspan=2, pady=10)
    
        else:
            messagebox.showwarning("Selection Required", "Please select a user to edit.")


if __name__ == "__main__":
    root = Tk()
    app = LoanManagementApp(root)
    root.mainloop()
