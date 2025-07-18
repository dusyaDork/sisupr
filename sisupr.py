import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import supabase
import os
from PIL import Image, ImageTk

SUPABASE_URL = "https://nnixjfqeygpvpeylkbux.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5uaXhqZnFleWdwdnBleWxrYnV4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTAxNDAyNzgsImV4cCI6MjA2NTcxNjI3OH0.Es78nkIZlRv9lRB92T8CPygqLiuM6I327iUWr53Q85U"
supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

def format_datetime(dt_str):
    if not dt_str:
        return ""
    try:
        dt = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S")
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return dt_str

def parse_datetime(dt_str):
    if not dt_str:
        return None
    try:
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        return dt.strftime("%Y-%m-%dT%H:%M:%S")
    except:
        return dt_str

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Вход в систему")
        self.root.geometry("400x300")
        
        # стили
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        self.style.configure("TButton", font=("Arial", 10))
        
        # основной фрейм
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # заголовок
        ttk.Label(self.main_frame, text="Вход в систему управления задачами", 
                 font=("Arial", 12, "bold")).pack(pady=20)
        
        # поля
        input_frame = ttk.Frame(self.main_frame)
        input_frame.pack(pady=10)
        
        ttk.Label(input_frame, text="Имя:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        self.name_entry = ttk.Entry(input_frame, width=25)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Email:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        self.email_entry = ttk.Entry(input_frame, width=25)
        self.email_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # кнопки
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Войти", command=self.login).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Регистрация", command=self.show_register_dialog).pack(side=tk.LEFT, padx=10)
    
    def login(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip().lower()
        
        if not name or not email:
            messagebox.showerror("Ошибка", "Введите имя и email")
            return
        
        try:
            # ищем пользователя в бд
            response = supabase_client.table("User").select("*").eq("name", name).eq("email", email).execute()
            if response.data:
                user = response.data[0]
                self.root.destroy()
                
                # запускаем основу
                root = tk.Tk()
                TaskManagerApp(root, user)
                root.mainloop()
            else:
                messagebox.showerror("Ошибка", "Пользователь не найден. Зарегистрируйтесь.")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось войти: {str(e)}")
    
    def show_register_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Регистрация")
        dialog.geometry("400x200")
        
        ttk.Label(dialog, text="Имя:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Email:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        email_entry = ttk.Entry(dialog, width=30)
        email_entry.grid(row=1, column=1, padx=10, pady=5)
        
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Зарегистрироваться", 
                  command=lambda: self.register_user(
                      name_entry.get(),
                      email_entry.get(),
                      dialog
                  )).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Отмена", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def register_user(self, name, email, dialog):
        if not name or not email:
            messagebox.showerror("Ошибка", "Введите имя и email")
            return
        
        try:
            response = supabase_client.table("User").select("*").eq("email", email).execute()
            if response.data:
                messagebox.showerror("Ошибка", "Пользователь с таким email уже существует")
                return
            
            supabase_client.table("User").insert({
                "name": name,
                "email": email
            }).execute()
            
            messagebox.showinfo("Успех", "Регистрация прошла успешно. Теперь вы можете войти.")
            dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось зарегистрироваться: {str(e)}")

class TaskManagerApp:
    def __init__(self, root, user):
        self.root = root
        self.root.title("Система управления задачами")
        self.root.geometry("1200x800")

        self.current_user = user
        
        # стили
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        self.style.configure("TButton", font=("Arial", 10))
        self.style.configure("Header.TLabel", font=("Arial", 12, "bold"))
        
        # осн фреймы
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # верх панель
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(self.header_frame, text="Система управления задачами", style="Header.TLabel").pack(side=tk.LEFT)
        
        self.user_label = ttk.Label(self.header_frame, text=f"Пользователь: {self.current_user['name']}")
        self.user_label.pack(side=tk.RIGHT)
        
        # осн содержимое
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # notebook для вкладок
        self.notebook = ttk.Notebook(self.content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # вкладка Kanban
        self.kanban_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.kanban_frame, text="Kanban доска")
        self.setup_kanban()
        
        # вкладка Календарь
        self.calendar_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.calendar_frame, text="Календарь")
        self.setup_calendar()
        
        # вкладка Задачи
        self.tasks_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tasks_frame, text="Все задачи")
        self.setup_tasks_list()
        
        # вкладка Пользователи (только для админа)
        if self.current_user["id"] == 1:
            self.users_frame = ttk.Frame(self.notebook)
            self.notebook.add(self.users_frame, text="Пользователи")
            self.setup_users_list()
        
        # загружаем данные
        self.load_data()
        
        # запускаем проверку уведомлений
        self.check_notifications()
    
    def setup_kanban(self):
        columns = ["To Do", "In Progress", "Done"]
        
        self.kanban_canvas = tk.Canvas(self.kanban_frame)
        self.kanban_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.kanban_frame, orient=tk.VERTICAL, command=self.kanban_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.kanban_canvas.configure(yscrollcommand=scrollbar.set)
        self.kanban_canvas.bind('<Configure>', lambda e: self.kanban_canvas.configure(scrollregion=self.kanban_canvas.bbox("all")))
        
        self.kanban_inner_frame = ttk.Frame(self.kanban_canvas)
        self.kanban_canvas.create_window((0, 0), window=self.kanban_inner_frame, anchor="nw")
        
        # колонки с фиксированным порядком
        self.kanban_columns = {}
        for i, column in enumerate(columns):
            frame = ttk.LabelFrame(self.kanban_inner_frame, text=column)
            frame.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            self.kanban_columns[column] = frame
        
        add_button = ttk.Button(self.kanban_inner_frame, text="Добавить задачу", command=self.show_add_task_dialog)
        add_button.grid(row=1, column=0, columnspan=len(columns), pady=10)
        
        for i in range(len(columns)):
            self.kanban_inner_frame.columnconfigure(i, weight=1, minsize=250)
    
    def setup_calendar(self):
        # простой календарь
        self.calendar_canvas = tk.Canvas(self.calendar_frame)
        self.calendar_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.calendar_frame, orient=tk.VERTICAL, command=self.calendar_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.calendar_canvas.configure(yscrollcommand=scrollbar.set)
        self.calendar_canvas.bind('<Configure>', lambda e: self.calendar_canvas.configure(scrollregion=self.calendar_canvas.bbox("all")))
        
        self.calendar_inner_frame = ttk.Frame(self.calendar_canvas)
        self.calendar_canvas.create_window((0, 0), window=self.calendar_inner_frame, anchor="nw")
        
        ttk.Label(self.calendar_inner_frame, text="Календарь задач", style="Header.TLabel").pack(pady=10)
        
        self.calendar_days_frame = ttk.Frame(self.calendar_inner_frame)
        self.calendar_days_frame.pack(fill=tk.BOTH, expand=True)
    
    def setup_tasks_list(self):
        self.tasks_tree = ttk.Treeview(self.tasks_frame, columns=("id", "title", "priority", "status", "deadline"), show="headings")
        
        self.tasks_tree.heading("id", text="ID")
        self.tasks_tree.heading("title", text="Название")
        self.tasks_tree.heading("priority", text="Приоритет")
        self.tasks_tree.heading("status", text="Статус")
        self.tasks_tree.heading("deadline", text="Дедлайн")
        
        self.tasks_tree.column("id", width=50)
        self.tasks_tree.column("title", width=200)
        self.tasks_tree.column("priority", width=100)
        self.tasks_tree.column("status", width=100)
        self.tasks_tree.column("deadline", width=150)
        
        scrollbar = ttk.Scrollbar(self.tasks_frame, orient=tk.VERTICAL, command=self.tasks_tree.yview)
        self.tasks_tree.configure(yscrollcommand=scrollbar.set)
        
        self.tasks_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        button_frame = ttk.Frame(self.tasks_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Добавить", command=self.show_add_task_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Редактировать", command=self.edit_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Удалить", command=self.delete_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Обновить", command=self.load_data).pack(side=tk.LEFT, padx=5)
        
        # привязка двойного клика для просмотра деталей
        self.tasks_tree.bind("<Double-1>", self.show_task_details)
    
    def setup_users_list(self):
        self.users_tree = ttk.Treeview(self.users_frame, columns=("id", "name", "email"), show="headings")
        
        self.users_tree.heading("id", text="ID")
        self.users_tree.heading("name", text="Имя")
        self.users_tree.heading("email", text="Email")
        
        self.users_tree.column("id", width=50)
        self.users_tree.column("name", width=150)
        self.users_tree.column("email", width=200)
        
        scrollbar = ttk.Scrollbar(self.users_frame, orient=tk.VERTICAL, command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        
        self.users_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        button_frame = ttk.Frame(self.users_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Добавить", command=self.show_add_user_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Редактировать", command=self.edit_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Удалить", command=self.delete_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Обновить", command=self.load_users).pack(side=tk.LEFT, padx=5)
    
    def load_data(self):
        try:
            tasks = supabase_client.table("Task").select("*").execute().data
            
            # очистка существующих данных
            for column in self.kanban_columns.values():
                for widget in column.winfo_children():
                    widget.destroy()
            
            self.tasks_tree.delete(*self.tasks_tree.get_children())
            
            # заполнение Kanban доски
            for task in tasks:
                self.add_task_to_kanban(task)
                
                # добавление в список задач
                self.tasks_tree.insert("", tk.END, values=(
                    task["id"],
                    task["title"],
                    task["priority"],
                    task["status"],
                    task["deadline"]
                ))
            
            self.update_calendar(tasks)
            
            # загрузка пользователей (если админ)
            if hasattr(self, 'users_tree'):
                self.load_users()
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {str(e)}")
    
    def load_users(self):
        try:
            users = supabase_client.table("User").select("*").execute().data
            self.users_tree.delete(*self.users_tree.get_children())
            
            for user in users:
                self.users_tree.insert("", tk.END, values=(
                    user["id"],
                    user["name"],
                    user["email"]
                ))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить пользователей: {str(e)}")
    
    def add_task_to_kanban(self, task):
        frame = ttk.Frame(self.kanban_columns[task["status"]])
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(frame, text=task["title"], font=("Arial", 10, "bold")).pack(anchor=tk.W)
        ttk.Label(frame, text=f"Приоритет: {task['priority']}").pack(anchor=tk.W)
        ttk.Label(frame, text=f"Дедлайн: {format_datetime(task['deadline'])}").pack(anchor=tk.W)
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X)
        
        # определяем доступные направления перемещения
        statuses = list(self.kanban_columns.keys())
        current_index = statuses.index(task["status"])
        
        # стрелка влево
        if current_index > 0:
            prev_status = statuses[current_index - 1]
            ttk.Button(button_frame, text="←", width=3, 
                    command=lambda t=task, s=prev_status: self.change_task_status(t, s)).pack(side=tk.LEFT)
        
        # стрелка вправо
        if current_index < len(statuses) - 1:
            next_status = statuses[current_index + 1]
            ttk.Button(button_frame, text="→", width=3, 
                    command=lambda t=task, s=next_status: self.change_task_status(t, s)).pack(side=tk.LEFT)
        
        # подробнее
        ttk.Button(button_frame, text="...", width=3, 
                command=lambda t=task: self.show_task_details(t)).pack(side=tk.RIGHT)
    
    def update_calendar(self, tasks):
        # очистка календаря
        for widget in self.calendar_days_frame.winfo_children():
            widget.destroy()
        
        # группировка задач по дате
        tasks_by_date = {}
        for task in tasks:
            deadline = task["deadline"][:10]  # Берем только дату без времени
            if deadline not in tasks_by_date:
                tasks_by_date[deadline] = []
            tasks_by_date[deadline].append(task)
        
        # сортировка дат
        sorted_dates = sorted(tasks_by_date.keys())
        
        # отображение задач по датам
        for i, date in enumerate(sorted_dates):
            date_frame = ttk.LabelFrame(self.calendar_days_frame, text=date)
            date_frame.pack(fill=tk.X, padx=10, pady=5)
            
            for task in tasks_by_date[date]:
                task_frame = ttk.Frame(date_frame)
                task_frame.pack(fill=tk.X, padx=5, pady=2)
                
                ttk.Label(task_frame, text=task["title"], width=30).pack(side=tk.LEFT)
                ttk.Label(task_frame, text=task["priority"], width=10).pack(side=tk.LEFT)
                ttk.Label(task_frame, text=task["status"], width=15).pack(side=tk.LEFT)
                ttk.Label(task_frame, text=format_datetime(task["deadline"]), width=15).pack(side=tk.LEFT)
                
                ttk.Button(task_frame, text="Подробнее", 
                          command=lambda t=task: self.show_task_details(t)).pack(side=tk.RIGHT)
    
    def show_add_task_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить задачу")
        dialog.geometry("500x400")
        assignees_vars = []

        ttk.Label(dialog, text="Название:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        title_entry = ttk.Entry(dialog, width=40)
        title_entry.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Описание:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        desc_text = tk.Text(dialog, width=40, height=5)
        desc_text.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Дедлайн:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        deadline_entry = ttk.Entry(dialog, width=40)
        deadline_entry.grid(row=2, column=1, padx=10, pady=5)
        deadline_entry.insert(0, (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M"))
        
        ttk.Label(dialog, text="Приоритет:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        priority_var = tk.StringVar(value="Средний")
        ttk.Combobox(dialog, textvariable=priority_var, 
                    values=["Низкий", "Средний", "Высокий", "Критический"]).grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Статус:").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
        status_var = tk.StringVar(value="To Do")
        ttk.Combobox(dialog, textvariable=status_var, 
                    values=["To Do", "In Progress", "Done"]).grid(row=4, column=1, padx=10, pady=5, sticky=tk.W)
        
        try:
            users = supabase_client.table("User").select("*").execute().data
            if users:
                ttk.Label(dialog, text="Исполнители:").grid(row=5, column=0, padx=10, pady=5, sticky=tk.W)
                
                assignees_vars = []
                assignees_frame = ttk.Frame(dialog)
                assignees_frame.grid(row=5, column=1, padx=10, pady=5, sticky=tk.W)
                
                for user in users:
                    var = tk.IntVar()
                    ttk.Checkbutton(assignees_frame, text=user["name"], variable=var).pack(anchor=tk.W)
                    assignees_vars.append((user["id"], var))
        except Exception as e:
            print(f"Ошибка при загрузке пользователей: {e}")
        
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Добавить", 
                  command=lambda: self.add_task(
                      title_entry.get(),
                      desc_text.get("1.0", tk.END),
                      deadline_entry.get(),
                      priority_var.get(),
                      status_var.get(),
                      [user_id for user_id, var in assignees_vars if var.get() == 1],
                      dialog
                  )).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Отмена", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def add_task(self, title, description, deadline, priority, status, assignees, dialog):
        if not title:
            messagebox.showerror("Ошибка", "Название задачи обязательно")
            return
        
        try:
            formatted_deadline = parse_datetime(deadline)
            task_data = {
                "title": title,
                "description": description,
                "deadline": formatted_deadline,
                "priority": priority,
                "status": status
            }
            
            response = supabase_client.table("Task").insert(task_data).execute()
            task_id = response.data[0]["id"]
            
            for user_id in assignees:
                supabase_client.table("TaskAssignment").insert({
                    "task_id": task_id,
                    "user_id": user_id
                }).execute()
            
            # обновление интерфейса
            self.load_data()
            dialog.destroy()
            messagebox.showinfo("Успех", "Задача успешно добавлена")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить задачу: {str(e)}")
    
    def show_task_details(self, task=None, event=None):
        # получаем задачу, если вызвано двойным кликом
        if event:
            selected_item = self.tasks_tree.focus()
            if not selected_item:
                return
            task_id = self.tasks_tree.item(selected_item)["values"][0]
            try:
                task = supabase_client.table("Task").select("*").eq("id", task_id).execute().data[0]
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить задачу: {str(e)}")
                return

        if not task or "id" not in task:
            messagebox.showerror("Ошибка", "Задача не найдена")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title(f"Задача: {task.get('title', 'Новая задача')}")
        dialog.geometry("700x600")
        
        dialog.task_id = task["id"]

        info_frame = ttk.LabelFrame(dialog, text="Информация о задаче")
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(info_frame, text=f"Название: {task.get('title', '')}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Статус: {task.get('status', '')}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Приоритет: {task.get('priority', '')}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Дедлайн: {format_datetime(task.get('deadline', ''))}").pack(anchor=tk.W)

        dialog.comments_frame = ttk.LabelFrame(dialog, text="Комментарии")
        dialog.comments_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        dialog.comments_canvas = tk.Canvas(dialog.comments_frame)
        dialog.comments_scrollbar = ttk.Scrollbar(dialog.comments_frame, orient="vertical", command=dialog.comments_canvas.yview)
        dialog.scrollable_frame = ttk.Frame(dialog.comments_canvas)
        
        dialog.scrollable_frame.bind(
            "<Configure>",
            lambda e: dialog.comments_canvas.configure(
                scrollregion=dialog.comments_canvas.bbox("all")
            )
        )
        
        dialog.comments_canvas.create_window((0, 0), window=dialog.scrollable_frame, anchor="nw")
        dialog.comments_canvas.configure(yscrollcommand=dialog.comments_scrollbar.set)
        
        dialog.comments_canvas.pack(side="left", fill="both", expand=True)
        dialog.comments_scrollbar.pack(side="right", fill="y")

        try:
            comments = supabase_client.table("Comment").select("*, User(name)").eq("task_id", task["id"]).execute().data
            for comment in comments:
                comment_frame = ttk.Frame(dialog.scrollable_frame)
                comment_frame.pack(fill=tk.X, padx=5, pady=2)
                
                ttk.Label(comment_frame, 
                        text=f"{comment['User']['name']} ({comment.get('created_at', '')}):",
                        font=('Arial', 9, 'bold')).pack(anchor=tk.W)
                ttk.Label(comment_frame, 
                        text=comment['text'],
                        wraplength=600,
                        justify=tk.LEFT).pack(anchor=tk.W)
        except Exception as e:
            ttk.Label(dialog.scrollable_frame, text=f"Ошибка загрузки комментариев: {str(e)}").pack()

        new_comment_frame = ttk.Frame(dialog)
        new_comment_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.comment_entry = ttk.Entry(new_comment_frame)
        self.comment_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Button(new_comment_frame, text="Добавить",
                command=lambda: self.add_comment(dialog)).pack(side=tk.LEFT)
        
        files_frame = ttk.LabelFrame(dialog, text="Файлы")
        files_frame.pack(fill=tk.X, padx=10, pady=5)

        try:
            files = supabase_client.table("File").select("*").eq("task_id", task["id"]).execute().data
            
            for file in files:
                file_frame = ttk.Frame(files_frame)
                file_frame.pack(fill=tk.X, padx=5, pady=2)
                
                ttk.Label(file_frame, text=file["filename"]).pack(side=tk.LEFT)
                ttk.Button(file_frame, text="Скачать", 
                          command=lambda f=file: self.download_file(f)).pack(side=tk.RIGHT)
        except Exception as e:
            print(f"Ошибка при загрузке файлов: {e}")

        add_file_frame = ttk.Frame(dialog)
        add_file_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(add_file_frame, text="Добавить файл", 
                  command=lambda: self.upload_file(task["id"], dialog)).pack(side=tk.LEFT)
    
    def add_comment(self, dialog):
        text = self.comment_entry.get().strip()
        if not text:
            messagebox.showwarning("Предупреждение", "Введите текст комментария")
            return
        
        try:
            response = supabase_client.table("Comment").insert({
                "task_id": dialog.task_id,
                "user_id": self.current_user["id"],
                "text": text
            }).execute()
            
            if response.data:
                self.comment_entry.delete(0, tk.END)
                
                # обновляем список комментариев без пересоздания окна
                for widget in dialog.winfo_children():
                    if isinstance(widget, ttk.LabelFrame) and widget["text"] == "Комментарии":
                        for child in widget.winfo_children():
                            if isinstance(child, tk.Canvas):
                                canvas = child
                                for item in canvas.winfo_children():
                                    if isinstance(item, ttk.Frame):
                                        scrollable_frame = item
                                        break
                                break
                        break
                
                # добавляем новый комментарий в существующий scrollable_frame
                try:
                    user = supabase_client.table("User").select("name").eq("id", self.current_user["id"]).execute().data[0]
                    user_name = user["name"]
                except:
                    user_name = "Неизвестный"
                    
                comment_frame = ttk.Frame(scrollable_frame)
                comment_frame.pack(fill=tk.X, padx=5, pady=2)
                
                ttk.Label(comment_frame, 
                        text=f"{user_name} ({datetime.now().strftime('%Y-%m-%d %H:%M')}):",
                        font=('Arial', 9, 'bold')).pack(anchor=tk.W)
                ttk.Label(comment_frame, 
                        text=text,
                        wraplength=600,
                        justify=tk.LEFT).pack(anchor=tk.W)
                
                canvas.yview_moveto(1)
                
                messagebox.showinfo("Успех", "Комментарий успешно добавлен")
            else:
                raise Exception("Не удалось добавить комментарий")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить комментарий: {str(e)}")
    
    def upload_file(self, task_id, dialog):
        filepath = filedialog.askopenfilename()
        if not filepath:
            return
        
        filename = os.path.basename(filepath)
        
        try:
            # должна быть загрузка файла в Supabase Storage
            # пока что просто сохраняем информацию о файле в таблицу File
            
            supabase_client.table("File").insert({
                "task_id": task_id,
                "filename": filename,
                "path": filepath  # должен быть путь в Storage
            }).execute()

            dialog.destroy()
            self.show_task_details({"id": task_id})
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {str(e)}")
    
    def download_file(self, file):
        # должно быть скачивание из Supabase Storage
        # пока что просто показываем сообщение
        messagebox.showinfo("Информация", f"Файл {file['filename']} будет скачан")
    
    def change_task_status(self, task, new_status):
        try:
            supabase_client.table("Task").update({"status": new_status}).eq("id", task["id"]).execute()
            self.load_data()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось изменить статус: {str(e)}")
    
    def edit_task(self):
        selected_item = self.tasks_tree.focus()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите задачу для редактирования")
            return
        
        task_id = self.tasks_tree.item(selected_item)["values"][0]
        
        try:
            task = supabase_client.table("Task").select("*").eq("id", task_id).execute().data[0]
            
            dialog = tk.Toplevel(self.root)
            dialog.title("Редактировать задачу")
            dialog.geometry("500x400")
            
            ttk.Label(dialog, text="Название:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
            title_entry = ttk.Entry(dialog, width=40)
            title_entry.grid(row=0, column=1, padx=10, pady=5)
            title_entry.insert(0, task["title"])
            
            ttk.Label(dialog, text="Описание:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
            desc_text = tk.Text(dialog, width=40, height=5)
            desc_text.grid(row=1, column=1, padx=10, pady=5)
            desc_text.insert(tk.END, task["description"])
            
            ttk.Label(dialog, text="Дедлайн:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
            deadline_entry = ttk.Entry(dialog, width=40)
            deadline_entry.grid(row=2, column=1, padx=10, pady=5)
            deadline_entry.insert(0, task["deadline"])
            
            ttk.Label(dialog, text="Приоритет:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
            priority_var = tk.StringVar(value=task["priority"])
            ttk.Combobox(dialog, textvariable=priority_var, 
                        values=["Низкий", "Средний", "Высокий", "Критический"]).grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)
            
            ttk.Label(dialog, text="Статус:").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
            status_var = tk.StringVar(value=task["status"])
            ttk.Combobox(dialog, textvariable=status_var, 
                        values=["To Do", "In Progress", "Done"]).grid(row=4, column=1, padx=10, pady=5, sticky=tk.W)
            
            # Кнопки
            button_frame = ttk.Frame(dialog)
            button_frame.grid(row=5, column=0, columnspan=2, pady=10)
            
            ttk.Button(button_frame, text="Сохранить", 
                      command=lambda: self.update_task(
                          task["id"],
                          title_entry.get(),
                          desc_text.get("1.0", tk.END),
                          deadline_entry.get(),
                          priority_var.get(),
                          status_var.get(),
                          dialog
                      )).pack(side=tk.LEFT, padx=5)
            
            ttk.Button(button_frame, text="Отмена", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить задачу для редактирования: {str(e)}")
    
    def update_task(self, task_id, title, description, deadline, priority, status, dialog):
        try:
            supabase_client.table("Task").update({
                "title": title,
                "description": description,
                "deadline": deadline,
                "priority": priority,
                "status": status
            }).eq("id", task_id).execute()
            
            self.load_data()
            dialog.destroy()
            messagebox.showinfo("Успех", "Задача успешно обновлена")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить задачу: {str(e)}")
    
    def delete_task(self):
        selected_item = self.tasks_tree.focus()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите задачу для удаления")
            return
        
        task_id = self.tasks_tree.item(selected_item)["values"][0]
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту задачу?"):
            try:
                supabase_client.table("Task").delete().eq("id", task_id).execute()
                self.load_data()
                messagebox.showinfo("Успех", "Задача успешно удалена")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить задачу: {str(e)}")
    
    def show_add_user_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить пользователя")
        dialog.geometry("400x200")
        
        ttk.Label(dialog, text="Имя:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Email:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        email_entry = ttk.Entry(dialog, width=30)
        email_entry.grid(row=1, column=1, padx=10, pady=5)
        
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Добавить", 
                  command=lambda: self.add_user(
                      name_entry.get(),
                      email_entry.get(),
                      dialog
                  )).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Отмена", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def add_user(self, name, email, dialog):
        if not name or not email:
            messagebox.showerror("Ошибка", "Имя и email обязательны")
            return
        
        try:
            supabase_client.table("User").insert({
                "name": name,
                "email": email
            }).execute()
            
            self.load_users()
            dialog.destroy()
            messagebox.showinfo("Успех", "Пользователь успешно добавлен")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить пользователя: {str(e)}")
    
    def edit_user(self):
        selected_item = self.users_tree.focus()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для редактирования")
            return
        
        user_id = self.users_tree.item(selected_item)["values"][0]
        name = self.users_tree.item(selected_item)["values"][1]
        email = self.users_tree.item(selected_item)["values"][2]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Редактировать пользователя")
        dialog.geometry("400x200")
        
        ttk.Label(dialog, text="Имя:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.grid(row=0, column=1, padx=10, pady=5)
        name_entry.insert(0, name)
        
        ttk.Label(dialog, text="Email:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        email_entry = ttk.Entry(dialog, width=30)
        email_entry.grid(row=1, column=1, padx=10, pady=5)
        email_entry.insert(0, email)
        
        # Кнопки
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Сохранить", 
                  command=lambda: self.update_user(
                      user_id,
                      name_entry.get(),
                      email_entry.get(),
                      dialog
                  )).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Отмена", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def update_user(self, user_id, name, email, dialog):
        try:
            supabase_client.table("User").update({
                "name": name,
                "email": email
            }).eq("id", user_id).execute()
            
            self.load_users()
            dialog.destroy()
            messagebox.showinfo("Успех", "Пользователь успешно обновлен")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить пользователя: {str(e)}")
    
    def delete_user(self):
        selected_item = self.users_tree.focus()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для удаления")
            return
        
        user_id = self.users_tree.item(selected_item)["values"][0]
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этого пользователя?"):
            try:
                supabase_client.table("User").delete().eq("id", user_id).execute()
                self.load_users()
                messagebox.showinfo("Успех", "Пользователь успешно удален")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить пользователя: {str(e)}")
    
    def check_notifications(self):
        try:
            notifications = supabase_client.table("Notification").select("*").eq("user_id", self.current_user["id"]).eq("is_read", False).execute().data
            
            for notification in notifications:
                messagebox.showinfo("Уведомление", notification["message"])
                
                supabase_client.table("Notification").update({"is_read": True}).eq("id", notification["id"]).execute()
                
        except Exception as e:
            print(f"Ошибка при проверке уведомлений: {e}")
        
        # повторяем проверку через 30 секунд
        self.root.after(30000, self.check_notifications)

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()