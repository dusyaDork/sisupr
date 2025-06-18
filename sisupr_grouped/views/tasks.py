import tkinter as tk
from tkinter import ttk, messagebox
from supabase_manager import supabase_client, format_datetime

class TasksView:
    def __init__(self, notebook, app):
        self.app = app
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text="Все задачи")
        self.setup_ui()
    
    def setup_ui(self):
        self.tree = ttk.Treeview(self.frame, columns=("id", "title", "priority", "status", "deadline"), show="headings")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="Название")
        self.tree.heading("priority", text="Приоритет")
        self.tree.heading("status", text="Статус")
        self.tree.heading("deadline", text="Дедлайн")
        
        self.tree.column("id", width=50)
        self.tree.column("title", width=200)
        self.tree.column("priority", width=100)
        self.tree.column("status", width=100)
        self.tree.column("deadline", width=150)
        
        scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Добавить", command=self.app.show_add_task_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Редактировать", command=self.edit_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Удалить", command=self.delete_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Обновить", command=self.app.load_data).pack(side=tk.LEFT, padx=5)
        
        self.tree.bind("<Double-1>", lambda e: self.app.show_task_details())
    
    def update(self, tasks):
        self.tree.delete(*self.tree.get_children())
        for task in tasks:
            self.tree.insert("", tk.END, values=(
                task["id"],
                task["title"],
                task["priority"],
                task["status"],
                format_datetime(task["deadline"])
            ))
    
    def edit_task(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите задачу для редактирования")
            return
        
        task_id = self.tree.item(selected_item)["values"][0]
        self.app.show_edit_task_dialog(task_id)
    
    def delete_task(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите задачу для удаления")
            return
        
        task_id = self.tree.item(selected_item)["values"][0]
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту задачу?"):
            try:
                supabase_client.table("Task").delete().eq("id", task_id).execute()
                self.app.load_data()
                messagebox.showinfo("Успех", "Задача успешно удалена")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить задачу: {str(e)}")