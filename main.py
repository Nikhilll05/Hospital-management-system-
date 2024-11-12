import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import hashlib
import uuid

class HospitalDB:
    def __init__(self):
        self.conn = sqlite3.connect('hospital.db')
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Create Users table for login
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )''')
        
        # Create Patients table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            patient_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            phone TEXT,
            address TEXT,
            blood_group TEXT
        )''')
        
        # Create Doctors table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            doctor_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            specialization TEXT,
            phone TEXT,
            email TEXT
        )''')
        
        # Create Appointments table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            appointment_id TEXT PRIMARY KEY,
            patient_id TEXT,
            doctor_id TEXT,
            date TEXT,
            time TEXT,
            status TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id),
            FOREIGN KEY (doctor_id) REFERENCES doctors (doctor_id)
        )''')
        
        # Insert default admin user if not exists
        cursor.execute('''
        INSERT OR IGNORE INTO users (username, password, role)
        VALUES (?, ?, ?)
        ''', ('admin', hashlib.sha256('admin123'.encode()).hexdigest(), 'admin'))
        
        self.conn.commit()

class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hospital Management System - Login")
        self.root.geometry("300x200")
        self.db = HospitalDB()
        self.create_widgets()
        
    def create_widgets(self):
        # Username
        tk.Label(self.root, text="Username:").pack(pady=5)
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack(pady=5)
        
        # Password
        tk.Label(self.root, text="Password:").pack(pady=5)
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack(pady=5)
        
        # Login button
        tk.Button(self.root, text="Login", command=self.login).pack(pady=20)
        
    def login(self):
        username = self.username_entry.get()
        password = hashlib.sha256(self.password_entry.get().encode()).hexdigest()
        
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT role FROM users WHERE username = ? AND password = ?',
                      (username, password))
        result = cursor.fetchone()
        
        if result:
            self.root.destroy()
            MainWindow(result[0])
        else:
            messagebox.showerror("Error", "Invalid credentials")

