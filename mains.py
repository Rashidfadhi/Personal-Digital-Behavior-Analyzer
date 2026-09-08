import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import csv
import os
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# SETTINGS
# ============================================================

JSON_FILE = "activity.json"
DATE_FORMAT = "%Y-%m-%d"

BG = "#F4F7FB"
CARD = "#FFFFFF"
PRIMARY = "#2563EB"
PRIMARY_DARK = "#1D4ED8"
PRIMARY_LIGHT = "#DBEAFE"
TEXT = "#172033"
MUTED = "#64748B"
BORDER = "#DCE4EF"
DANGER = "#DC2626"
TABLE_HEADER = "#EFF6FF"
FONT = "Roboto"

CATEGORIES = [
    "outdoor", "entertainment", "study",
    "work", "exercise", "other"
]


# ============================================================
# UI HELPERS
# ============================================================

def card(parent, **kwargs):
    return tk.Frame(
        parent, bg=CARD,
        highlightbackground=BORDER,
        highlightthickness=1, **kwargs
    )


def label(parent, text="", size=10, bold=False, color=TEXT, **kwargs):
    return tk.Label(
        parent, text=text,
        font=(FONT, size, "bold" if bold else "normal"),
        bg=CARD, fg=color, **kwargs
    )


def button(parent, text, command, bg=PRIMARY, width=12):
    return tk.Button(
        parent, text=text, command=command,
        font=(FONT, 10, "bold"),
        bg=bg, fg="white",
        activebackground=PRIMARY_DARK,
        activeforeground="white",
        relief="flat", bd=0,
        cursor="hand2",
        padx=10, pady=7, width=width
    )


# ============================================================
# ACTIVITY
# ============================================================

class Activity:

    def __init__(self, name, category, duration, date=None):
        self.name = name
        self.category = category
        self.duration = float(duration)
        self.date = date or datetime.now().strftime(DATE_FORMAT)

    def to_dict(self):
        return {
            "name": self.name,
            "category": self.category,
            "duration": self.duration,
            "date": self.date
        }


# ============================================================
# DATA MANAGER
# ============================================================

