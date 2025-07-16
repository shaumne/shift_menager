import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from datetime import datetime, date, timedelta
import calendar

from database.db_manager import DatabaseManager

class CalendarViewFrame(ctk.CTkFrame):
    def __init__(self, parent, db_manager: DatabaseManager, main_app):
        super().__init__(parent)
        
        self.db_manager = db_manager
        self.main_app = main_app
        self.colors = main_app.colors
        
        # Current date for calendar navigation
        self.current_date = date.today()
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.create_ui()
    
    def create_ui(self):
        """Create calendar view interface"""
        # Create header with navigation
        self.create_header()
        
        # Create calendar grid
        self.create_calendar()
        
        # Create side panel for shift details
        self.create_side_panel()
    
    def create_header(self):
        """Create calendar header with navigation"""
        header_frame = ctk.CTkFrame(self, height=80, fg_color=self.colors['primary'])
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Previous month button
        self.prev_btn = ctk.CTkButton(
            header_frame,
            text="◀ Previous",
            command=self.previous_month,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="transparent",
            text_color="white",
            hover_color="rgba(255,255,255,0.1)",
            width=100
        )
        self.prev_btn.grid(row=0, column=0, padx=20, pady=20)
        
        # Current month/year label
        self.month_label = ctk.CTkLabel(
            header_frame,
            text=self.get_month_year_text(),
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        self.month_label.grid(row=0, column=1, pady=20)
        
        # Next month button
        self.next_btn = ctk.CTkButton(
            header_frame,
            text="Next ▶",
            command=self.next_month,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="transparent",
            text_color="white",
            hover_color="rgba(255,255,255,0.1)",
            width=100
        )
        self.next_btn.grid(row=0, column=2, padx=20, pady=20)
        
        # Today button
        self.today_btn = ctk.CTkButton(
            header_frame,
            text="📅 Today",
            command=self.go_to_today,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.colors['secondary'],
            text_color="white",
            width=80,
            height=30
        )
        self.today_btn.grid(row=0, column=3, padx=(0, 20), pady=20)
    
    def create_calendar(self):
        """Create calendar grid"""
        # Main content frame
        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        content_frame.grid_columnconfigure(0, weight=2)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)
        
        # Calendar frame
        self.calendar_frame = ctk.CTkFrame(content_frame)
        self.calendar_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        
        # Configure calendar grid
        for i in range(7):  # 7 columns for days of week
            self.calendar_frame.grid_columnconfigure(i, weight=1, minsize=120)
        for i in range(7):  # 7 rows (header + 6 weeks)
            self.calendar_frame.grid_rowconfigure(i, weight=1, minsize=80)
        
        self.draw_calendar()
    
    def create_side_panel(self):
        """Create side panel for shift details and quick actions"""
        # Side panel
        side_panel = ctk.CTkFrame(self.calendar_frame.master)
        side_panel.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        side_panel.grid_rowconfigure(2, weight=1)
        
        # Selected date info
        date_info_frame = ctk.CTkFrame(side_panel)
        date_info_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=15)
        
        self.selected_date_label = ctk.CTkLabel(
            date_info_frame,
            text="Select a date",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['text_primary']
        )
        self.selected_date_label.pack(pady=15)
        
        # Quick stats
        stats_frame = ctk.CTkFrame(side_panel)
        stats_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        stats_title = ctk.CTkLabel(
            stats_frame,
            text="Quick Stats",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors['text_primary']
        )
        stats_title.pack(pady=(15, 10))
        
        # Sample stats
        stats_labels = [
            "Shifts This Month: 84",
            "Total Labor Hours: 672",
            "Average Daily Cost: $1,248",
            "Peak Coverage: 94%"
        ]
        
        for stat in stats_labels:
            stat_label = ctk.CTkLabel(
                stats_frame,
                text=stat,
                font=ctk.CTkFont(size=12),
                text_color=self.colors['text_secondary']
            )
            stat_label.pack(pady=2, anchor="w", padx=15)
        
        # Add some padding at bottom
        ctk.CTkLabel(stats_frame, text="").pack(pady=10)
        
        # Shift details frame
        details_frame = ctk.CTkFrame(side_panel)
        details_frame.grid(row=2, column=0, sticky="nsew", padx=15, pady=(0, 15))
        
        details_title = ctk.CTkLabel(
            details_frame,
            text="Shift Details",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors['text_primary']
        )
        details_title.pack(pady=(15, 10))
        
        # Placeholder for shift details
        self.shift_details_label = ctk.CTkLabel(
            details_frame,
            text="Select a date to view\nshift details",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_secondary'],
            justify="center"
        )
        self.shift_details_label.pack(pady=20)
        
        # Quick actions
        actions_frame = ctk.CTkFrame(side_panel)
        actions_frame.grid(row=3, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        actions_title = ctk.CTkLabel(
            actions_frame,
            text="Quick Actions",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors['text_primary']
        )
        actions_title.pack(pady=(15, 10))
        
        # Action buttons
        create_shift_btn = ctk.CTkButton(
            actions_frame,
            text="📅 Create Shift",
            command=self.create_shift,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.colors['success'],
            height=35
        )
        create_shift_btn.pack(pady=5, padx=15, fill="x")
        
        view_schedule_btn = ctk.CTkButton(
            actions_frame,
            text="📊 View Schedule",
            command=self.view_schedule,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.colors['primary'],
            height=35
        )
        view_schedule_btn.pack(pady=5, padx=15, fill="x")
        
        export_btn = ctk.CTkButton(
            actions_frame,
            text="📄 Export Month",
            command=self.export_month,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.colors['warning'],
            height=35
        )
        export_btn.pack(pady=(5, 15), padx=15, fill="x")
    
    def draw_calendar(self):
        """Draw the calendar grid"""
        # Clear existing calendar
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
        
        # Day of week headers
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for i, day in enumerate(days):
            header = ctk.CTkLabel(
                self.calendar_frame,
                text=day,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=self.colors['text_primary'],
                fg_color=self.colors['sidebar']
            )
            header.grid(row=0, column=i, sticky="nsew", padx=1, pady=1)
        
        # Get calendar data
        cal = calendar.monthcalendar(self.current_date.year, self.current_date.month)
        
        # Draw calendar days
        today = date.today()
        
        for week_num, week in enumerate(cal, 1):
            for day_num, day in enumerate(week):
                if day == 0:
                    # Empty cell for days not in current month
                    cell = ctk.CTkFrame(self.calendar_frame, fg_color="transparent")
                else:
                    # Create date for this cell
                    cell_date = date(self.current_date.year, self.current_date.month, day)
                    
                    # Determine cell color
                    if cell_date == today:
                        fg_color = self.colors['primary']
                        text_color = "white"
                    elif cell_date.weekday() >= 5:  # Weekend
                        fg_color = self.colors['sidebar']
                        text_color = self.colors['text_secondary']
                    else:
                        fg_color = self.colors['background']
                        text_color = self.colors['text_primary']
                    
                    # Create cell frame
                    cell = ctk.CTkFrame(
                        self.calendar_frame,
                        fg_color=fg_color,
                        border_width=1,
                        border_color=self.colors['text_secondary']
                    )
                    
                    # Day number
                    day_label = ctk.CTkLabel(
                        cell,
                        text=str(day),
                        font=ctk.CTkFont(size=16, weight="bold"),
                        text_color=text_color
                    )
                    day_label.pack(pady=(5, 0))
                    
                    # Sample shift indicators
                    if day % 3 == 0:  # Show shifts on every 3rd day
                        shift_indicator = ctk.CTkLabel(
                            cell,
                            text="🍟 3 shifts",
                            font=ctk.CTkFont(size=10),
                            text_color=self.colors['success'] if cell_date != today else "white"
                        )
                        shift_indicator.pack()
                    elif day % 5 == 0:  # Show different indicator on every 5th day
                        shift_indicator = ctk.CTkLabel(
                            cell,
                            text="⚠️ Understaffed",
                            font=ctk.CTkFont(size=10),
                            text_color=self.colors['danger'] if cell_date != today else "white"
                        )
                        shift_indicator.pack()
                    
                    # Bind click event
                    cell.bind("<Button-1>", lambda e, d=cell_date: self.on_date_click(d))
                    day_label.bind("<Button-1>", lambda e, d=cell_date: self.on_date_click(d))
                
                cell.grid(row=week_num, column=day_num, sticky="nsew", padx=1, pady=1)
    
    def get_month_year_text(self):
        """Get formatted month and year text"""
        return self.current_date.strftime("%B %Y")
    
    def previous_month(self):
        """Navigate to previous month"""
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month - 1)
        
        self.month_label.configure(text=self.get_month_year_text())
        self.draw_calendar()
        self.main_app.update_status(f"Viewing {self.get_month_year_text()}")
    
    def next_month(self):
        """Navigate to next month"""
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month + 1)
        
        self.month_label.configure(text=self.get_month_year_text())
        self.draw_calendar()
        self.main_app.update_status(f"Viewing {self.get_month_year_text()}")
    
    def go_to_today(self):
        """Navigate to current month"""
        self.current_date = date.today()
        self.month_label.configure(text=self.get_month_year_text())
        self.draw_calendar()
        self.main_app.update_status("Viewing current month")
    
    def on_date_click(self, selected_date):
        """Handle date click"""
        self.selected_date_label.configure(
            text=selected_date.strftime("%A, %B %d, %Y")
        )
        
        # Sample shift details for the selected date
        if selected_date.day % 3 == 0:
            shift_details = (
                "Morning Shift: 6:00 AM - 2:00 PM\n"
                "• Manager: Sarah Johnson\n"
                "• Cashiers: 3 scheduled\n"
                "• Kitchen: 4 scheduled\n"
                "• Drive-Thru: 2 scheduled\n\n"
                "Afternoon Shift: 11:00 AM - 7:00 PM\n"
                "• Supervisor: Michael Brown\n"
                "• Cashiers: 4 scheduled\n"
                "• Kitchen: 5 scheduled\n\n"
                "Evening Shift: 5:00 PM - 11:00 PM\n"
                "• Supervisor: Emily Davis\n"
                "• Cashiers: 2 scheduled\n"
                "• Kitchen: 3 scheduled"
            )
        elif selected_date.day % 5 == 0:
            shift_details = (
                "⚠️ UNDERSTAFFED ALERT\n\n"
                "Morning Shift: 6:00 AM - 2:00 PM\n"
                "• Manager: James Wilson\n"
                "• Cashiers: 2 scheduled (need 3)\n"
                "• Kitchen: 3 scheduled (need 4)\n\n"
                "Need to fill 2 positions!"
            )
        else:
            shift_details = (
                "No shifts scheduled for this date.\n\n"
                "Click 'Create Shift' to add\n"
                "a new shift for this day."
            )
        
        self.shift_details_label.configure(text=shift_details)
        self.main_app.update_status(f"Selected: {selected_date.strftime('%B %d, %Y')}")
    
    def create_shift(self):
        """Create new shift (placeholder)"""
        from tkinter import messagebox
        messagebox.showinfo(
            "Create Shift",
            "This feature will open the Shift Creator\nwith the selected date pre-filled.\n\n"
            "For now, please use the Shift Creator\nfrom the main navigation."
        )
    
    def view_schedule(self):
        """View detailed schedule (placeholder)"""
        from tkinter import messagebox
        messagebox.showinfo(
            "View Schedule",
            "This feature will show a detailed\nschedule view for the selected date.\n\n"
            "Coming soon in the next update!"
        )
    
    def export_month(self):
        """Export month schedule (placeholder)"""
        from tkinter import messagebox
        messagebox.showinfo(
            "Export Month",
            "This feature will export the entire\nmonth's schedule to PDF or Excel.\n\n"
            "Coming soon in the next update!"
        ) 