class MainWindow:
    def __init__(self, role):
        self.root = tk.Tk()
        self.root.title("Hospital Management System")
        self.root.geometry("800x600")
        self.db = HospitalDB()
        self.role = role
        self.create_widgets()
        
    def create_widgets(self):
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(expand=True, fill='both')
        
        # Patients tab
        patients_frame = ttk.Frame(notebook)
        notebook.add(patients_frame, text='Patients')
        self.create_patients_tab(patients_frame)
        
        # Doctors tab
        doctors_frame = ttk.Frame(notebook)
        notebook.add(doctors_frame, text='Doctors')
        self.create_doctors_tab(doctors_frame)
        
        # Appointments tab
        appointments_frame = ttk.Frame(notebook)
        notebook.add(appointments_frame, text='Appointments')
        self.create_appointments_tab(appointments_frame)
    
    def create_patients_tab(self, parent):
        # Patient registration form
        form_frame = ttk.LabelFrame(parent, text="Patient Registration")
        form_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        
        # Patient details entries
        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        self.patient_name = ttk.Entry(form_frame)
        self.patient_name.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Age:").grid(row=1, column=0, padx=5, pady=5)
        self.patient_age = ttk.Entry(form_frame)
        self.patient_age.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Gender:").grid(row=2, column=0, padx=5, pady=5)
        self.patient_gender = ttk.Combobox(form_frame, values=["Male", "Female", "Other"])
        self.patient_gender.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Phone:").grid(row=3, column=0, padx=5, pady=5)
        self.patient_phone = ttk.Entry(form_frame)
        self.patient_phone.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Address:").grid(row=4, column=0, padx=5, pady=5)
        self.patient_address = ttk.Entry(form_frame)
        self.patient_address.grid(row=4, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Blood Group:").grid(row=5, column=0, padx=5, pady=5)
        self.patient_blood = ttk.Combobox(form_frame, values=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
        self.patient_blood.grid(row=5, column=1, padx=5, pady=5)
        
        ttk.Button(form_frame, text="Register Patient", command=self.register_patient).grid(row=6, column=0, columnspan=2, pady=20)
        
        # Patient list
        list_frame = ttk.LabelFrame(parent, text="Patient List")
        list_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        
        self.patient_tree = ttk.Treeview(list_frame, columns=("ID", "Name", "Age", "Gender", "Phone"))
        self.patient_tree.heading("ID", text="ID")
        self.patient_tree.heading("Name", text="Name")
        self.patient_tree.heading("Age", text="Age")
        self.patient_tree.heading("Gender", text="Gender")
        self.patient_tree.heading("Phone", text="Phone")
        self.patient_tree.column("ID", width=100)
        self.patient_tree.pack(padx=5, pady=5)
        
        self.refresh_patient_list()
    
    def create_doctors_tab(self, parent):
        # Doctor registration form
        form_frame = ttk.LabelFrame(parent, text="Doctor Registration")
        form_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        
        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        self.doctor_name = ttk.Entry(form_frame)
        self.doctor_name.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Specialization:").grid(row=1, column=0, padx=5, pady=5)
        self.doctor_specialization = ttk.Entry(form_frame)
        self.doctor_specialization.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Phone:").grid(row=2, column=0, padx=5, pady=5)
        self.doctor_phone = ttk.Entry(form_frame)
        self.doctor_phone.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Email:").grid(row=3, column=0, padx=5, pady=5)
        self.doctor_email = ttk.Entry(form_frame)
        self.doctor_email.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Button(form_frame, text="Register Doctor", command=self.register_doctor).grid(row=4, column=0, columnspan=2, pady=20)
        
        # Doctor list
        list_frame = ttk.LabelFrame(parent, text="Doctor List")
        list_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        
        self.doctor_tree = ttk.Treeview(list_frame, columns=("ID", "Name", "Specialization", "Phone"))
        self.doctor_tree.heading("ID", text="ID")
        self.doctor_tree.heading("Name", text="Name")
        self.doctor_tree.heading("Specialization", text="Specialization")
        self.doctor_tree.heading("Phone", text="Phone")
        self.doctor_tree.column("ID", width=100)
        self.doctor_tree.pack(padx=5, pady=5)
        
        self.refresh_doctor_list()
    
    def create_appointments_tab(self, parent):
        # Appointment booking form
        form_frame = ttk.LabelFrame(parent, text="Book Appointment")
        form_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        
        ttk.Label(form_frame, text="Patient ID:").grid(row=0, column=0, padx=5, pady=5)
        self.appointment_patient = ttk.Entry(form_frame)
        self.appointment_patient.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Doctor ID:").grid(row=1, column=0, padx=5, pady=5)
        self.appointment_doctor = ttk.Entry(form_frame)
        self.appointment_doctor.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Date (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=5)
        self.appointment_date = ttk.Entry(form_frame)
        self.appointment_date.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Time (HH:MM):").grid(row=3, column=0, padx=5, pady=5)
        self.appointment_time = ttk.Entry(form_frame)
        self.appointment_time.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Button(form_frame, text="Book Appointment", command=self.book_appointment).grid(row=4, column=0, columnspan=2, pady=20)
        
        # Appointment list
        list_frame = ttk.LabelFrame(parent, text="Appointment List")
        list_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        
        self.appointment_tree = ttk.Treeview(list_frame, columns=("ID", "Patient", "Doctor", "Date", "Time", "Status"))
        self.appointment_tree.heading("ID", text="ID")
        self.appointment_tree.heading("Patient", text="Patient")
        self.appointment_tree.heading("Doctor", text="Doctor")
        self.appointment_tree.heading("Date", text="Date")
        self.appointment_tree.heading("Time", text="Time")
        self.appointment_tree.heading("Status", text="Status")
        self.appointment_tree.column("ID", width=100)
        self.appointment_tree.pack(padx=5, pady=5)
        
        self.refresh_appointment_list()
    
    def register_patient(self):
        try:
            patient_id = str(uuid.uuid4())
            cursor = self.db.conn.cursor()
            cursor.execute('''
            INSERT INTO patients (patient_id, name, age, gender, phone, address, blood_group)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (patient_id, self.patient_name.get(), self.patient_age.get(),
                 self.patient_gender.get(), self.patient_phone.get(),
                 self.patient_address.get(), self.patient_blood.get()))
            self.db.conn.commit()
            messagebox.showinfo("Success", f"Patient registered successfully\nID: {patient_id}")
            self.refresh_patient_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def register_doctor(self):
        try:
            doctor_id = str(uuid.uuid4())
            cursor = self.db.conn.cursor()
            cursor.execute('''
            INSERT INTO doctors (doctor_id, name, specialization, phone, email)
            VALUES (?, ?, ?, ?, ?)
            ''', (doctor_id, self.doctor_name.get(), self.doctor_specialization.get(),
                 self.doctor_phone.get(), self.doctor_email.get()))
            self.db.conn.commit()
            messagebox.showinfo("Success", f"Doctor registered successfully\nID: {doctor_id}")
            self.refresh_doctor_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def book_appointment(self):
        try:
            appointment_id = str(uuid.uuid4())
            cursor = self.db.conn.cursor()
            cursor.execute('''
            INSERT INTO appointments (appointment_id, patient_id, doctor_id, date, time, status)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (appointment_id, self.appointment_patient.get(),
                 self.appointment_doctor.get(), self.appointment_date.get(),
                 self.appointment_time.get(), "Scheduled"))
            self.db.conn.commit()
            messagebox.showinfo("Success", "Appointment booked successfully")
            self.refresh_appointment_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def refresh_patient_list(self):
        for item in self.patient_tree.get_children():
            self.patient_tree.delete(item)
        
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT patient_id, name, age, gender, phone FROM patients')
        for row in cursor.fetchall():
            self.patient_tree.insert('', 'end', values=row)
    
    def refresh_doctor_list(self):
        for item in self.doctor_tree.get_children():
            self.doctor_tree.delete(item)
        
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT doctor_id, name, specialization, phone FROM doctors')
        for row in cursor.fetchall():
            self.doctor_tree.insert('', 'end', values=row)
    
    def refresh_appointment_list(self):
        for item in self.appointment_tree.get_children():
            self.appointment_tree.delete(item)
        
        cursor = self.db.conn.cursor()
        cursor.execute('''
        SELECT a.appointment_id, p.name, d.name, a.date, a.time, a.status
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
        ''')
        for row in cursor.fetchall():
            self.appointment_tree.insert('', 'end', values=row)
    
    def run(self):
        self.root.mainloop()

class SearchWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Search Records")
        self.window.geometry("400x300")
        self.db = HospitalDB()
        self.create_widgets()
    
    def create_widgets(self):
        # Search options
        ttk.Label(self.window, text="Search by:").pack(pady=5)
        self.search_type = ttk.Combobox(self.window, 
                                      values=["Patient ID", "Patient Name", 
                                             "Doctor ID", "Doctor Name"])
        self.search_type.pack(pady=5)
        
        ttk.Label(self.window, text="Search term:").pack(pady=5)
        self.search_term = ttk.Entry(self.window)
        self.search_term.pack(pady=5)
        
        ttk.Button(self.window, text="Search", 
                  command=self.perform_search).pack(pady=20)
        
        # Results tree
        self.result_tree = ttk.Treeview(self.window, 
                                       columns=("ID", "Name", "Type", "Details"))
        self.result_tree.heading("ID", text="ID")
        self.result_tree.heading("Name", text="Name")
        self.result_tree.heading("Type", text="Type")
        self.result_tree.heading("Details", text="Details")
        self.result_tree.pack(pady=10, padx=10, fill='both', expand=True)
    
    def perform_search(self):
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        search_type = self.search_type.get()
        search_term = self.search_term.get()
        
        cursor = self.db.conn.cursor()
        
        if "Patient" in search_type:
            if "ID" in search_type:
                cursor.execute('''
                SELECT patient_id, name, 'Patient', 
                       gender || ', Age: ' || age || ', Phone: ' || phone
                FROM patients WHERE patient_id LIKE ?
                ''', (f'%{search_term}%',))
            else:
                cursor.execute('''
                SELECT patient_id, name, 'Patient', 
                       gender || ', Age: ' || age || ', Phone: ' || phone
                FROM patients WHERE name LIKE ?
                ''', (f'%{search_term}%',))
        else:
            if "ID" in search_type:
                cursor.execute('''
                SELECT doctor_id, name, 'Doctor', 
                       specialization || ', Phone: ' || phone
                FROM doctors WHERE doctor_id LIKE ?
                ''', (f'%{search_term}%',))
            else:
                cursor.execute('''
                SELECT doctor_id, name, 'Doctor', 
                       specialization || ', Phone: ' || phone
                FROM doctors WHERE name LIKE ?
                ''', (f'%{search_term}%',))
        
        for row in cursor.fetchall():
            self.result_tree.insert('', 'end', values=row)

def main():
    login = LoginWindow()
    login.root.mainloop()

if __name__ == "__main__":
    main()
    
class HospitalDB:
    def __init__(self):
        self.conn = sqlite3.connect('hospital.db')
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Add Medical Records table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS medical_records (
            record_id TEXT PRIMARY KEY,
            patient_id TEXT,
            doctor_id TEXT,
            date TEXT,
            diagnosis TEXT,
            treatment TEXT,
            notes TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id),
            FOREIGN KEY (doctor_id) REFERENCES doctors (doctor_id)
        )''')
        
        # Add Prescriptions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS prescriptions (
            prescription_id TEXT PRIMARY KEY,
            record_id TEXT,
            medicine_name TEXT,
            dosage TEXT,
            frequency TEXT,
            duration TEXT,
            FOREIGN KEY (record_id) REFERENCES medical_records (record_id)
        )''')
        
        # Add Bills table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS bills (
            bill_id TEXT PRIMARY KEY,
            patient_id TEXT,
            date TEXT,
            description TEXT,
            amount REAL,
            status TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
        )''')
        
        self.conn.commit()

class MedicalRecordWindow:
    def __init__(self, parent, patient_id):
        self.window = tk.Toplevel(parent)
        self.window.title("Medical Records")
        self.window.geometry("800x600")
        self.db = HospitalDB()
        self.patient_id = patient_id
        self.create_widgets()
        
    def create_widgets(self):
        # Patient Info
        info_frame = ttk.LabelFrame(self.window, text="Patient Information")
        info_frame.pack(fill='x', padx=10, pady=5)
        
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM patients WHERE patient_id = ?', (self.patient_id,))
        patient = cursor.fetchone()
        
        ttk.Label(info_frame, text=f"Name: {patient[1]}").pack(side='left', padx=5)
        ttk.Label(info_frame, text=f"Age: {patient[2]}").pack(side='left', padx=5)
        ttk.Label(info_frame, text=f"Gender: {patient[3]}").pack(side='left', padx=5)
        
        # New Record Frame
        record_frame = ttk.LabelFrame(self.window, text="New Medical Record")
        record_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(record_frame, text="Doctor:").grid(row=0, column=0, padx=5, pady=5)
        self.doctor_var = tk.StringVar()
        cursor.execute('SELECT doctor_id, name FROM doctors')
        doctors = cursor.fetchall()
        self.doctor_combo = ttk.Combobox(record_frame, textvariable=self.doctor_var,
                                       values=[f"{d[0]} - {d[1]}" for d in doctors])
        self.doctor_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(record_frame, text="Diagnosis:").grid(row=1, column=0, padx=5, pady=5)
        self.diagnosis = ttk.Entry(record_frame, width=50)
        self.diagnosis.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(record_frame, text="Treatment:").grid(row=2, column=0, padx=5, pady=5)
        self.treatment = ttk.Entry(record_frame, width=50)
        self.treatment.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(record_frame, text="Notes:").grid(row=3, column=0, padx=5, pady=5)
        self.notes = tk.Text(record_frame, height=4, width=50)
        self.notes.grid(row=3, column=1, padx=5, pady=5)
        
        # Prescription Frame
        prescription_frame = ttk.LabelFrame(record_frame, text="Prescription")
        prescription_frame.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        
        self.prescriptions = []
        self.add_prescription_entry()
        
        ttk.Button(prescription_frame, text="Add More Medicines",
                  command=self.add_prescription_entry).pack(pady=5)
        
        ttk.Button(record_frame, text="Save Medical Record",
                  command=self.save_record).grid(row=5, column=0, columnspan=2, pady=10)
        
        # Records List
        list_frame = ttk.LabelFrame(self.window, text="Medical History")
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.record_tree = ttk.Treeview(list_frame,
                                      columns=("Date", "Doctor", "Diagnosis", "Treatment"))
        self.record_tree.heading("Date", text="Date")
        self.record_tree.heading("Doctor", text="Doctor")
        self.record_tree.heading("Diagnosis", text="Diagnosis")
        self.record_tree.heading("Treatment", text="Treatment")
        self.record_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.record_tree.bind('<Double-1>', self.view_record_details)
        self.refresh_records()
    
    def add_prescription_entry(self):
        frame = ttk.Frame(self.window)
        frame.pack(fill='x', padx=5)
        
        medicine = ttk.Entry(frame, width=20, placeholder="Medicine Name")
        medicine.pack(side='left', padx=2)
        
        dosage = ttk.Entry(frame, width=10, placeholder="Dosage")
        dosage.pack(side='left', padx=2)
        
        frequency = ttk.Entry(frame, width=10, placeholder="Frequency")
        frequency.pack(side='left', padx=2)
        
        duration = ttk.Entry(frame, width=10, placeholder="Duration")
        duration.pack(side='left', padx=2)
        
        self.prescriptions.append((medicine, dosage, frequency, duration))
    
    def save_record(self):
        try:
            record_id = str(uuid.uuid4())
            doctor_id = self.doctor_var.get().split(' - ')[0]
            
            cursor = self.db.conn.cursor()
            
            # Save medical record
            cursor.execute('''
            INSERT INTO medical_records 
            (record_id, patient_id, doctor_id, date, diagnosis, treatment, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (record_id, self.patient_id, doctor_id, 
                 datetime.now().strftime('%Y-%m-%d'),
                 self.diagnosis.get(), self.treatment.get(), 
                 self.notes.get('1.0', 'end-1c')))
            
            # Save prescriptions
            for med, dos, freq, dur in self.prescriptions:
                if med.get():  # Only save if medicine name is provided
                    cursor.execute('''
                    INSERT INTO prescriptions 
                    (prescription_id, record_id, medicine_name, dosage, frequency, duration)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''', (str(uuid.uuid4()), record_id, med.get(), dos.get(),
                         freq.get(), dur.get()))
            
            self.db.conn.commit()
            messagebox.showinfo("Success", "Medical record saved successfully")
            self.refresh_records()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def refresh_records(self):
        for item in self.record_tree.get_children():
            self.record_tree.delete(item)
        
        cursor = self.db.conn.cursor()
        cursor.execute('''
        SELECT m.date, d.name, m.diagnosis, m.treatment
        FROM medical_records m
        JOIN doctors d ON m.doctor_id = d.doctor_id
        WHERE m.patient_id = ?
        ORDER BY m.date DESC
        ''', (self.patient_id,))
        
        for row in cursor.fetchall():
            self.record_tree.insert('', 'end', values=row)
    
    def view_record_details(self, event):
        item = self.record_tree.selection()[0]
        date = self.record_tree.item(item)['values'][0]
        
        details_window = tk.Toplevel(self.window)
        details_window.title("Record Details")
        details_window.geometry("600x400")
        
        cursor = self.db.conn.cursor()
        cursor.execute('''
        SELECT m.*, d.name, p.medicine_name, p.dosage, p.frequency, p.duration
        FROM medical_records m
        JOIN doctors d ON m.doctor_id = d.doctor_id
        LEFT JOIN prescriptions p ON m.record_id = p.record_id
        WHERE m.patient_id = ? AND m.date = ?
        ''', (self.patient_id, date))
        
        record = cursor.fetchone()
        
        ttk.Label(details_window, text="Medical Record Details",
                 font=('Helvetica', 14, 'bold')).pack(pady=10)
        
        details_frame = ttk.Frame(details_window)
        details_frame.pack(fill='both', expand=True, padx=10)
        
        ttk.Label(details_frame, text=f"Date: {record[3]}").pack(anchor='w')
        ttk.Label(details_frame, text=f"Doctor: {record[7]}").pack(anchor='w')
        ttk.Label(details_frame, text=f"Diagnosis: {record[4]}").pack(anchor='w')
        ttk.Label(details_frame, text=f"Treatment: {record[5]}").pack(anchor='w')
        ttk.Label(details_frame, text=f"Notes: {record[6]}").pack(anchor='w')
        
        if record[8]:  # If prescriptions exist
            ttk.Label(details_frame, text="\nPrescriptions:",
                     font=('Helvetica', 12, 'bold')).pack(anchor='w', pady=(10,5))
            ttk.Label(details_frame,
                     text=f"Medicine: {record[8]}\nDosage: {record[9]}\n" \
                          f"Frequency: {record[10]}\nDuration: {record[11]}").pack(anchor='w')

