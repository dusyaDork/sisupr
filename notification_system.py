import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Optional
import datetime

class NotificationSystem:
    def __init__(self, supabase_client):
        self.supabase = supabase_client
    
    def create_notification(self, user_id: int, message: str) -> Optional[Dict]:
        """Создание уведомления"""
        try:
            notification_data = {
                'user_id': user_id,
                'message': message
            }
            response = self.supabase.table('Notification').insert(notification_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Ошибка при создании уведомления: {e}")
            return None
    
    def get_unread_notifications(self, user_id: int) -> List[Dict]:
        """Получение непрочитанных уведомлений"""
        try:
            response = self.supabase.table('Notification').select('*').eq('user_id', user_id).eq('is_read', False).execute()
            return response.data
        except Exception as e:
            print(f"Ошибка при получении уведомлений: {e}")
            return []
    
    def mark_as_read(self, notification_id: int) -> bool:
        """Пометить уведомление как прочитанное"""
        try:
            response = self.supabase.table('Notification').update({'is_read': True}).eq('id', notification_id).execute()
            return len(response.data) > 0
        except Exception as e:
            print(f"Ошибка при обновлении уведомления: {e}")
            return False
    
    def check_deadlines(self):
        """Проверка приближающихся дедлайнов"""
        try:
            # Получаем задачи с дедлайнами в ближайшие 2 дня
            today = datetime.datetime.now().date()
            deadline = today + datetime.timedelta(days=2)
            
            response = self.supabase.table('Task').select('*, TaskAssignment(user_id)').lt('deadline', deadline.isoformat()).gt('deadline', today.isoformat()).execute()
            
            for task in response.data:
                for assignment in task['TaskAssignment']:
                    message = f"Приближается дедлайн задачи: {task['title']} ({task['deadline'][:10]})"
                    self.create_notification(assignment['user_id'], message)
        except Exception as e:
            print(f"Ошибка при проверке дедлайнов: {e}")