import tkinter as tk
from tkinter import ttk
from supabase_manager import format_datetime

class CalendarView:
    def __init__(self, notebook, app):
        self.app = app
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text="Календарь")
        self.setup_ui()
    
    def setup_ui(self):
        self.canvas = tk.Canvas(self.frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.inner_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        
        ttk.Label(self.inner_frame, text="Календарь задач", style="Header.TLabel").pack(pady=10)
        
        self.days_frame = ttk.Frame(self.inner_frame)
        self.days_frame.pack(fill=tk.BOTH, expand=True)
    
    def update(self, tasks):
        for widget in self.days_frame.winfo_children():
            widget.destroy()
        
        tasks_by_date = {}
        for task in tasks:
            deadline = task["deadline"][:10]
            if deadline not in tasks_by_date:
                tasks_by_date[deadline] = []
            tasks_by_date[deadline].append(task)
        
        sorted_dates = sorted(tasks_by_date.keys())
        
        for i, date in enumerate(sorted_dates):
            date_frame = ttk.LabelFrame(self.days_frame, text=date)
            date_frame.pack(fill=tk.X, padx=10, pady=5)
            
            for task in tasks_by_date[date]:
                task_frame = ttk.Frame(date_frame)
                task_frame.pack(fill=tk.X, padx=5, pady=2)
                
                ttk.Label(task_frame, text=task["title"], width=30).pack(side=tk.LEFT)
                ttk.Label(task_frame, text=task["priority"], width=10).pack(side=tk.LEFT)
                ttk.Label(task_frame, text=task["status"], width=15).pack(side=tk.LEFT)
                ttk.Label(task_frame, text=format_datetime(task["deadline"]), width=15).pack(side=tk.LEFT)
                
                ttk.Button(task_frame, text="Подробнее", 
                          command=lambda t=task: self.app.show_task_details(t)).pack(side=tk.RIGHT)