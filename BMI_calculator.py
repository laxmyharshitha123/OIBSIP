import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import matplotlib.pyplot as plt

# -------------------------------------------------------------------
# DATABASE SETUP & HELPER FUNCTIONS
# -------------------------------------------------------------------
DB_NAME = "bmi_tracker.db"

def init_db():
    """Initialize SQLite database table if it doesn't exist."""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    weight REAL NOT NULL,
                    height REAL NOT NULL,
                    bmi REAL NOT NULL,
                    category TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            ''')
            conn.commit()
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Failed to initialize database: {e}")

def save_record(username, weight, height, bmi, category):
    """Save a single calculation record to SQLite."""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('''
                INSERT INTO records (username, weight, height, bmi, category, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username.strip().title(), weight, height, bmi, category, timestamp))
            conn.commit()
            return True
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Failed to save record: {e}")
        return False

def fetch_user_history(username):
    """Fetch BMI records for a specific user ordered by date."""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT timestamp, bmi FROM records 
                WHERE username = ? 
                ORDER BY id ASC
            ''', (username.strip().title(),))
            return cursor.fetchall()
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Failed to retrieve history: {e}")
        return []

# -------------------------------------------------------------------
# GUI APPLICATION CLASS
# -------------------------------------------------------------------
class BMICalculatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BMI Tracker & Visualizer")
        self.geometry("450x520")
        self.resizable(False, False)

        init_db()
        self.create_widgets()

    def create_widgets(self):
        # Header
        header = ttk.Label(self, text="Body Mass Index Calculator", font=("Helvetica", 16, "bold"))
        header.pack(pady=15)

        # Form Frame
        form_frame = ttk.Frame(self, padding=10)
        form_frame.pack(fill="x", padx=20)

        # User Name
        ttk.Label(form_frame, text="User Name:", font=("Helvetica", 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.username_entry = ttk.Entry(form_frame, width=25)
        self.username_entry.grid(row=0, column=1, pady=5)

        # Weight
        ttk.Label(form_frame, text="Weight (kg):", font=("Helvetica", 10)).grid(row=1, column=0, sticky="w", pady=5)
        self.weight_entry = ttk.Entry(form_frame, width=25)
        self.weight_entry.grid(row=1, column=1, pady=5)

        # Height
        ttk.Label(form_frame, text="Height (m):", font=("Helvetica", 10)).grid(row=2, column=0, sticky="w", pady=5)
        self.height_entry = ttk.Entry(form_frame, width=25)
        self.height_entry.grid(row=2, column=1, pady=5)

        # Calculate Button
        calc_btn = ttk.Button(self, text="Calculate & Save BMI", command=self.calculate_and_save)
        calc_btn.pack(pady=15)

        # Result Display Area
        self.result_frame = tk.Frame(self, bg="#f0f0f0", bd=2, relief="groove")
        self.result_frame.pack(fill="x", padx=30, pady=10)

        self.bmi_label = tk.Label(self.result_frame, text="BMI: --", font=("Helvetica", 14, "bold"), bg="#f0f0f0")
        self.bmi_label.pack(pady=(10, 2))

        self.category_label = tk.Label(self.result_frame, text="Category: --", font=("Helvetica", 12), bg="#f0f0f0")
        self.category_label.pack(pady=(0, 10))

        # History / Graph Frame
        history_frame = ttk.Frame(self, padding=10)
        history_frame.pack(fill="x", padx=20, pady=10)

        graph_btn = ttk.Button(history_frame, text="Show BMI Trend Graph", command=self.plot_history)
        graph_btn.pack(fill="x")

    def calculate_and_save(self):
        username = self.username_entry.get().strip()
        
        # Validation checks
        if not username:
            messagebox.showwarning("Input Error", "Please enter a user name.")
            return

        try:
            weight = float(self.weight_entry.get())
            height = float(self.height_entry.get())
            
            if weight <= 0 or height <= 0:
                raise ValueError("Values must be positive.")
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid positive numbers for weight and height.")
            return

        # Calculation
        bmi = weight / (height ** 2)

        # Category and Color Coding
        if bmi < 18.5:
            category = "Underweight"
            color = "#3498db"  # Blue
        elif 18.5 <= bmi <= 24.9:
            category = "Normal"
            color = "#2ecc71"  # Green
        elif 25.0 <= bmi <= 29.9:
            category = "Overweight"
            color = "#f39c12"  # Orange
        else:
            category = "Obese"
            color = "#e74c3c"  # Red

        # Update UI
        self.result_frame.config(bg=color)
        self.bmi_label.config(text=f"BMI: {bmi:.2f}", bg=color, fg="white")
        self.category_label.config(text=f"Category: {category}", bg=color, fg="white")

        # Save to database
        if save_record(username, weight, height, bmi, category):
            messagebox.showinfo("Success", f"Record saved for {username.title()}!")

    def plot_history(self):
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showwarning("Input Error", "Please enter a user name to view history.")
            return

        data = fetch_user_history(username)
        if not data:
            messagebox.showinfo("No Data", f"No historical records found for user '{username.title()}'.")
            return

        # Extract timestamps and BMI scores
        timestamps = [entry[0] for entry in data]
        bmis = [entry[1] for entry in data]

        # Plotting with Matplotlib
        plt.figure(figsize=(7, 4))
        plt.plot(timestamps, bmis, marker='o', color='#2b5b84', linewidth=2, label="BMI")
        
        # Reference Lines for Categories
        plt.axhline(y=18.5, color='#3498db', linestyle='--', label='Normal Min (18.5)')
        plt.axhline(y=24.9, color='#2ecc71', linestyle='--', label='Normal Max (24.9)')
        plt.axhline(y=29.9, color='#f39c12', linestyle='--', label='Overweight Cutoff (29.9)')

        plt.title(f"BMI History Trend: {username.title()}")
        plt.xlabel("Date & Time")
        plt.ylabel("BMI Value")
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        plt.legend(loc="upper left")
        plt.show()

# -------------------------------------------------------------------
# MAIN PROGRAM EXECUTION
# -------------------------------------------------------------------
if __name__ == "__main__":
    app = BMICalculatorApp()
    app.mainloop()