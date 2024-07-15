import tkinter as tk
from tkinter import messagebox
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

# Database setup
conn = sqlite3.connect('bmi_data.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS bmi_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                age INTEGER,
                height REAL,
                weight REAL,
                bmi REAL,
                category TEXT
            )''')
conn.commit()


# BMI Calculator Class
class BMICalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced BMI Calculator")

        # Creating GUI elements
        tk.Label(root, text="Name:").grid(row=0, column=0)
        tk.Label(root, text="Age:").grid(row=1, column=0)
        tk.Label(root, text="Height (cm):").grid(row=2, column=0)
        tk.Label(root, text="Weight (kg):").grid(row=3, column=0)

        self.name_entry = tk.Entry(root)
        self.age_entry = tk.Entry(root)
        self.height_entry = tk.Entry(root)
        self.weight_entry = tk.Entry(root)

        self.name_entry.grid(row=0, column=1)
        self.age_entry.grid(row=1, column=1)
        self.height_entry.grid(row=2, column=1)
        self.weight_entry.grid(row=3, column=1)

        tk.Button(root, text="Calculate BMI", command=self.calculate_bmi).grid(row=4, column=0, columnspan=2)
        tk.Button(root, text="Show History", command=self.show_history).grid(row=5, column=0, columnspan=2)

        self.result_label = tk.Label(root, text="")
        self.result_label.grid(row=6, column=0, columnspan=2)

    def validate_inputs(self):
        try:
            name = self.name_entry.get()
            age = int(self.age_entry.get())
            height = float(self.height_entry.get())
            weight = float(self.weight_entry.get())
            if not name or age <= 0 or height <= 0 or weight <= 0:
                raise ValueError
            return name, age, height, weight
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid values for all fields.")
            return None

    def calculate_bmi(self):
        inputs = self.validate_inputs()
        if inputs:
            name, age, height, weight = inputs
            height_m = height / 100
            bmi = weight / (height_m ** 2)
            category = self.categorize_bmi(bmi)
            self.result_label.config(text=f"BMI: {bmi:.2f} ({category})")
            self.save_to_db(name, age, height, weight, bmi, category)

    def categorize_bmi(self, bmi):
        if bmi < 18.5:
            return "Underweight"
        elif 18.5 <= bmi < 24.9:
            return "Normal weight"
        elif 25 <= bmi < 29.9:
            return "Overweight"
        else:
            return "Obesity"

    def save_to_db(self, name, age, height, weight, bmi, category):
        c.execute("INSERT INTO bmi_data (name, age, height, weight, bmi, category) VALUES (?, ?, ?, ?, ?, ?)",
                  (name, age, height, weight, bmi, category))
        conn.commit()

    def show_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("BMI History")

        c.execute("SELECT * FROM bmi_data")
        rows = c.fetchall()

        columns = ("ID", "Name", "Age", "Height", "Weight", "BMI", "Category")
        tree = tk.ttk.Treeview(history_window, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
        for row in rows:
            tree.insert("", tk.END, values=row)

        tree.pack(fill=tk.BOTH, expand=True)

        tk.Button(history_window, text="Show Graph", command=self.show_graph).pack()

    def show_graph(self):
        c.execute("SELECT * FROM bmi_data")
        data = c.fetchall()
        df = pd.DataFrame(data, columns=["ID", "Name", "Age", "Height", "Weight", "BMI", "Category"])

        fig, ax = plt.subplots()
        df.plot(kind='line', x='ID', y='BMI', ax=ax)

        graph_window = tk.Toplevel(self.root)
        graph_window.title("BMI Graph")

        canvas = FigureCanvasTkAgg(fig, master=graph_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


# Main Program
if __name__ == "__main__":
    root = tk.Tk()
    app = BMICalculator(root)
    root.mainloop()
    conn.close()
