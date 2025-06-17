import tkinter as tk
from tkinter import ttk, messagebox
from supabase import create_client, Client
import datetime
from task_management import TaskManager
from user_management import UserManager
from kanban_board import KanbanBoard
from calendar_view import CalendarView
from notification_system import NotificationSystem

class TaskManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система управления задачами")
        self.root.geometry("1200x800")
        
        # Подключение к Supabase
        self.supabase_url = "https://nnixjfqeygpvpeylkbux.supabase.co"
        self.supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5uaXhqZnFleWdwdnBleWxrYnV4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTAxNDAyNzgsImV4cCI6MjA2NTcxNjI3OH0.Es78nkIZlRv9lRB92T8CPygqLiuM6I327iUWr53Q85U"
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
        # Инициализация модулей
        self.user_manager = UserManager(self.supabase)
        self.task_manager = TaskManager(self.supabase)
        self.notification_system = NotificationSystem(self.supabase)
        
        # Текущий пользователь (для демонстрации)
        self.current_user = None
        
        # Создание интерфейса
        self.create_widgets()
        
        # Проверка уведомлений
        self.check_notifications()
    
    def create_widgets(self):
        # Панель вкладок
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Вкладка Kanban
        self.kanban_frame = ttk.Frame(self.notebook)
        self.kanban_board = KanbanBoard(self.kanban_frame, self.task_manager, self.user_manager)
        self.notebook.add(self.kanban_frame, text="Kanban доска")
        
        # Вкладка Календарь
        self.calendar_frame = ttk.Frame(self.notebook)
        self.calendar_view = CalendarView(self.calendar_frame, self.task_manager)
        self.notebook.add(self.calendar_frame, text="Календарь")
        
        # Вкладка Пользователи (только для администратора)
        self.users_frame = ttk.Frame(self.notebook)
        self.user_manager.create_ui(self.users_frame)
        self.notebook.add(self.users_frame, text="Пользователи", state="hidden")
        
        # Кнопка входа/выхода
        self.auth_button = ttk.Button(self.root, text="Войти", command=self.toggle_auth)
        self.auth_button.pack(side=tk.BOTTOM, pady=10)
    
    def toggle_auth(self):
        if self.current_user:
            self.logout()
        else:
            self.login()
    
    def login(self):
        # В реальном приложении здесь должна быть форма входа
        # Для демонстрации просто выберем первого пользователя
        users = self.user_manager.get_users()
        if users:
            self.current_user = users[0]
            self.auth_button.config(text="Выйти")
            self.update_ui_for_user()
            messagebox.showinfo("Вход", f"Вы вошли как {self.current_user['name']}")
        else:
            messagebox.showerror("Ошибка", "Нет пользователей в системе")
    
    def logout(self):
        self.current_user = None
        self.auth_button.config(text="Войти")
        self.update_ui_for_user()
        messagebox.showinfo("Выход", "Вы вышли из системы")
    
    def update_ui_for_user(self):
        # Показываем/скрываем вкладку пользователей для администраторов
        if self.current_user and self.current_user.get('is_admin', False):
            self.notebook.tab(2, state="normal")
        else:
            self.notebook.tab(2, state="hidden")
    
    def check_notifications(self):
        if self.current_user:
            notifications = self.notification_system.get_unread_notifications(self.current_user['id'])
            for notification in notifications:
                messagebox.showwarning("Уведомление", notification['message'])
                self.notification_system.mark_as_read(notification['id'])
        
        # Проверяем уведомления каждые 5 минут
        self.root.after(300000, self.check_notifications)

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagementApp(root)
    root.mainloop()