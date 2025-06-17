import tkinter as tk
from tkinter import ttk, messagebox
from tkinterdnd2 import TkinterDnD, DND_ALL
from PIL import Image, ImageTk
import datetime

class KanbanBoard:
    def __init__(self, parent, task_manager, user_manager):
        self.parent = parent
        self.task_manager = task_manager
        self.user_manager = user_manager
        
        self.create_widgets()
        self.load_tasks()
    
    def create_widgets(self):
        # Основной фрейм для колонок
        self.columns_frame = ttk.Frame(self.parent)
        self.columns_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Колонки Kanban
        self.columns = {
            'To Do': self.create_column('To Do', 'К выполнению'),
            'In Progress': self.create_column('In Progress', 'В работе'),
            'Done': self.create_column('Done', 'Выполнено')
        }
        
        # Кнопка добавления задачи
        add_button = ttk.Button(self.parent, text="Добавить задачу", command=self.add_task_dialog)
        add_button.pack(side=tk.BOTTOM, pady=10)
    
    def create_column(self, status, title):
        """Создание колонки Kanban"""
        column_frame = ttk.LabelFrame(self.columns_frame, text=title)
        column_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Canvas с Scrollbar для колонки
        canvas = tk.Canvas(column_frame)
        scrollbar = ttk.Scrollbar(column_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Сохраняем ссылки на элементы
        column = {
            'frame': column_frame,
            'canvas': canvas,
            'scrollable_frame': scrollable_frame,
            'tasks': {}
        }
        
        # Настройка перетаскивания (в реальном приложении нужно реализовать DnD)
        # Для простоты используем кнопки для изменения статуса
        
        return column
    
    def load_tasks(self):
        """Загрузка задач в Kanban доску"""
        for status, column in self.columns.items():
            # Очищаем колонку
            for widget in column['scrollable_frame'].winfo_children():
                widget.destroy()
            column['tasks'] = {}
            
            # Загружаем задачи для этого статуса
            tasks = self.task_manager.get_tasks_by_status(status)
            for task in tasks:
                self.add_task_to_column(task, status)
    
    def add_task_to_column(self, task, status):
        """Добавление задачи в колонку"""
        task_frame = ttk.Frame(self.columns[status]['scrollable_frame'], borderwidth=1, relief="solid", padding=5)
        task_frame.pack(fill=tk.X, pady=2, padx=2)
        
        # Отображение информации о задаче
        ttk.Label(task_frame, text=task['title'], font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        ttk.Label(task_frame, text=f"Приоритет: {task['priority']}").pack(anchor=tk.W)
        ttk.Label(task_frame, text=f"Дедлайн: {task['deadline'][:10]}").pack(anchor=tk.W)
        
        # Кнопки управления
        button_frame = ttk.Frame(task_frame)
        button_frame.pack(fill=tk.X, pady=2)
        
        # Кнопки для изменения статуса
        if status != 'To Do':
            ttk.Button(button_frame, text="←", 
                      command=lambda t=task: self.change_task_status(t['id'], 'To Do')).pack(side=tk.LEFT)
        
        if status != 'In Progress':
            ttk.Button(button_frame, text="→", 
                      command=lambda t=task: self.change_task_status(t['id'], 'In Progress')).pack(side=tk.LEFT)
        
        if status != 'Done':
            ttk.Button(button_frame, text="✓", 
                      command=lambda t=task: self.change_task_status(t['id'], 'Done')).pack(side=tk.LEFT)
        
        # Кнопка просмотра/редактирования
        ttk.Button(task_frame, text="Подробнее", 
                  command=lambda t=task: self.view_task_details(t)).pack(fill=tk.X)
        
        # Сохраняем ссылку на задачу
        self.columns[status]['tasks'][task['id']] = task_frame
    
    def change_task_status(self, task_id, new_status):
        """Изменение статуса задачи"""
        if self.task_manager.change_task_status(task_id, new_status):
            self.load_tasks()
    
    def add_task_dialog(self):
        """Диалог добавления новой задачи"""
        dialog = tk.Toplevel()
        dialog.title("Добавить задачу")
        
        ttk.Label(dialog, text="Название:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        title_entry = ttk.Entry(dialog, width=30)
        title_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Описание:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        desc_entry = tk.Text(dialog, width=30, height=5)
        desc_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Дедлайн:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        deadline_entry = ttk.Entry(dialog, width=30)
        deadline_entry.grid(row=2, column=1, padx=5, pady=5)
        deadline_entry.insert(0, (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%Y-%m-%d"))
        
        ttk.Label(dialog, text="Приоритет:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        priority_var = tk.StringVar(value="Средний")
        priority_menu = ttk.OptionMenu(dialog, priority_var, "Средний", "Высокий", "Средний", "Низкий")
        priority_menu.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        def save():
            title = title_entry.get()
            description = desc_entry.get("1.0", tk.END).strip()
            deadline = deadline_entry.get()
            
            if title and description and deadline:
                try:
                    deadline_dt = datetime.datetime.strptime(deadline, "%Y-%m-%d")
                    self.task_manager.create_task(title, description, deadline_dt, priority_var.get(), 1)  # 1 - ID текущего пользователя
                    self.load_tasks()
                    dialog.destroy()
                except ValueError:
                    messagebox.showerror("Ошибка", "Некорректный формат даты (используйте ГГГГ-ММ-ДД)")
        
        ttk.Button(dialog, text="Сохранить", command=save).grid(row=4, column=1, padx=5, pady=5, sticky=tk.E)
    
    def view_task_details(self, task):
        """Просмотр деталей задачи"""
        dialog = tk.Toplevel()
        dialog.title(task['title'])
        dialog.geometry("600x500")
        
        # Основной фрейм с прокруткой
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Информация о задаче
        ttk.Label(scrollable_frame, text=task['title'], font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=5)
        
        info_frame = ttk.LabelFrame(scrollable_frame, text="Информация о задаче")
        info_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(info_frame, text=f"Статус: {task['status']}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Приоритет: {task['priority']}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Дедлайн: {task['deadline'][:10]}").pack(anchor=tk.W)
        
        # Описание
        desc_frame = ttk.LabelFrame(scrollable_frame, text="Описание")
        desc_frame.pack(fill=tk.X, pady=5)
        
        desc_text = tk.Text(desc_frame, height=5, wrap=tk.WORD)
        desc_text.insert(tk.END, task['description'])
        desc_text.config(state=tk.DISABLED)
        desc_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Комментарии
        comments_frame = ttk.LabelFrame(scrollable_frame, text="Комментарии")
        comments_frame.pack(fill=tk.X, pady=5)
        
        comments = self.task_manager.get_task_comments(task['id'])
        for comment in comments:
            comment_frame = ttk.Frame(comments_frame, borderwidth=1, relief="solid", padding=5)
            comment_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(comment_frame, text=f"{comment['User']['name']}:", font=('Arial', 9, 'bold')).pack(anchor=tk.W)
            ttk.Label(comment_frame, text=comment['text'], wraplength=550).pack(anchor=tk.W)
        
        # Форма добавления комментария
        new_comment_frame = ttk.Frame(scrollable_frame)
        new_comment_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(new_comment_frame, text="Добавить комментарий:").pack(anchor=tk.W)
        new_comment_text = tk.Text(new_comment_frame, height=3, wrap=tk.WORD)
        new_comment_text.pack(fill=tk.X, padx=5, pady=5)
        
        def add_comment():
            text = new_comment_text.get("1.0", tk.END).strip()
            if text:
                self.task_manager.add_comment(task['id'], 1, text)  # 1 - ID текущего пользователя
                dialog.destroy()
                self.view_task_details(task)
        
        ttk.Button(new_comment_frame, text="Отправить", command=add_comment).pack(anchor=tk.E)