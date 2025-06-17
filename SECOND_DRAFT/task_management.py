import datetime
from typing import List, Dict, Optional

class TaskManager:
    def __init__(self, supabase_client):
        self.supabase = supabase_client
    
    def create_task(self, title: str, description: str, deadline: datetime.datetime, 
                   priority: str, creator_id: int) -> Optional[Dict]:
        """Создание новой задачи"""
        try:
            task_data = {
                'title': title,
                'description': description,
                'deadline': deadline.isoformat(),
                'priority': priority,
                'status': 'To Do'
            }
            response = self.supabase.table('Task').insert(task_data).execute()
            if response.data:
                task_id = response.data[0]['id']
                # Назначаем создателя задачи
                self.assign_task(task_id, creator_id)
                return response.data[0]
        except Exception as e:
            print(f"Ошибка при создании задачи: {e}")
        return None
    
    def update_task(self, task_id: int, **kwargs) -> bool:
        """Обновление задачи"""
        try:
            response = self.supabase.table('Task').update(kwargs).eq('id', task_id).execute()
            return len(response.data) > 0
        except Exception as e:
            print(f"Ошибка при обновлении задачи: {e}")
            return False
    
    def delete_task(self, task_id: int) -> bool:
        """Удаление задачи"""
        try:
            response = self.supabase.table('Task').delete().eq('id', task_id).execute()
            return len(response.data) > 0
        except Exception as e:
            print(f"Ошибка при удалении задачи: {e}")
            return False
    
    def get_task(self, task_id: int) -> Optional[Dict]:
        """Получение задачи по ID"""
        try:
            response = self.supabase.table('Task').select('*').eq('id', task_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Ошибка при получении задачи: {e}")
            return None
    
    def get_all_tasks(self) -> List[Dict]:
        """Получение всех задач"""
        try:
            response = self.supabase.table('Task').select('*').execute()
            return response.data
        except Exception as e:
            print(f"Ошибка при получении задач: {e}")
            return []
    
    def get_tasks_by_status(self, status: str) -> List[Dict]:
        """Получение задач по статусу"""
        try:
            response = self.supabase.table('Task').select('*').eq('status', status).execute()
            return response.data
        except Exception as e:
            print(f"Ошибка при получении задач по статусу: {e}")
            return []
    
    def assign_task(self, task_id: int, user_id: int) -> bool:
        """Назначение задачи пользователю"""
        try:
            assignment_data = {
                'task_id': task_id,
                'user_id': user_id
            }
            response = self.supabase.table('TaskAssignment').insert(assignment_data).execute()
            return len(response.data) > 0
        except Exception as e:
            print(f"Ошибка при назначении задачи: {e}")
            return False
    
    def get_task_assignees(self, task_id: int) -> List[Dict]:
        """Получение исполнителей задачи"""
        try:
            response = self.supabase.table('TaskAssignment').select('User(id, name)').eq('task_id', task_id).execute()
            return [item['User'] for item in response.data]
        except Exception as e:
            print(f"Ошибка при получении исполнителей задачи: {e}")
            return []
    
    def add_comment(self, task_id: int, user_id: int, text: str) -> Optional[Dict]:
        """Добавление комментария к задаче"""
        try:
            comment_data = {
                'task_id': task_id,
                'user_id': user_id,
                'text': text
            }
            response = self.supabase.table('Comment').insert(comment_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Ошибка при добавлении комментария: {e}")
            return None
    
    def get_task_comments(self, task_id: int) -> List[Dict]:
        """Получение комментариев задачи"""
        try:
            response = self.supabase.table('Comment').select('*, User(name)').eq('task_id', task_id).execute()
            return response.data
        except Exception as e:
            print(f"Ошибка при получении комментариев: {e}")
            return []
    
    def add_file(self, task_id: int, filename: str, path: str) -> Optional[Dict]:
        """Добавление файла к задаче"""
        try:
            file_data = {
                'task_id': task_id,
                'filename': filename,
                'path': path
            }
            response = self.supabase.table('File').insert(file_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Ошибка при добавлении файла: {e}")
            return None
    
    def get_task_files(self, task_id: int) -> List[Dict]:
        """Получение файлов задачи"""
        try:
            response = self.supabase.table('File').select('*').eq('task_id', task_id).execute()
            return response.data
        except Exception as e:
            print(f"Ошибка при получении файлов: {e}")
            return []
    
    def change_task_status(self, task_id: int, new_status: str) -> bool:
        """Изменение статуса задачи"""
        return self.update_task(task_id, status=new_status)