class DataManager:

    @staticmethod
    def save(activities):
        try:
            with open(JSON_FILE, "w", encoding="utf-8") as file:
                json.dump([a.to_dict() for a in activities], file, indent=4)
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    @staticmethod
    def load():
        if not os.path.exists(JSON_FILE):
            return []

        try:
            with open(JSON_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            activities = []

            for item in data:
                category = str(
                    item.get("category", "other")
                ).lower().strip()

                if category == "productivity":
                    category = "outdoor"

                activities.append(
                    Activity(
                        item.get("name", "Unknown"),
                        category,
                        item.get("duration", 0),
                        item.get("date")
                    )
                )

            return activities

        except Exception as e:
            messagebox.showerror("Load Error", str(e))
            return []

    @staticmethod
    def import_csv(path):
        activities = []

        try:
            with open(path, "r", encoding="utf-8-sig") as file:
                for row in csv.DictReader(file):

                    name = row.get("name", "").strip()
                    category = row.get("category", "other").strip().lower()
                    duration = row.get("duration", "0").strip()
                    date = row.get("date", "").strip()

                    if not name:
                        continue

                    if category == "productivity":
                        category = "outdoor"

                    try:
                        duration = float(duration)
                    except ValueError:
                        continue

                    activities.append(
                        Activity(
                            name,
                            category,
                            duration,
                            date or datetime.now().strftime(DATE_FORMAT)
                        )
                    )

            return activities

        except Exception as e:
            messagebox.showerror("Import Error", str(e))
            return []

    @staticmethod
    def export_csv(activities, path):
        try:
            with open(
                path, "w",
                newline="",
                encoding="utf-8"
            ) as file:

                fields = ["name", "category", "duration", "date"]
                writer = csv.DictWriter(file, fieldnames=fields)

                writer.writeheader()

                for activity in activities:
                    writer.writerow(activity.to_dict())

            return True

        except Exception as e:
            messagebox.showerror("Export Error", str(e))
            return False


# ============================================================
# ACTIVITY MANAGER
# ============================================================

class ActivityManager:

    def __init__(self, activities):
        self.activities = activities

    def add(self, activity):
        self.activities.append(activity)
        DataManager.save(self.activities)

    def delete(self, index):
        if 0 <= index < len(self.activities):
            del self.activities[index]
            DataManager.save(self.activities)

    def clear(self):
        self.activities.clear()
        DataManager.save(self.activities)


# ============================================================
# DATA ANALYZER
# ============================================================

class DataAnalyzer:

    def __init__(self, activities):
        self.activities = activities

    def total_time(self):
        return sum(a.duration for a in self.activities)

    def average_session(self):
        return self.total_time() / len(self.activities) if self.activities else 0

    def longest_session(self):
        return max(
            (a.duration for a in self.activities),
            default=0
        )

    def active_days(self):
        return len({a.date for a in self.activities})

    def most_active_day(self):
        daily = self.daily_data()
        return max(daily, key=daily.get) if daily else "N/A"

    def category_time(self):
        result = {}

        for a in self.activities:
            category = "outdoor" if a.category == "productivity" else a.category
            result[category] = result.get(category, 0) + a.duration

        return result

    def top_category(self):
        data = self.category_time()
        return max(data, key=data.get) if data else "N/A"

    def daily_data(self):
        result = {}

        for a in self.activities:
            result[a.date] = result.get(a.date, 0) + a.duration

        return dict(sorted(result.items()))

    def long_sessions(self):
        average = self.average_session()
        return [a for a in self.activities if a.duration > average]

    def consistency(self):
        return min(self.active_days() / 30 * 100, 100)

    def dataframe(self):
        df = pd.DataFrame([a.to_dict() for a in self.activities])

        if df.empty:
            return pd.DataFrame(
                columns=["name", "category", "duration", "date"]
            )

        df["duration"] = pd.to_numeric(
            df["duration"], errors="coerce"
        ).fillna(0)

        df["date"] = pd.to_datetime(
            df["date"], errors="coerce"
        )

        return df

    def statistics(self):
        return {
            "Activities": len(self.activities),
            "Total Time": self.total_time(),
            "Average": self.average_session(),
            "Longest": self.longest_session(),
            "Active Days": self.active_days()
        }

    def insights(self):
        if not self.activities:
            return ["Add activities to generate insights."]

        return [
            f"Recorded {self.total_time():.0f} minutes of activity.",
            f"Average session: {self.average_session():.1f} minutes.",
            f"Longest session: {self.longest_session():.0f} minutes.",
            f"Top category: {self.top_category().title()}.",
            f"{len(self.long_sessions())} session(s) above average."
        ]

    def patterns(self):
        if not self.activities:
            return ["No behavior patterns available yet."]

        return [
            "✓ Active across multiple days."
            if self.active_days() >= 7
            else "• Record more days to identify patterns.",

            "✓ You have some long sessions."
            if self.longest_session() >= 120
            else "• Most sessions are under two hours.",

            f"✓ {self.top_category().title()} is your dominant category."
        ]


# ============================================================
# VISUALIZER
# ============================================================

class Visualizer:

    def __init__(self, analyzer):
        self.analyzer = analyzer

    def check_data(self):
        if not self.analyzer.activities:
            messagebox.showinfo(
                "No Data",
                "Add activities before creating a chart."
            )
            return False
        return True

    def show_chart(self, chart_type):

        if not self.check_data():
            return

        if chart_type == "category":
            data = self.analyzer.category_time()

            plt.figure(figsize=(9, 5))
            plt.bar(data.keys(), data.values())
            plt.title("Time Spent by Category",
                      fontsize=16, fontweight="bold")
            plt.xlabel("Category")
            plt.ylabel("Minutes")
            plt.xticks(rotation=20)

        elif chart_type == "daily":
            data = self.analyzer.daily_data()

            plt.figure(figsize=(10, 5))
            plt.plot(
                list(data.keys()),
                list(data.values()),
                marker="o",
                linewidth=2
            )
            plt.title("Daily Activity Trend",
                      fontsize=16, fontweight="bold")
            plt.xlabel("Date")
            plt.ylabel("Minutes")
            plt.xticks(rotation=45)
            plt.grid(alpha=0.25)

        elif chart_type == "pie":
            data = self.analyzer.category_time()

            plt.figure(figsize=(8, 6))
            plt.pie(
                data.values(),
                labels=data.keys(),
                autopct="%1.1f%%",
                startangle=90
            )
            plt.title("Category Distribution",
                      fontsize=16, fontweight="bold")

        elif chart_type == "stats":
            stats = self.analyzer.statistics()

            plt.figure(figsize=(9, 5))
            plt.bar(
                stats.keys(),
                stats.values()
            )
            plt.title("Activity Statistics",
                      fontsize=16, fontweight="bold")
            plt.ylabel("Value")
            plt.xticks(rotation=20)

        plt.tight_layout()
        plt.show()

    def category_chart(self):
        self.show_chart("category")

    def daily_chart(self):
        self.show_chart("daily")

    def pie_chart(self):
        self.show_chart("pie")

    def statistics_chart(self):
        self.show_chart("stats")


# ============================================================
# APPLICATION
# ============================================================

class App:

    def __init__(self, window):

        self.window = window
        self.window.title("Personal Digital Behavior Analyzer")
        self.window.geometry("1250x850")
        self.window.minsize(1050, 700)
        self.window.configure(bg=BG)

        self.activities = DataManager.load()
        self.manager = ActivityManager(self.activities)
        self.analyzer = DataAnalyzer(self.activities)
        self.visualizer = Visualizer(self.analyzer)

        self.setup_style()
        self.build_ui()

        self.refresh_table()
        self.update_dashboard()

        self.activity_entry.focus()

    # ========================================================
    # STYLE
    # ========================================================

    def setup_style(self):

        style = ttk.Style()

        try:
            style.theme_use("clam")
        except:
            pass

        style.configure(
            "TEntry",
            fieldbackground="white",
            borderwidth=1,
            padding=7
        )

        style.configure(
            "TCombobox",
            fieldbackground="white",
            background="white",
            padding=6
        )

        style.configure(
            "Treeview",
            background="white",
            fieldbackground="white",
            foreground=TEXT,
            rowheight=34,
            font=(FONT, 10)
        )

        style.configure(
            "Treeview.Heading",
            background=TABLE_HEADER,
            foreground=TEXT,
            font=(FONT, 10, "bold")
        )

        style.map(
            "Treeview",
            background=[("selected", PRIMARY_LIGHT)],
            foreground=[("selected", TEXT)]
        )

    # ========================================================
    # BUILD UI
    # ========================================================

    def build_ui(self):

        self.build_header()
        self.build_dashboard()
        self.build_content()

        self.window.bind(
            "<Control-Return>",
            lambda e: self.add_activity()
        )

        self.window.bind(
            "<Delete>",
            lambda e: self.delete_activity()
        )

    # ========================================================
    # HEADER
    # ========================================================

    def build_header(self):

        header = tk.Frame(
            self.window,
            bg=PRIMARY,
            height=85
        )

        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Personal Digital Behavior Analyzer",
            font=(FONT, 22, "bold"),
            bg=PRIMARY,
            fg="white"
        ).pack(anchor="w", padx=28, pady=(15, 0))

        tk.Label(
            header,
            text="Track your time. Understand your habits.",
            font=(FONT, 10),
            bg=PRIMARY,
            fg=PRIMARY_LIGHT
        ).pack(anchor="w", padx=30)

    # ========================================================
    # DASHBOARD
    # ========================================================

    def build_dashboard(self):

        dashboard = tk.Frame(self.window, bg=BG)
        dashboard.pack(fill="x", padx=24, pady=20)

        self.card_values = {}

        cards = [
            ("TOTAL TIME", "0 min"),
            ("AVERAGE SESSION", "0 min"),
            ("TOP CATEGORY", "N/A"),
            ("ACTIVE DAYS", "0"),
            ("LONGEST SESSION", "0 min")
        ]

        for i, (title, value) in enumerate(cards):

            dashboard.grid_columnconfigure(i, weight=1)

            c = card(dashboard, height=105)
            c.grid(row=0, column=i, sticky="nsew", padx=6)
            c.grid_propagate(False)

            label(
                c, title,
                size=9,
                bold=True,
                color=MUTED
            ).pack(anchor="w", padx=15, pady=(15, 4))

            value_label = label(
                c,
                value,
                size=17,
                bold=True,
                color=PRIMARY
            )

            value_label.pack(anchor="w", padx=15)
            self.card_values[title] = value_label

    # ========================================================
    # MAIN CONTENT
    # ========================================================

    def build_content(self):

        content = tk.Frame(self.window, bg=BG)
        content.pack(
            fill="both",
            expand=True,
            padx=24,
            pady=(0, 24)
        )

        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(0, weight=1)

        left = card(content)
        left.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 12)
        )

        right = card(content, width=330)
        right.grid(row=0, column=1, sticky="ns")
        right.grid_propagate(False)

        self.build_input(left)
        self.build_actions(left)
        self.build_table(left)
        self.build_charts(left)
        self.build_right_panel(right)

    # ========================================================
    # INPUT
    # ========================================================

    def build_input(self, parent):

        frame = tk.Frame(parent, bg=CARD)
        frame.pack(fill="x", padx=18, pady=18)

        label(
            frame,
            "Add Activity",
            size=14,
            bold=True
        ).grid(
            row=0,
            column=0,
            columnspan=6,
            sticky="w",
            pady=(0, 12)
        )

        fields = [
            ("Activity", 24),
            ("Category", 16),
            ("Duration (min)", 13),
            ("Date", 14)
        ]

        for i, (text, width) in enumerate(fields):
            label(frame, text).grid(
                row=1,
                column=i,
                sticky="w"
            )

        self.activity_entry = ttk.Entry(frame, width=24)
        self.activity_entry.grid(
            row=2, column=0,
            padx=(0, 10), pady=5
        )

        self.category_combo = ttk.Combobox(
            frame,
            values=CATEGORIES,
            state="readonly",
            width=16
        )
        self.category_combo.set("outdoor")
        self.category_combo.grid(
            row=2, column=1,
            padx=(0, 10), pady=5
        )

        self.duration_entry = ttk.Entry(
            frame,
            width=13
        )
        self.duration_entry.grid(
            row=2, column=2,
            padx=(0, 10), pady=5
        )

        self.date_entry = ttk.Entry(
            frame,
            width=14
        )
        self.date_entry.insert(
            0,
            datetime.now().strftime(DATE_FORMAT)
        )
        self.date_entry.grid(
            row=2, column=3,
            padx=(0, 10), pady=5
        )

        button(
            frame,
            "＋ Add",
            self.add_activity,
            width=10
        ).grid(row=2, column=4, padx=5)

    # ========================================================
    # ACTIONS
    # ========================================================

    def build_actions(self, parent):

        frame = tk.Frame(parent, bg=CARD)
        frame.pack(fill="x", padx=18, pady=(0, 10))

        buttons = [
            ("Delete", self.delete_activity, DANGER, 10),
            ("Import CSV", self.import_csv, PRIMARY, 12),
            ("Export CSV", self.export_csv, PRIMARY, 12),
            ("Clear All", self.clear_all, DANGER, 10)
        ]

        for text, command, color, width in buttons:
            button(
                frame,
                text,
                command,
                bg=color,
                width=width
            ).pack(
                side="left",
                padx=7
            )

    # ========================================================
    # TABLE
    # ========================================================

    def build_table(self, parent):

        frame = tk.Frame(parent, bg=CARD)
        frame.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=10
        )

        columns = (
            "name",
            "category",
            "duration",
            "date"
        )

        self.table = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        headings = {
            "name": ("Activity", 220, "w"),
            "category": ("Category", 130, "w"),
            "duration": ("Duration", 100, "center"),
            "date": ("Date", 120, "center")
        }

        for column, (text, width, anchor) in headings.items():
            self.table.heading(column, text=text)
            self.table.column(
                column,
                width=width,
                anchor=anchor
            )

        scrollbar = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=self.table.yview
        )

        self.table.configure(
            yscrollcommand=scrollbar.set
        )

        self.table.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

    # ========================================================
    # CHARTS
    # ========================================================

    def build_charts(self, parent):

        frame = tk.Frame(parent, bg=CARD)
        frame.pack(
            fill="x",
            padx=18,
            pady=(5, 18)
        )

        label(
            frame,
            "Visual Analysis",
            size=12,
            bold=True
        ).pack(anchor="w", pady=(0, 8))

        charts = [
            ("Category Chart", self.visualizer.category_chart, 15),
            ("Daily Trend", self.visualizer.daily_chart, 13),
            ("Category Distribution", self.visualizer.pie_chart, 18),
            ("Statistics", self.visualizer.statistics_chart, 12)
        ]

        for text, command, width in charts:
            button(
                frame,
                text,
                command,
                width=width
            ).pack(side="left", padx=7)

    # ========================================================
    # RIGHT PANEL
    # ========================================================

    def build_right_panel(self, parent):

        search = tk.Frame(parent, bg=CARD)
        search.pack(fill="x", padx=16, pady=16)

        label(
            search,
            "Search Activities",
            size=12,
            bold=True
        ).pack(anchor="w", pady=(0, 7))

        self.search_entry = ttk.Entry(search)
        self.search_entry.pack(fill="x")

        self.search_entry.bind(
            "<KeyRelease>",
            self.search_activities
        )

        self.time_frame = self.analysis_card(
            parent,
            "⏱  Time Analysis"
        )

        self.category_frame = self.analysis_card(
            parent,
            "📊  Category Analysis"
        )

        self.insights_frame = self.analysis_card(
            parent,
            "🔎  Behavior Insights"
        )

        self.patterns_frame = self.analysis_card(
            parent,
            "🧠  Behavior Patterns"
        )

    # ========================================================
    # ANALYSIS CARD
    # ========================================================

    def analysis_card(self, parent, title):

        frame = tk.Frame(parent, bg=CARD)
        frame.pack(fill="x", padx=16, pady=7)

        label(
            frame,
            title,
            size=11,
            bold=True
        ).pack(anchor="w", pady=(0, 5))

        return frame

    def update_analysis(self, frame, items):

        for widget in frame.winfo_children()[1:]:
            widget.destroy()

        for item in items:
            label(
                frame,
                item,
                size=9,
                color=MUTED,
                justify="left",
                anchor="w",
                wraplength=290
            ).pack(
                fill="x",
                pady=2
            )

    # ========================================================
    # ADD
    # ========================================================

    def add_activity(self):

        name = self.activity_entry.get().strip()
        category = self.category_combo.get().strip().lower()
        duration = self.duration_entry.get().strip()
        date = self.date_entry.get().strip()

        if not name:
            messagebox.showwarning(
                "Missing Activity",
                "Please enter an activity name."
            )
            self.activity_entry.focus()
            return

        try:
            duration = float(duration)
            if duration <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Invalid Duration",
                "Duration must be a positive number."
            )
            self.duration_entry.focus()
            return

        try:
            datetime.strptime(date, DATE_FORMAT)
        except ValueError:
            messagebox.showwarning(
                "Invalid Date",
                "Date must use YYYY-MM-DD format."
            )
            self.date_entry.focus()
            return

        activity = Activity(
            name,
            category,
            duration,
            date
        )

        self.manager.add(activity)

        self.activity_entry.delete(0, tk.END)
        self.duration_entry.delete(0, tk.END)

        self.refresh_table()
        self.update_dashboard()

        self.activity_entry.focus()

    # ========================================================
    # DELETE
    # ========================================================

    def delete_activity(self):

        selected = self.table.selection()

        if not selected:
            messagebox.showinfo(
                "Delete Activity",
                "Please select an activity first."
            )
            return

        index = int(
            self.table.item(
                selected[0],
                "tags"
            )[0]
        )

        if messagebox.askyesno(
            "Delete Activity",
            "Are you sure you want to delete this activity?"
        ):
            self.manager.delete(index)
            self.refresh_table()
            self.update_dashboard()

    # ========================================================
    # CLEAR
    # ========================================================

    def clear_all(self):

        if not self.activities:
            messagebox.showinfo(
                "Clear All",
                "There are no activities to clear."
            )
            return

        if messagebox.askyesno(
            "Clear All Activities",
            "Are you sure you want to delete all activities?"
        ):
            self.manager.clear()
            self.refresh_table()
            self.update_dashboard()

    # ========================================================
    # IMPORT
    # ========================================================

    def import_csv(self):

        path = filedialog.askopenfilename(
            title="Import CSV",
            filetypes=[
                ("CSV Files", "*.csv"),
                ("All Files", "*.*")
            ]
        )

        if not path:
            return

        imported = DataManager.import_csv(path)

        if not imported:
            messagebox.showinfo(
                "Import",
                "No valid activities were found."
            )
            return

        self.activities.extend(imported)
        DataManager.save(self.activities)

        self.refresh_table()
        self.update_dashboard()

        messagebox.showinfo(
            "Import Complete",
            f"{len(imported)} activities imported successfully."
        )

    # ========================================================
    # EXPORT
    # ========================================================

    def export_csv(self):

        if not self.activities:
            messagebox.showinfo(
                "Export",
                "There are no activities to export."
            )
            return

        path = filedialog.asksaveasfilename(
            title="Export CSV",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")]
        )

        if path and DataManager.export_csv(
            self.activities,
            path
        ):
            messagebox.showinfo(
                "Export Complete",
                "Activities exported successfully."
            )

    # ========================================================
    # SEARCH
    # ========================================================

    def search_activities(self, event=None):

        search = self.search_entry.get().lower().strip()

        self.refresh_table(search)

    # ========================================================
    # TABLE
    # ========================================================

    def refresh_table(self, search=""):

        for item in self.table.get_children():
            self.table.delete(item)

        for index, activity in enumerate(self.activities):

            text = (
                f"{activity.name} "
                f"{activity.category} "
                f"{activity.date}"
            ).lower()

            if search and search not in text:
                continue

            category = (
                "outdoor"
                if activity.category == "productivity"
                else activity.category
            )

            self.table.insert(
                "",
                "end",
                values=(
                    activity.name,
                    category.title(),
                    f"{activity.duration:.0f} min",
                    activity.date
                ),
                tags=(str(index),)
            )

    # ========================================================
    # DASHBOARD
    # ========================================================

    def update_dashboard(self):

        self.analyzer = DataAnalyzer(self.activities)
        self.visualizer = Visualizer(self.analyzer)

        stats = {
            "TOTAL TIME":
                f"{self.analyzer.total_time():.0f} min",

            "AVERAGE SESSION":
                f"{self.analyzer.average_session():.1f} min",

            "TOP CATEGORY":
                self.analyzer.top_category().title()
                if self.analyzer.top_category() != "N/A"
                else "N/A",

            "ACTIVE DAYS":
                str(self.analyzer.active_days()),

            "LONGEST SESSION":
                f"{self.analyzer.longest_session():.0f} min"
        }

        for key, value in stats.items():
            self.card_values[key].config(text=value)

        self.update_right_panel()

    # ========================================================
    # RIGHT PANEL UPDATE
    # ========================================================

    def update_right_panel(self):

        analyzer = self.analyzer

        time_items = [
            f"Total: {analyzer.total_time():.0f} min",
            f"Average: {analyzer.average_session():.1f} min",
            f"Longest: {analyzer.longest_session():.0f} min",
            f"Active days: {analyzer.active_days()}",
            f"Most active day: {analyzer.most_active_day()}"
        ]

        category_data = analyzer.category_time()

        category_items = [
            f"{category.title()}: {minutes:.0f} min"
            for category, minutes in sorted(
                category_data.items(),
                key=lambda x: x[1],
                reverse=True
            )
        ] or ["No category data available."]

        self.update_analysis(
            self.time_frame,
            time_items
        )

        self.update_analysis(
            self.category_frame,
            category_items
        )

        self.update_analysis(
            self.insights_frame,
            analyzer.insights()
        )

        self.update_analysis(
            self.patterns_frame,
            analyzer.patterns()
        )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    window = tk.Tk()
    App(window)
    window.mainloop()