class BillingWindow:
    def __init__(self, parent, patient_id):
        self.window = tk.Toplevel(parent)
        self.window.title("Billing Management")
        self.window.geometry("600x500")
        self.db = HospitalDB()
        self.patient_id = patient_id
        self.create_widgets()
    
    def create_widgets(self):
        # New Bill Frame
        bill_frame = ttk.LabelFrame(self.window, text="New Bill")
        bill_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(bill_frame, text="Description:").grid(row=0, column=0, padx=5, pady=5)
        self.description = ttk.Entry(bill_frame, width=40)
        self.description.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(bill_frame, text="Amount:").grid(row=1, column=0, padx=5, pady=5)
        self.amount = ttk.Entry(bill_frame)
        self.amount.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(bill_frame, text="Generate Bill",
                  command=self.generate_bill).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Bills List
        list_frame = ttk.LabelFrame(self.window, text="Bills History")
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.bill_tree = ttk.Treeview(list_frame,
                                    columns=("Date", "Description", "Amount", "Status"))
        self.bill_tree.heading("Date", text="Date")
        self.bill_tree.heading("Description", text="Description")
        self.bill_tree.heading("Amount", text="Amount")
        self.bill_tree.heading("Status", text="Status")
        self.bill_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.refresh_bills()
    
    def generate_bill(self):
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
            INSERT INTO bills (bill_id, patient_id, date, description, amount, status)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (str(uuid.uuid4()), self.patient_id,
                 datetime.now().strftime('%Y-%m-%d'),
                 self.description.get(), float(self.amount.get()), "Pending"))
            
            self.db.conn.commit()
            messagebox.showinfo("Success", "Bill generated successfully")
            self.refresh_bills()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def refresh_bills(self):
        for item in self.bill_tree.get_children():
            self.bill_tree.delete(item)
        
        cursor = self.db.conn.cursor()
        cursor.execute('''
        SELECT date, description, amount, status
        FROM bills
        WHERE patient_id = ?
        ORDER BY date DESC
        ''', (self.patient_id,))
        
        for row in cursor.fetchall():
            self.bill_tree.insert('', 'end', values=row)