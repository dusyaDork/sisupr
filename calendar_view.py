import tkinter as tk
from tkinter import ttk, messagebox
import calendar
import datetime
from dateutil.relativedelta import relativedelta

class CalendarView:
    def __init__(self, parent, task_manager):
        self.parent = parent
        self.task_manager = task_manager
        self.current_date = datetime.date.today()
        
        self.create_widgets()
        self.update_calendar()
    
    def create_widgets(self):
        # Панель управления
        control_frame = ttk.Frame(self.parent)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.month_year_label = ttk.Label(control_frame, text="", font=('Arial', 10, 'bold'))
        self.month_year_label.pack(side=tk.LEFT)
        
        ttk.Button(control_frame, text="<", command=self.prev_month).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Сегодня", command=self.show_today).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text=">", command=self.next_month).pack(side=tk.LEFT, padx=5)
        
        # Календарь
        self.calendar_frame = ttk.Frame(self.parent)
        self.calendar_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Создаем заголовки дней недели
        days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        for i, day in enumerate(days):
            ttk.Label(self.calendar_frame, text=day, width=10, relief="ridge").grid(row=0, column=i, sticky="nsew")
        
        # Создаем ячейки календаря
        self.cells = []
        for row in range(6):
            row_cells = []
            for col in range(7):
                cell = ttk.Frame(self.calendar_frame, width=100, height=80, relief="solid", borderwidth=1)
                cell.grid(row=row+1, column=col, sticky="nsew")
                cell.grid_propagate(False)
                
                # Метка для числа
                day_label = ttk.Label(cell, font=('Arial', 8))
                day_label.pack(anchor=tk.NW)
                
                # Фрейм для задач
                tasks_frame = ttk.Frame(cell)
                tasks_frame.pack(fill=tk.BOTH, expand=True)
                
                row_cells.append({
                    'frame': cell,
                    'day_label': day_label,
                    'tasks_frame': tasks_frame
                })
            self.cells.append(row_cells)
        
        # Настройка веса строк и столбцов
        for i in range(7):
            self.calendar_frame.columnconfigure(i, weight=1)
        for i in range(1, 7):
            self.calendar_frame.rowconfigure(i, weight=1)
    
    def update_calendar(self):
        """Обновление календаря"""
        # Обновляем заголовок
        month_name = self.current_date.strftime("%B %Y")
        self.month_year_label.config(text=month_name)
        
        # Получаем задачи для текущего месяца
        start_date = datetime.date(self.current_date.year, self.current_date.month, 1)
        end_date = start_date + relativedelta(months=1)
        tasks = self.get_tasks_for_period(start_date, end_date)
        
        # Очищаем ячейки
        for row in self.cells:
            for cell in row:
                cell['day_label'].config(text="")
                for widget in cell['tasks_frame'].winfo_children():
                    widget.destroy()
        
        # Получаем календарь на текущий месяц
        cal = calendar.monthcalendar(self.current_date.year, self.current_date.month)
        
        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day == 0:
                    continue  # День другого месяца
                
                cell = self.cells[week_num][day_num]
                cell['day_label'].config(text=str(day))
                
                # Проверяем задачи на этот день
                current_date = datetime.date(self.current_date.year, self.current_date.month, day)
                day_tasks = [t for t in tasks if t['deadline'][:10] == current_date.isoformat()]
                
                for task in day_tasks:
                    task_label = ttk.Label(
                        cell['tasks_frame'], 
                        text=task['title'], 
                        foreground="red" if task['priority'] == "Высокий" else "black",
                        wraplength=80
                    )
                    task_label.pack(fill=tk.X)
                    task_label.bind("<Button-1>", lambda e, t=task: self.show_task_details(t))
    
    def get_tasks_for_period(self, start_date, end_date):
        """Получение задач за период"""
        all_tasks = self.task_manager.get_all_tasks()
        period_tasks = []
        
        for task in all_tasks:
            try:
                task_date = datetime.datetime.strptime(task['deadline'][:10], "%Y-%m-%d").date()
                if start_date <= task_date < end_date:
                    period_tasks.append(task)
            except:
                continue
        
        return period_tasks
    
    def prev_month(self):
        """Переход к предыдущему месяцу"""
        self.current_date = self.current_date - relativedelta(months=1)
        self.update_calendar()
    
    def next_month(self):
        """Переход к следующему месяцу"""
        self.current_date = self.current_date + relativedelta(months=1)
        self.update_calendar()
    
    def show_today(self):
        """Переход к текущему месяцу"""
        self.current_date = datetime.date.today()
        self.update_calendar()
    
    def show_task_details(self, task):
        """Показать детали задачи"""
        dialog = tk.Toplevel()
        dialog.title(task['title'])
        
        ttk.Label(dialog, text=f"Название: {task['title']}").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(dialog, text=f"Статус: {task['status']}").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(dialog, text=f"Приоритет: {task['priority']}").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(dialog, text=f"Дедлайн: {task['deadline'][:10]}").pack(anchor=tk.W, padx=5, pady=2)
        
        desc_frame = ttk.LabelFrame(dialog, text="Описание")
        desc_frame.pack(fill=tk.X, padx=5, pady=5)
        
        desc_text = tk.Text(desc_frame, height=5, wrap=tk.WORD)
        desc_text.insert(tk.END, task['description'])
        desc_text.config(state=tk.DISABLED)
        desc_text.pack(fill=tk.X, padx=5, pady=5)