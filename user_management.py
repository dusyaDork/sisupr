import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Optional

class UserManager:
    def __init__(self, supabase_client):
        self.supabase = supabase_client
    
    def create_user(self, name: str, email: str, is_admin: bool = False) -> Optional[Dict]:
        """Создание нового пользователя"""
        try:
            user_data = {
                'name': name,
                'email': email,
                'is_admin': is_admin
            }
            response = self.supabase.table('User').insert(user_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Ошибка при создании пользователя: {e}")
            return None
    
    def get_users(self) -> List[Dict]:
        """Получение всех пользователей"""
        try:
            response = self.supabase.table('User').select('*').execute()
            return response.data
        except Exception as e:
            print(f"Ошибка при получении пользователей: {e}")
            return []
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Получение пользователя по ID"""
        try:
            response = self.supabase.table('User').select('*').eq('id', user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Ошибка при получении пользователя: {e}")
            return None
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """Обновление данных пользователя"""
        try:
            response = self.supabase.table('User').update(kwargs).eq('id', user_id).execute()
            return len(response.data) > 0
        except Exception as e:
            print(f"Ошибка при обновлении пользователя: {e}")
            return False
    
    def delete_user(self, user_id: int) -> bool:
        """Удаление пользователя"""
        try:
            response = self.supabase.table('User').delete().eq('id', user_id).execute()
            return len(response.data) > 0
        except Exception as e:
            print(f"Ошибка при удалении пользователя: {e}")
            return False
    
    def create_ui(self, parent):
        """Создание интерфейса управления пользователями"""
        self.tree = ttk.Treeview(parent, columns=('ID', 'Name', 'Email', 'Admin'), show='headings')
        self.tree.heading('ID', text='ID')
        self.tree.heading('Name', text='Имя')
        self.tree.heading('Email', text='Email')
        self.tree.heading('Admin', text='Админ')
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Кнопки управления
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Добавить", command=self.add_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Редактировать", command=self.edit_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Удалить", command=self.delete_selected_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Обновить", command=self.refresh_users).pack(side=tk.RIGHT, padx=5)
        
        self.refresh_users()
    
    def refresh_users(self):
        """Обновление списка пользователей"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        users = self.get_users()
        for user in users:
            self.tree.insert('', tk.END, values=(
                user['id'],
                user['name'],
                user['email'],
                'Да' if user.get('is_admin', False) else 'Нет'
            ))
    
    def add_user(self):
        """Добавление нового пользователя"""
        dialog = tk.Toplevel()
        dialog.title("Добавить пользователя")
        
        ttk.Label(dialog, text="Имя:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        name_entry = ttk.Entry(dialog)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Email:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        email_entry = ttk.Entry(dialog)
        email_entry.grid(row=1, column=1, padx=5, pady=5)
        
        admin_var = tk.BooleanVar()
        ttk.Checkbutton(dialog, text="Администратор", variable=admin_var).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        def save():
            name = name_entry.get()
            email = email_entry.get()
            if name and email:
                self.create_user(name, email, admin_var.get())
                self.refresh_users()
                dialog.destroy()
        
        ttk.Button(dialog, text="Сохранить", command=save).grid(row=3, column=1, padx=5, pady=5, sticky=tk.E)
    
    def edit_user(self):
        """Редактирование пользователя"""
        selected = self.tree.selection()
        if not selected:
            return
        
        user_id = self.tree.item(selected[0], 'values')[0]
        user = self.get_user(int(user_id))
        if not user:
            return
        
        dialog = tk.Toplevel()
        dialog.title("Редактировать пользователя")
        
        ttk.Label(dialog, text="Имя:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        name_entry = ttk.Entry(dialog)
        name_entry.insert(0, user['name'])
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Email:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        email_entry = ttk.Entry(dialog)
        email_entry.insert(0, user['email'])
        email_entry.grid(row=1, column=1, padx=5, pady=5)
        
        admin_var = tk.BooleanVar(value=user.get('is_admin', False))
        ttk.Checkbutton(dialog, text="Администратор", variable=admin_var).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        def save():
            name = name_entry.get()
            email = email_entry.get()
            if name and email:
                self.update_user(user['id'], name=name, email=email, is_admin=admin_var.get())
                self.refresh_users()
                dialog.destroy()
        
        ttk.Button(dialog, text="Сохранить", command=save).grid(row=3, column=1, padx=5, pady=5, sticky=tk.E)
    
    def delete_selected_user(self):
        """Удаление выбранного пользователя"""
        selected = self.tree.selection()
        if not selected:
            return
        
        user_id = self.tree.item(selected[0], 'values')[0]
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этого пользователя?"):
            self.delete_user(int(user_id))
            self.refresh_users()