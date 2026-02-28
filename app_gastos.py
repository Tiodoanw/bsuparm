import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys
from datetime import datetime

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FILE_NAME = os.path.join(BASE_DIR, 'expenses.json')

def load_expenses():
    if not os.path.exists(FILE_NAME):
        return []
    try:
        with open(FILE_NAME, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []

def save_expenses(expenses):
    with open(FILE_NAME, 'w') as file:
        json.dump(expenses, file, indent=4)

def get_next_id(expenses):
    return max([exp['id'] for exp in expenses], default=0) + 1

class ExpenseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Gastos Personales")
        self.root.geometry("600x450")
        
        self.desc_var = tk.StringVar()
        self.amount_var = tk.StringVar()
        
        input_frame = tk.Frame(root)
        input_frame.pack(pady=10)
        
        tk.Label(input_frame, text="Descripción:").grid(row=0, column=0, padx=5)
        tk.Entry(input_frame, textvariable=self.desc_var, width=20).grid(row=0, column=1, padx=5)
        
        tk.Label(input_frame, text="Monto ($):").grid(row=0, column=2, padx=5)
        tk.Entry(input_frame, textvariable=self.amount_var, width=10).grid(row=0, column=3, padx=5)
        
        tk.Button(input_frame, text="Añadir Gasto", command=self.add_expense, bg="lightblue").grid(row=0, column=4, padx=10)

        columns = ("ID", "Fecha", "Descripción", "Monto")
        self.tree = ttk.Treeview(root, columns=columns, show="headings", height=12)
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Fecha", text="Fecha")
        self.tree.heading("Descripción", text="Descripción")
        self.tree.heading("Monto", text="Monto")
        
        self.tree.column("ID", width=50, anchor=tk.CENTER)
        self.tree.column("Fecha", width=100, anchor=tk.CENTER)
        self.tree.column("Descripción", width=250, anchor=tk.W)
        self.tree.column("Monto", width=100, anchor=tk.E)
        
        self.tree.pack(pady=10)
        
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Eliminar Seleccionado", command=self.delete_expense, bg="lightcoral").grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="Ver Resumen Total", command=self.show_summary, bg="lightgreen").grid(row=0, column=1, padx=10)

        self.refresh_table()

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        expenses = load_expenses()
        for exp in expenses:
            self.tree.insert("", tk.END, values=(exp['id'], exp['date'], exp['description'], f"${exp['amount']:.2f}"))

    def add_expense(self):
        desc = self.desc_var.get().strip()
        try:
            amount = float(self.amount_var.get())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Por favor ingresa un monto numérico positivo.")
            return

        if not desc:
            messagebox.showerror("Error", "La descripción no puede estar vacía.")
            return

        expenses = load_expenses()
        expenses.append({
            'id': get_next_id(expenses),
            'date': datetime.now().strftime("%Y-%m-%d"),
            'description': desc,
            'amount': amount
        })
        save_expenses(expenses)
        
        self.desc_var.set("")
        self.amount_var.set("")
        self.refresh_table()
        messagebox.showinfo("Éxito", "Gasto añadido correctamente.")

    def delete_expense(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor selecciona un gasto de la tabla para eliminar.")
            return
            
        item_values = self.tree.item(selected_item[0], 'values')
        expense_id = int(item_values[0])
        
        expenses = load_expenses()
        expenses = [exp for exp in expenses if exp['id'] != expense_id]
        save_expenses(expenses)
        
        self.refresh_table()
        messagebox.showinfo("Éxito", "Gasto eliminado.")

    def show_summary(self):
        expenses = load_expenses()
        total = sum(exp['amount'] for exp in expenses)
        messagebox.showinfo("Resumen de Gastos", f"El total de tus gastos registrados es:\n\n${total:.2f}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseApp(root)
    root.mainloop()
