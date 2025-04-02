import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

class StudentManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Course Management System")
        self.root.state('zoomed')  # Maximize window to fill the screen
        self.create_database()
        self.style = ttk.Style()
        self.customize_style()
        self.show_login()
    
    def customize_style(self):
        self.style.theme_use('clam')
        self.style.configure("TFrame", background="black")
        self.style.configure("TLabel", background="black", foreground="orange", font=("Helvetica", 11))
        self.style.configure("TButton", background="black", foreground="gold", font=("Helvetica", 10, "italic"))
        self.style.map("TButton", background=[('active', 'black')], foreground=[('active', 'gold')])
        self.style.configure("TCombobox", font=("Helvetica", 10))
        self.style.configure("Treeview", font=("Helvetica", 10),
                             background="black", fieldbackground="black", foreground="white")
        self.style.map("Treeview", background=[('selected', 'red')])
    
    def create_database(self):
        self.conn = sqlite3.connect("student_management.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                code TEXT PRIMARY KEY,
                name TEXT,
                faculty TEXT,
                fees TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS enrollments (
                student_name TEXT,
                course_code TEXT,
                FOREIGN KEY (course_code) REFERENCES courses(code)
            )
        """)
        self.conn.commit()
    
    def show_login(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Are you admin or student ? ", font=("Helvetica", 12, "italic")).grid(row=0, column=0, padx=5, pady=5)
        self.role_var = tk.StringVar(value="Student")
        role_combo = ttk.Combobox(frame, textvariable=self.role_var, values=["Admin", "Student"], state="readonly")
        role_combo.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Login", command=self.login).grid(row=1, column=0, columnspan=2, pady=15)
    
    def login(self):
        role = self.role_var.get()
        if role == "Admin":
            self.admin_portal()
        else:
            self.student_portal()
    
    def student_portal(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill="both", expand=True)
        
        # Student details entry
        ttk.Label(frame, text="Student Name:", font=("Helvetica", 11, "italic")).grid(
            row=0, column=0, padx=5, pady=5, sticky="w")
        self.name_entry = ttk.Entry(frame, font=("Helvetica", 10))
        self.name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Select Course:", font=("Helvetica", 11, "italic")).grid(
            row=1, column=0, padx=5, pady=5, sticky="w")
        self.course_var = tk.StringVar()
        self.course_menu = ttk.Combobox(frame, textvariable=self.course_var, state="readonly", font=("Helvetica", 10))
        self.course_menu.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # Enrollment and unenrollment buttons
        ttk.Button(frame, text="Enroll", command=self.enroll_course).grid(
            row=2, column=0, columnspan=2, pady=10)
        ttk.Button(frame, text="Unenroll", command=self.unenroll_course).grid(
            row=3, column=0, columnspan=2, pady=10)
        ttk.Button(frame, text="Refresh ", command=self.refresh_student_courses).grid(
            row=4, column=0, columnspan=2, pady=10)
        
        # Table displaying available courses
        table_frame = ttk.Frame(frame)
        table_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        self.course_table = ttk.Treeview(table_frame, columns=("Code", "Name", "Faculty", "Fees"),
                                         show="headings", height=15)
        for col in ("Code", "Name", "Faculty", "Fees"):
            self.course_table.heading(col, text=col)
            self.course_table.column(col, width=250)
        self.course_table.grid(row=0, column=0, sticky="nsew")
        
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.course_table.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.course_table.configure(yscrollcommand=v_scrollbar.set)
        
        ttk.Button(frame, text="Logout", command=self.show_login).grid(
            row=6, column=0, columnspan=2, pady=10)
        self.refresh_student_courses()
    
    def enroll_course(self):
        name = self.name_entry.get().strip()
        course = self.course_var.get().strip()
        if not (name and course):
            messagebox.showerror("don't worry, buddy", "please enroll after entering your good name, my friend!!")
            return
        
        # Check if the student is already enrolled
        self.cursor.execute("SELECT * FROM enrollments WHERE student_name = ?", (name,))
        if self.cursor.fetchone() is not None:
            messagebox.showerror("Enrollment Error", f"{name} is already enrolled in a course")
            return
        
        try:
            self.cursor.execute("INSERT INTO enrollments (student_name, course_code) VALUES (?, ?)", (name, course))
            self.conn.commit()
            messagebox.showinfo("Success", f"student,{name} has enrolled in the course {course}")
            self.refresh_admin_courses()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
    
    def unenroll_course(self):
        student_name = self.name_entry.get().strip()
        if not student_name:
            messagebox.showerror("sorry!!!", "Please enter your good name to unenroll, my friend")
            return
        
        self.cursor.execute("SELECT * FROM enrollments WHERE student_name = ?", (student_name,))
        if self.cursor.fetchone() is None:
            messagebox.showinfo("Unenroll", f"{student_name} is not enrolled in any course")
            return
        
        try:
            self.cursor.execute("DELETE FROM enrollments WHERE student_name = ?", (student_name,))
            self.conn.commit()
            messagebox.showinfo("Success", f"student {student_name} has been unenrolled")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
    
    def refresh_student_courses(self):
        self.cursor.execute("SELECT * FROM courses")
        courses = self.cursor.fetchall()
        # Clear the existing table rows
        for row in self.course_table.get_children():
            self.course_table.delete(row)
        # Update the course selection menu with course names
        self.course_menu["values"] = [course[1] for course in courses]
        # Insert each course into the table
        for course in courses:
            self.course_table.insert("", tk.END, values=course)
    
    def admin_portal(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill="both", expand=True)
        
        # Search section with dropdown to select search field
        search_frame = ttk.Frame(frame)
        search_frame.grid(row=0, column=0, columnspan=4, sticky="ew", pady=5)
        ttk.Label(search_frame, text="Search Field:", font=("Helvetica", 11, "italic")).grid(row=0, column=0, padx=5)
        self.search_field_var = tk.StringVar(value="Course Name")
        search_field_combo = ttk.Combobox(search_frame, textvariable=self.search_field_var, 
                                          values=["Course Code", "Course Name", "Faculty"], state="readonly", width=15)
        search_field_combo.grid(row=0, column=1, padx=5)
        ttk.Label(search_frame, text="Search : ", font=("Helvetica", 11, "italic")).grid(row=0, column=2, padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, font=("Helvetica", 10))
        search_entry.grid(row=0, column=3, padx=5)
        ttk.Button(search_frame, text="Go", command=self.search_courses).grid(row=0, column=4, padx=5)
        ttk.Button(search_frame, text="Clear", command=self.refresh_admin_courses).grid(row=0, column=5, padx=5)
        
        # Course entry section
        fields = ["Course Code", "Course Name", "Faculty", "Fees"]
        self.entries = {}
        for i, field in enumerate(fields, start=1):
            ttk.Label(frame, text=field+":", font=("Helvetica", 11, "italic")).grid(
                row=i, column=0, padx=5, pady=5, sticky="w")
            self.entries[field] = ttk.Entry(frame, font=("Helvetica", 10))
            self.entries[field].grid(row=i, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(frame, text="Add ", command=self.add_course).grid(
            row=5, column=0, columnspan=2, pady=10)
        ttk.Button(frame, text="Delete ", command=self.delete_course).grid(
            row=5, column=2, padx=5, pady=10)
        
        # Admin courses table with scrollbar
        admin_table_frame = ttk.Frame(frame)
        admin_table_frame.grid(row=6, column=0, columnspan=4, pady=10, sticky="nsew")
        admin_table_frame.columnconfigure(0, weight=1)
        admin_table_frame.rowconfigure(0, weight=1)
        
        self.course_table_admin = ttk.Treeview(admin_table_frame, columns=("Code", "Name", "Faculty", "Fees"),
                                               show="headings", height=15)
        for col in ("Code", "Name", "Faculty", "Fees"):
            self.course_table_admin.heading(col, text=col)
            self.course_table_admin.column(col, width=250)
        self.course_table_admin.grid(row=0, column=0, sticky="nsew")
        
        admin_v_scrollbar = ttk.Scrollbar(admin_table_frame, orient="vertical", command=self.course_table_admin.yview)
        admin_v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.course_table_admin.configure(yscrollcommand=admin_v_scrollbar.set)
        
        ttk.Button(frame, text="Logout", command=self.show_login).grid(
            row=7, column=0, columnspan=4, pady=10)
        self.refresh_admin_courses()
    
    def add_course(self):
        code = self.entries["Course Code"].get().strip()
        name = self.entries["Course Name"].get().strip()
        faculty = self.entries["Faculty"].get().strip()
        fees = self.entries["Fees"].get().strip()
        if code and name and faculty and fees:
            try:
                self.cursor.execute("INSERT INTO courses (code, name, faculty, fees) VALUES (?, ?, ?, ?)",
                                    (code, name, faculty, fees))
                self.conn.commit()
                messagebox.showinfo("Success", f"Course {name} has been added successfully")
                self.refresh_admin_courses()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "The Course code already exists")
        else:
            messagebox.showerror("Error", "all fields are necessary")
    
    def delete_course(self):
        selected_item = self.course_table_admin.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a course to delete")
            return
        
        course_data = self.course_table_admin.item(selected_item)
        course_code = course_data["values"][0]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete course {course_code}?"):
            try:
                self.cursor.execute("DELETE FROM courses WHERE code = ?", (course_code,))
                self.conn.commit()
                messagebox.showinfo("Success", f"Course {course_code} has been deleted successfully")
                self.refresh_admin_courses()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", str(e))
    
    def refresh_admin_courses(self):
        # Load all courses when no search filter is applied
        self.cursor.execute("SELECT code, name, faculty, fees FROM courses")
        courses = self.cursor.fetchall()
        # Clear existing rows from the admin table
        for row in self.course_table_admin.get_children():
            self.course_table_admin.delete(row)
        # Insert each course into the admin table
        for course in courses:
            self.course_table_admin.insert("", tk.END, values=course)
    
    def search_courses(self):
        search_term = self.search_var.get().strip()
        search_field = self.search_field_var.get()
        # Map the dropdown selection to the actual database field
        field_map = {
            "Course Code": "code",
            "Course Name": "name",
            "Faculty": "faculty",
            "Fees": "fees"
        }
        db_field = field_map.get(search_field, "name")
        query = f"SELECT code, name, faculty, fees FROM courses WHERE {db_field} LIKE ?"
        search_pattern = f"%{search_term}%"
        self.cursor.execute(query, (search_pattern,))
        courses = self.cursor.fetchall()
        # Clear existing rows from the admin table
        for row in self.course_table_admin.get_children():
            self.course_table_admin.delete(row)
        # Insert each matching course into the admin table
        for course in courses:
            self.course_table_admin.insert("", tk.END, values=course)

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentManagementApp(root)
    root.mainloop()
