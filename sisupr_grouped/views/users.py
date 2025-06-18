import tkinter as tk
from tkinter import ttk, messagebox
from supabase_manager import supabase_client

class UsersView:
    def __init__(self, notebook, app):
        self.app = app
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text="Пользователи")
        self.setup_ui()
    
    def setup_ui(self):
        self.tree = ttk.Treeview(self.frame, columns=("id", "name", "email"), show="headings")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Имя")
        self.tree.heading("email", text="Email")
        
        self.tree.column("id", width=50)
        self.tree.column("name", width=150)
        self.tree.column("email", width=200)
        
        scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Добавить", command=self.show_add_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Редактировать", command=self.edit_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Удалить", command=self.delete_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Обновить", command=self.load_users).pack(side=tk.LEFT, padx=5)
    
    def load_users(self):
        try:
            users = supabase_client.table("User").select("*").execute().data
            self.tree.delete(*self.tree.get_children())
            
            for user in users:
                self.tree.insert("", tk.END, values=(
                    user["id"],
                    user["name"],
                    user["email"]
                ))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить пользователей: {str(e)}")
    
    def show_add_dialog(self):
        self.app.show_add_user_dialog()
    
    def edit_user(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для редактирования")
            return
        
        user_id = self.tree.item(selected_item)["values"][0]
        self.app.show_edit_user_dialog(user_id)
    
    def delete_user(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для удаления")
            return
        
        user_id = self.tree.item(selected_item)["values"][0]
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этого пользователя?"):
            try:
                supabase_client.table("User").delete().eq("id", user_id).execute()
                self.load_users()
                messagebox.showinfo("Успех", "Пользователь успешно удален")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить пользователя: {str(e)}")