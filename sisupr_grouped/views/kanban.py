import tkinter as tk
from tkinter import ttk, messagebox
from supabase_manager import supabase_client, format_datetime

class KanbanView:
    def __init__(self, notebook, app):
        self.app = app
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text="Kanban доска")
        self.setup_ui()
    
    def setup_ui(self):
        self.columns = ["To Do", "In Progress", "Done"]
        self.kanban_columns = {}
        
        self.canvas = tk.Canvas(self.frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.inner_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        
        for i, column in enumerate(self.columns):
            frame = ttk.LabelFrame(self.inner_frame, text=column)
            frame.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            self.kanban_columns[column] = frame
        
        add_button = ttk.Button(self.inner_frame, text="Добавить задачу", command=self.app.show_add_task_dialog)
        add_button.grid(row=1, column=0, columnspan=len(self.columns), pady=10)
        
        for i in range(len(self.columns)):
            self.inner_frame.columnconfigure(i, weight=1, minsize=250)
    
    def update(self, tasks):
        for column in self.kanban_columns.values():
            for widget in column.winfo_children():
                widget.destroy()
        
        for task in tasks:
            self.add_task(task)
    
    def add_task(self, task):
        frame = ttk.Frame(self.kanban_columns[task["status"]])
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(frame, text=task["title"], font=("Arial", 10, "bold")).pack(anchor=tk.W)
        ttk.Label(frame, text=f"Приоритет: {task['priority']}").pack(anchor=tk.W)
        ttk.Label(frame, text=f"Дедлайн: {format_datetime(task['deadline'])}").pack(anchor=tk.W)
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X)
        
        statuses = list(self.kanban_columns.keys())
        current_index = statuses.index(task["status"])
        
        if current_index > 0:
            prev_status = statuses[current_index - 1]
            ttk.Button(button_frame, text="←", width=3, 
                     command=lambda t=task, s=prev_status: self.change_status(t, s)).pack(side=tk.LEFT)
        
        if current_index < len(statuses) - 1:
            next_status = statuses[current_index + 1]
            ttk.Button(button_frame, text="→", width=3, 
                     command=lambda t=task, s=next_status: self.change_status(t, s)).pack(side=tk.LEFT)
        
        ttk.Button(button_frame, text="...", width=3, 
                 command=lambda t=task: self.app.show_task_details(t)).pack(side=tk.RIGHT)
    
    def change_status(self, task, new_status):
        try:
            supabase_client.table("Task").update({"status": new_status}).eq("id", task["id"]).execute()
            self.app.load_data()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось изменить статус: {str(e)}")