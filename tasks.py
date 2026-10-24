import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- Базовый класс (Инкапсуляция) ---
class FinancialGoal:
    def __init__(self, name, target_amount, current_amount, deadline):
        self.name = name
        self.target_amount = float(target_amount)
        self.current_amount = float(current_amount)
        self.deadline = deadline

    def get_progress(self):
        if self.target_amount <= 0:
            return 0.0
        return (self.current_amount / self.target_amount) * 100

    def get_status_str(self):
        return f"{self.get_progress():.1f}% достигнуто"

    def days_left(self):
        try:
            deadline_date = datetime.datetime.strptime(self.deadline, "%d.%m.%Y").date()
            today = datetime.date.today()
            return (deadline_date - today).days
        except ValueError:
            return 999

    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "name": self.name,
            "target_amount": self.target_amount,
            "current_amount": self.current_amount,
            "deadline": self.deadline
        }

# --- Дочерний класс (Наследование) ---
class UrgentGoal(FinancialGoal):
    # Переопределяем метод (Полиморфизм)
    def get_status_str(self):
        days = self.days_left()
        if days < 30 and self.get_progress() < 100:
            return f"{self.get_progress():.1f}% (СРОЧНО! Осталось {days} дн.)"
        return super().get_status_str()

# --- Менеджер данных ---
class GoalManager:
    def __init__(self, filename="goals_data.json"):
        self.filename = filename
        self.goals = []
        self.load_data()

    def add_goal(self, goal):
        self.goals.append(goal)
        self.save_data()

    def update_goal(self, index, new_current_amount):
        self.goals[index].current_amount = float(new_current_amount)
        self.save_data()

    def save_data(self):
        data = [goal.to_dict() for goal in self.goals]
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_data(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.goals = []
                for item in data:
                    if item.get("type") == "UrgentGoal":
                        goal = UrgentGoal(item['name'], item['target_amount'], item['current_amount'], item['deadline'])
                    else:
                        goal = FinancialGoal(item['name'], item['target_amount'], item['current_amount'], item['deadline'])
                    self.goals.append(goal)

    def sort_goals(self, by="progress"):
        if by == "progress":
            self.goals.sort(key=lambda x: x.get_progress(), reverse=True)
        elif by == "date":
            self.goals.sort(key=lambda x: datetime.datetime.strptime(x.deadline, "%d.%m.%Y").date() if x.deadline else datetime.date.max)

    def filter_urgent(self):
        return [g for g in self.goals if g.days_left() < 30]

# --- Главное окно приложения ---
class FinancialGoalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Калькулятор финансовых целей (Вариант 5)")
        self.geometry("950x650")
        
        self.manager = GoalManager()

        frame_input = tk.LabelFrame(self, text="Добавить новую цель", padx=10, pady=10)
        frame_input.pack(pady=10, fill="x", padx=10)

        tk.Label(frame_input, text="Название:").grid(row=0, column=0, sticky="w")
        self.entry_name = tk.Entry(frame_input)
        self.entry_name.grid(row=0, column=1, padx=5)

        tk.Label(frame_input, text="Цель (руб):").grid(row=0, column=2, sticky="w")
        self.entry_target = tk.Entry(frame_input)
        self.entry_target.grid(row=0, column=3, padx=5)

        tk.Label(frame_input, text="Накоплено (руб):").grid(row=0, column=4, sticky="w")
        self.entry_current = tk.Entry(frame_input)
        self.entry_current.grid(row=0, column=5, padx=5)

        tk.Label(frame_input, text="Дедлайн (ДД.ММ.ГГГГ):").grid(row=0, column=6, sticky="w")
        self.entry_deadline = tk.Entry(frame_input)
        self.entry_deadline.grid(row=0, column=7, padx=5)

        btn_add = tk.Button(frame_input, text="Добавить цель", command=self.add_goal, bg="lightgreen")
        btn_add.grid(row=0, column=8, padx=10)

        frame_table = tk.Frame(self)
        frame_table.pack(fill="both", expand=True, padx=10)

        columns = ("name", "target", "current", "deadline", "status")
        self.tree = ttk.Treeview(frame_table, columns=columns, show="headings")
        self.tree.heading("name", text="Название")
        self.tree.heading("target", text="Цель (руб)")
        self.tree.heading("current", text="Накоплено (руб)")
        self.tree.heading("deadline", text="Дедлайн")
        self.tree.heading("status", text="Статус")

        self.tree.column("name", width=150)
        self.tree.column("target", width=100, anchor="e")
        self.tree.column("current", width=100, anchor="e")
        self.tree.column("deadline", width=100, anchor="center")
        self.tree.column("status", width=200, anchor="w")
        
        self.tree.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        frame_buttons = tk.Frame(self)
        frame_buttons.pack(pady=10)

        btn_update = tk.Button(frame_buttons, text="Обновить прогресс", command=self.update_progress, bg="lightblue")
        btn_update.pack(side="left", padx=5)

        btn_sort_prog = tk.Button(frame_buttons, text="Сортировать по статусу", command=lambda: self.sort_data("progress"))
        btn_sort_prog.pack(side="left", padx=5)

        btn_sort_date = tk.Button(frame_buttons, text="Сортировать по дате", command=lambda: self.sort_data("date"))
        btn_sort_date.pack(side="left", padx=5)

        btn_filter = tk.Button(frame_buttons, text="Показать срочные (<30 дней)", command=self.filter_data, bg="orange")
        btn_filter.pack(side="left", padx=5)

        btn_show_all = tk.Button(frame_buttons, text="Показать все", command=self.refresh_tree)
        btn_show_all.pack(side="left", padx=5)

        btn_chart = tk.Button(frame_buttons, text="График (Прогресс-бары)", command=self.show_chart, bg="lightyellow")
        btn_chart.pack(side="left", padx=5)

        self.refresh_tree()

    def add_goal(self):
        name = self.entry_name.get()
        target = self.entry_target.get()
        current = self.entry_current.get()
        deadline = self.entry_deadline.get()

        if not name or not target or not current or not deadline:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return

        try:
            target_f = float(target)
            current_f = float(current)
            datetime.datetime.strptime(deadline, "%d.%m.%Y") 
        except ValueError:
            messagebox.showerror("Ошибка", "Проверьте правильность ввода сумм или даты (ДД.ММ.ГГГГ)!")
            return

        days = (datetime.datetime.strptime(deadline, "%d.%m.%Y").date() - datetime.date.today()).days
        if days < 30:
            goal = UrgentGoal(name, target_f, current_f, deadline)
        else:
            goal = FinancialGoal(name, target_f, current_f, deadline)

        self.manager.add_goal(goal)
        self.refresh_tree()
        
        self.entry_name.delete(0, tk.END)
        self.entry_target.delete(0, tk.END)
        self.entry_current.delete(0, tk.END)
        self.entry_deadline.delete(0, tk.END)

    def refresh_tree(self, goals_to_show=None):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        goals = goals_to_show if goals_to_show is not None else self.manager.goals
        for goal in goals:
            self.tree.insert("", "end", values=(
                goal.name, 
                f"{goal.target_amount:.2f}", 
                f"{goal.current_amount:.2f}", 
                goal.deadline, 
                goal.get_status_str()
            ))

    def update_progress(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите цель из списка для обновления!")
            return
        
        item = self.tree.item(selected[0])
        goal_name = item['values'][0]
        
        goal_index = next((i for i, g in enumerate(self.manager.goals) if g.name == goal_name), None)
        
        if goal_index is not None:
            current_val = self.manager.goals[goal_index].current_amount
            new_val = simpledialog.askfloat("Обновление", f"Введите новую накопленную сумму для '{goal_name}':", initialvalue=current_val)
            if new_val is not None:
                self.manager.update_goal(goal_index, new_val)
                self.refresh_tree()

    def sort_data(self, by):
        self.manager.sort_goals(by)
        self.refresh_tree()

    def filter_data(self):
        filtered = self.manager.filter_urgent()
        self.refresh_tree(filtered)

    def show_chart(self):
        if not self.manager.goals:
            messagebox.showinfo("График", "Нет данных для отображения.")
            return

        names = [g.name for g in self.manager.goals]
        targets = [g.target_amount for g in self.manager.goals]
        currents = [g.current_amount for g in self.manager.goals]

        chart_window = tk.Toplevel(self)
        chart_window.title("Графическое представление целей")
        chart_window.geometry("800x500")

        fig, ax = plt.subplots(figsize=(8, 4))
        
        x = range(len(names))
        ax.bar([i - 0.2 for i in x], targets, width=0.4, label='Цель', color='lightgray')
        ax.bar([i + 0.2 for i in x], currents, width=0.4, label='Накоплено', color='green')

        ax.set_ylabel('Сумма (руб)')
        ax.set_title('Прогресс по финансовым целям')
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=15)
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=chart_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

if __name__ == "__main__":
    app = FinancialGoalApp()
    app.mainloop()