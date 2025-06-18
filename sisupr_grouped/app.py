import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from supabase_manager import supabase_client
from views.kanban import KanbanView
from views.calendar import CalendarView
from views.tasks import TasksView
from views.users import UsersView

class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система управления задачами")
        self.root.geometry("1200x800")
        
        self.current_user = {"id": 1, "name": "Admin", "email": "admin@example.com"}
        self.setup_styles()
        self.setup_main_frames()
        self.setup_views()
        self.load_data()
        self.check_notifications()
    
    def setup_styles(self):
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        self.style.configure("TButton", font=("Arial", 10))
        self.style.configure("Header.TLabel", font=("Arial", 12, "bold"))
    
    def setup_main_frames(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(self.header_frame, text="Система управления задачами", style="Header.TLabel").pack(side=tk.LEFT)
        self.user_label = ttk.Label(self.header_frame, text=f"Пользователь: {self.current_user['name']}")
        self.user_label.pack(side=tk.RIGHT)
        
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.notebook = ttk.Notebook(self.content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
    
    def setup_views(self):
        self.kanban_view = KanbanView(self.notebook, self)
        self.calendar_view = CalendarView(self.notebook, self)
        self.tasks_view = TasksView(self.notebook, self)
        
        if self.current_user["id"] == 1:
            self.users_view = UsersView(self.notebook, self)
    
    def load_data(self):
        try:
            tasks = supabase_client.table("Task").select("*").execute().data
            self.kanban_view.update(tasks)
            self.calendar_view.update(tasks)
            self.tasks_view.update(tasks)
            
            if hasattr(self, 'users_view'):
                self.users_view.load_users()
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {str(e)}")
    
    def check_notifications(self):
        try:
            notifications = supabase_client.table("Notification").select("*").eq("user_id", self.current_user["id"]).eq("is_read", False).execute().data
            
            for notification in notifications:
                messagebox.showinfo("Уведомление", notification["message"])
                supabase_client.table("Notification").update({"is_read": True}).eq("id", notification["id"]).execute()
                
        except Exception as e:
            print(f"Ошибка при проверке уведомлений: {e}")
        
        self.root.after(1000, self.check_notifications)