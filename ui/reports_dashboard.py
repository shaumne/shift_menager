import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
import threading
from typing import List, Dict, Any

from database.db_manager import DatabaseManager
from models.employee import Employee, EmploymentStatus, Position

class ReportsDashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, db_manager: DatabaseManager, main_app):
        super().__init__(parent)
        
        self.db_manager = db_manager
        self.main_app = main_app
        self.colors = main_app.colors
        self.employees: List[Employee] = []
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.create_ui()
        self.load_employee_data()
    
    def create_ui(self):
        """Create reports dashboard interface"""
        # Create main container with tabs
        self.tabview = ctk.CTkTabview(self, width=1000, height=700)
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Add tabs
        self.overview_tab = self.tabview.add("📊 Overview")
        self.labor_tab = self.tabview.add("💰 Labor Costs")
        self.performance_tab = self.tabview.add("📈 Performance")
        self.attendance_tab = self.tabview.add("⏰ Attendance")
        
        # Setup each tab
        self.setup_overview_tab()
        self.setup_labor_tab()
        self.setup_performance_tab()
        self.setup_attendance_tab()
    
    def setup_overview_tab(self):
        """Setup overview dashboard"""
        # Configure grid for overview tab
        self.overview_tab.grid_columnconfigure(1, weight=1)
        self.overview_tab.grid_rowconfigure(1, weight=1)
        
        # Key metrics frame
        metrics_frame = ctk.CTkFrame(self.overview_tab)
        metrics_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=20)
        metrics_frame.grid_columnconfigure(0, weight=1)
        metrics_frame.grid_columnconfigure(1, weight=1)
        metrics_frame.grid_columnconfigure(2, weight=1)
        metrics_frame.grid_columnconfigure(3, weight=1)
        
        # Key metric cards
        self.create_metric_card(metrics_frame, "Total Employees", "0", "👥", 0)
        self.create_metric_card(metrics_frame, "Active Staff", "0", "✅", 1)
        self.create_metric_card(metrics_frame, "Weekly Hours", "0", "⏰", 2)
        self.create_metric_card(metrics_frame, "Labor Cost", "$0", "💰", 3)
        
        # Charts area
        charts_frame = ctk.CTkFrame(self.overview_tab)
        charts_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=20, pady=(0, 20))
        charts_frame.grid_columnconfigure(0, weight=1)
        charts_frame.grid_columnconfigure(1, weight=1)
        charts_frame.grid_rowconfigure(0, weight=1)
        
        # Position distribution chart (text-based)
        self.create_position_chart(charts_frame)
        
        # Recent activity
        self.create_recent_activity(charts_frame)
    
    def create_metric_card(self, parent, title, value, icon, column):
        """Create a metric card widget"""
        card = ctk.CTkFrame(parent, corner_radius=10)
        card.grid(row=0, column=column, sticky="ew", padx=10, pady=15)
        
        # Icon
        icon_label = ctk.CTkLabel(
            card,
            text=icon,
            font=ctk.CTkFont(size=28),
        )
        icon_label.pack(pady=(15, 5))
        
        # Value
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors['primary']
        )
        value_label.pack(pady=5)
        
        # Title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_secondary']
        )
        title_label.pack(pady=(0, 15))
        
        return card, value_label
    
    def create_position_chart(self, parent):
        """Create position distribution chart"""
        chart_frame = ctk.CTkFrame(parent)
        chart_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        
        # Title
        title_label = ctk.CTkLabel(
            chart_frame,
            text="Staff by Position",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['text_primary']
        )
        title_label.pack(pady=(20, 10))
        
        # Chart area (scrollable)
        self.position_chart_frame = ctk.CTkScrollableFrame(chart_frame, height=300)
        self.position_chart_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Initially empty, will be populated when data loads
        placeholder_label = ctk.CTkLabel(
            self.position_chart_frame,
            text="Loading position data...",
            font=ctk.CTkFont(size=14),
            text_color=self.colors['text_secondary']
        )
        placeholder_label.pack(pady=50)
    
    def create_recent_activity(self, parent):
        """Create recent activity feed"""
        activity_frame = ctk.CTkFrame(parent)
        activity_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)
        
        # Title
        title_label = ctk.CTkLabel(
            activity_frame,
            text="Recent Activity",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['text_primary']
        )
        title_label.pack(pady=(20, 10))
        
        # Activity list
        self.activity_frame = ctk.CTkScrollableFrame(activity_frame, height=300)
        self.activity_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Sample activity items
        sample_activities = [
            ("👥", "New employee hired", "Sarah Johnson joined as Cashier", "2 hours ago"),
            ("📅", "Shift template created", "Morning Shift template updated", "4 hours ago"),
            ("⚠️", "Understaffing alert", "Kitchen needs 2 more staff on Friday", "6 hours ago"),
            ("📊", "Weekly report generated", "Labor cost report for Week 29", "1 day ago"),
            ("✅", "Schedule approved", "Manager approved next week's schedule", "2 days ago"),
            ("🔄", "Employee status change", "Michael Brown returned from leave", "3 days ago"),
        ]
        
        for icon, title, description, time in sample_activities:
            self.create_activity_item(icon, title, description, time)
    
    def create_activity_item(self, icon, title, description, time):
        """Create an activity item"""
        item_frame = ctk.CTkFrame(self.activity_frame, corner_radius=8)
        item_frame.pack(fill="x", pady=5, padx=5)
        
        # Content frame
        content_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=15, pady=10)
        content_frame.grid_columnconfigure(1, weight=1)
        
        # Icon
        icon_label = ctk.CTkLabel(
            content_frame,
            text=icon,
            font=ctk.CTkFont(size=16),
            width=30
        )
        icon_label.grid(row=0, column=0, rowspan=2, sticky="w", padx=(0, 10))
        
        # Title
        title_label = ctk.CTkLabel(
            content_frame,
            text=title,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors['text_primary'],
            anchor="w"
        )
        title_label.grid(row=0, column=1, sticky="ew")
        
        # Description
        desc_label = ctk.CTkLabel(
            content_frame,
            text=description,
            font=ctk.CTkFont(size=10),
            text_color=self.colors['text_secondary'],
            anchor="w"
        )
        desc_label.grid(row=1, column=1, sticky="ew")
        
        # Time
        time_label = ctk.CTkLabel(
            content_frame,
            text=time,
            font=ctk.CTkFont(size=10),
            text_color=self.colors['text_secondary']
        )
        time_label.grid(row=0, column=2, sticky="e", padx=(10, 0))
    
    def setup_labor_tab(self):
        """Setup labor costs tab"""
        # Configure grid
        self.labor_tab.grid_columnconfigure(0, weight=1)
        self.labor_tab.grid_rowconfigure(1, weight=1)
        
        # Controls frame
        controls_frame = ctk.CTkFrame(self.labor_tab)
        controls_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            controls_frame,
            text="Labor Cost Analysis",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['text_primary']
        )
        title_label.pack(pady=(15, 10))
        
        # Time period selector
        period_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        period_frame.pack(pady=(0, 15))
        
        ctk.CTkLabel(
            period_frame,
            text="Time Period:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=(0, 10))
        
        self.period_menu = ctk.CTkOptionMenu(
            period_frame,
            values=["This Week", "Last Week", "This Month", "Last Month", "Last 3 Months"],
            command=self.update_labor_analysis
        )
        self.period_menu.pack(side="left", padx=(0, 20))
        
        # Export button
        export_btn = ctk.CTkButton(
            period_frame,
            text="📄 Export Report",
            command=self.export_labor_report,
            height=30
        )
        export_btn.pack(side="left")
        
        # Analysis results
        self.labor_results_frame = ctk.CTkScrollableFrame(self.labor_tab)
        self.labor_results_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        self.update_labor_analysis()
    
    def setup_performance_tab(self):
        """Setup performance metrics tab"""
        # Configure grid
        self.performance_tab.grid_columnconfigure(0, weight=1)
        self.performance_tab.grid_rowconfigure(1, weight=1)
        
        # Controls
        controls_frame = ctk.CTkFrame(self.performance_tab)
        controls_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            controls_frame,
            text="Employee Performance Metrics",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['text_primary']
        )
        title_label.pack(pady=15)
        
        # Performance table
        self.performance_frame = ctk.CTkScrollableFrame(self.performance_tab)
        self.performance_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        self.update_performance_metrics()
    
    def setup_attendance_tab(self):
        """Setup attendance tracking tab"""
        # Configure grid
        self.attendance_tab.grid_columnconfigure(0, weight=1)
        self.attendance_tab.grid_rowconfigure(1, weight=1)
        
        # Controls
        controls_frame = ctk.CTkFrame(self.attendance_tab)
        controls_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            controls_frame,
            text="Attendance & Punctuality Report",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['text_primary']
        )
        title_label.pack(pady=15)
        
        # Attendance summary
        self.attendance_frame = ctk.CTkScrollableFrame(self.attendance_tab)
        self.attendance_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        self.update_attendance_report()
    
    def load_employee_data(self):
        """Load employee data for reports"""
        def load_data():
            try:
                employees = self.db_manager.get_all_employees(EmploymentStatus.ACTIVE)
                self.after(0, lambda: self.update_reports_with_data(employees))
            except Exception as e:
                self.after(0, lambda: self.main_app.update_status(f"Error loading employee data: {str(e)}"))
        
        threading.Thread(target=load_data, daemon=True).start()
    
    def update_reports_with_data(self, employees: List[Employee]):
        """Update all reports with employee data"""
        self.employees = employees
        
        # Update overview metrics
        self.update_overview_metrics()
        self.update_position_distribution()
        self.update_performance_metrics()
        self.update_attendance_report()
        
        self.main_app.update_status(f"Reports updated with {len(employees)} employees")
    
    def update_overview_metrics(self):
        """Update overview key metrics"""
        if not self.employees:
            return
        
        total_employees = len(self.employees)
        active_employees = len([emp for emp in self.employees if emp.status == EmploymentStatus.ACTIVE])
        total_hours = sum(emp.max_hours_per_week for emp in self.employees)
        total_cost = sum(emp.weekly_labor_cost for emp in self.employees)
        
        # Find and update metric cards (this is a simplified approach)
        # In a real implementation, we'd store references to the value labels
        # For now, we'll recreate the metrics frame
        
        # Update status
        self.main_app.update_status(f"Overview: {total_employees} employees, ${total_cost:.0f} weekly cost")
    
    def update_position_distribution(self):
        """Update position distribution chart"""
        # Clear existing chart
        for widget in self.position_chart_frame.winfo_children():
            widget.destroy()
        
        if not self.employees:
            no_data_label = ctk.CTkLabel(
                self.position_chart_frame,
                text="No employee data available",
                font=ctk.CTkFont(size=14),
                text_color=self.colors['text_secondary']
            )
            no_data_label.pack(pady=50)
            return
        
        # Count employees by position
        position_counts = {}
        for emp in self.employees:
            pos = emp.primary_position.value
            position_counts[pos] = position_counts.get(pos, 0) + 1
        
        # Create visual bars
        max_count = max(position_counts.values()) if position_counts else 1
        
        for position, count in position_counts.items():
            # Position row
            pos_frame = ctk.CTkFrame(self.position_chart_frame, corner_radius=8)
            pos_frame.pack(fill="x", pady=5, padx=10)
            
            # Position info
            info_frame = ctk.CTkFrame(pos_frame, fg_color="transparent")
            info_frame.pack(fill="x", padx=15, pady=10)
            info_frame.grid_columnconfigure(1, weight=1)
            
            # Position name
            pos_label = ctk.CTkLabel(
                info_frame,
                text=position,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.colors['text_primary']
            )
            pos_label.grid(row=0, column=0, sticky="w")
            
            # Count
            count_label = ctk.CTkLabel(
                info_frame,
                text=f"{count} employees",
                font=ctk.CTkFont(size=12),
                text_color=self.colors['text_secondary']
            )
            count_label.grid(row=0, column=2, sticky="e")
            
            # Visual bar
            bar_width = int((count / max_count) * 200)
            bar_frame = ctk.CTkFrame(
                info_frame,
                width=bar_width,
                height=8,
                fg_color=self.colors['primary']
            )
            bar_frame.grid(row=1, column=0, columnspan=3, sticky="w", pady=(5, 0))
    
    def update_labor_analysis(self, *args):
        """Update labor cost analysis"""
        # Clear existing analysis
        for widget in self.labor_results_frame.winfo_children():
            widget.destroy()
        
        if not self.employees:
            no_data_label = ctk.CTkLabel(
                self.labor_results_frame,
                text="No employee data available for analysis",
                font=ctk.CTkFont(size=14),
                text_color=self.colors['text_secondary']
            )
            no_data_label.pack(pady=50)
            return
        
        period = self.period_menu.get()
        
        # Summary card
        summary_frame = ctk.CTkFrame(self.labor_results_frame)
        summary_frame.pack(fill="x", pady=10, padx=10)
        
        title_label = ctk.CTkLabel(
            summary_frame,
            text=f"Labor Cost Summary - {period}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['text_primary']
        )
        title_label.pack(pady=(15, 10))
        
        # Calculate totals
        total_cost = sum(emp.weekly_labor_cost for emp in self.employees)
        avg_wage = sum(emp.hourly_wage for emp in self.employees) / len(self.employees)
        total_hours = sum(emp.max_hours_per_week for emp in self.employees)
        
        # Cost breakdown
        breakdown_text = f"""
Total Weekly Labor Cost: ${total_cost:.2f}
Average Hourly Wage: ${avg_wage:.2f}
Total Scheduled Hours: {total_hours} hrs
Cost per Hour: ${total_cost / total_hours:.2f}

Estimated Monthly Cost: ${total_cost * 4.33:.2f}
Estimated Annual Cost: ${total_cost * 52:.2f}
        """.strip()
        
        breakdown_label = ctk.CTkLabel(
            summary_frame,
            text=breakdown_text,
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_secondary'],
            justify="left"
        )
        breakdown_label.pack(pady=(0, 15), padx=20)
        
        # Cost by position
        position_costs_frame = ctk.CTkFrame(self.labor_results_frame)
        position_costs_frame.pack(fill="x", pady=10, padx=10)
        
        pos_title_label = ctk.CTkLabel(
            position_costs_frame,
            text="Labor Cost by Position",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors['text_primary']
        )
        pos_title_label.pack(pady=(15, 10))
        
        # Calculate cost by position
        position_costs = {}
        for emp in self.employees:
            pos = emp.primary_position.value
            if pos not in position_costs:
                position_costs[pos] = {'count': 0, 'cost': 0}
            position_costs[pos]['count'] += 1
            position_costs[pos]['cost'] += emp.weekly_labor_cost
        
        # Create cost table
        for position, data in position_costs.items():
            pos_row_frame = ctk.CTkFrame(position_costs_frame, fg_color="transparent")
            pos_row_frame.pack(fill="x", padx=20, pady=2)
            pos_row_frame.grid_columnconfigure(1, weight=1)
            
            ctk.CTkLabel(
                pos_row_frame,
                text=position,
                font=ctk.CTkFont(size=11),
                text_color=self.colors['text_primary']
            ).grid(row=0, column=0, sticky="w")
            
            ctk.CTkLabel(
                pos_row_frame,
                text=f"{data['count']} employees",
                font=ctk.CTkFont(size=11),
                text_color=self.colors['text_secondary']
            ).grid(row=0, column=1, sticky="e")
            
            ctk.CTkLabel(
                pos_row_frame,
                text=f"${data['cost']:.2f}/week",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=self.colors['success']
            ).grid(row=0, column=2, sticky="e", padx=(10, 0))
        
        # Add some padding
        ctk.CTkLabel(position_costs_frame, text="").pack(pady=10)
    
    def update_performance_metrics(self):
        """Update performance metrics table"""
        # Clear existing metrics
        for widget in self.performance_frame.winfo_children():
            widget.destroy()
        
        if not self.employees:
            no_data_label = ctk.CTkLabel(
                self.performance_frame,
                text="No employee data available",
                font=ctk.CTkFont(size=14),
                text_color=self.colors['text_secondary']
            )
            no_data_label.pack(pady=50)
            return
        
        # Create performance table
        # Header
        header_frame = ctk.CTkFrame(self.performance_frame, fg_color=self.colors['primary'])
        header_frame.pack(fill="x", pady=(0, 5), padx=10)
        header_frame.grid_columnconfigure(0, weight=2)
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_columnconfigure(2, weight=1)
        header_frame.grid_columnconfigure(3, weight=1)
        header_frame.grid_columnconfigure(4, weight=1)
        
        headers = ["Employee", "Position", "Attendance", "Punctuality", "Rating"]
        for i, header in enumerate(headers):
            ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="white"
            ).grid(row=0, column=i, padx=10, pady=10)
        
        # Employee rows
        for emp in self.employees:
            row_frame = ctk.CTkFrame(self.performance_frame, corner_radius=5)
            row_frame.pack(fill="x", pady=2, padx=10)
            row_frame.grid_columnconfigure(0, weight=2)
            row_frame.grid_columnconfigure(1, weight=1)
            row_frame.grid_columnconfigure(2, weight=1)
            row_frame.grid_columnconfigure(3, weight=1)
            row_frame.grid_columnconfigure(4, weight=1)
            
            # Employee name
            ctk.CTkLabel(
                row_frame,
                text=emp.full_name,
                font=ctk.CTkFont(size=11),
                text_color=self.colors['text_primary']
            ).grid(row=0, column=0, sticky="w", padx=10, pady=8)
            
            # Position
            ctk.CTkLabel(
                row_frame,
                text=emp.primary_position.value,
                font=ctk.CTkFont(size=11),
                text_color=self.colors['text_secondary']
            ).grid(row=0, column=1, padx=10, pady=8)
            
            # Attendance
            attendance_color = self.colors['success'] if emp.attendance_rate >= 95 else self.colors['warning'] if emp.attendance_rate >= 85 else self.colors['danger']
            ctk.CTkLabel(
                row_frame,
                text=f"{emp.attendance_rate:.1f}%",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=attendance_color
            ).grid(row=0, column=2, padx=10, pady=8)
            
            # Punctuality
            punctuality_color = self.colors['success'] if emp.punctuality_score >= 95 else self.colors['warning'] if emp.punctuality_score >= 85 else self.colors['danger']
            ctk.CTkLabel(
                row_frame,
                text=f"{emp.punctuality_score:.1f}%",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=punctuality_color
            ).grid(row=0, column=3, padx=10, pady=8)
            
            # Rating
            rating_color = self.colors['success'] if emp.customer_rating >= 4.5 else self.colors['warning'] if emp.customer_rating >= 3.5 else self.colors['danger']
            ctk.CTkLabel(
                row_frame,
                text=f"{emp.customer_rating:.1f}/5.0",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=rating_color
            ).grid(row=0, column=4, padx=10, pady=8)
    
    def update_attendance_report(self):
        """Update attendance report"""
        # Clear existing report
        for widget in self.attendance_frame.winfo_children():
            widget.destroy()
        
        if not self.employees:
            no_data_label = ctk.CTkLabel(
                self.attendance_frame,
                text="No employee data available",
                font=ctk.CTkFont(size=14),
                text_color=self.colors['text_secondary']
            )
            no_data_label.pack(pady=50)
            return
        
        # Attendance summary
        summary_frame = ctk.CTkFrame(self.attendance_frame)
        summary_frame.pack(fill="x", pady=10, padx=10)
        
        title_label = ctk.CTkLabel(
            summary_frame,
            text="Attendance Summary",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['text_primary']
        )
        title_label.pack(pady=(15, 10))
        
        # Calculate attendance stats
        avg_attendance = sum(emp.attendance_rate for emp in self.employees) / len(self.employees)
        avg_punctuality = sum(emp.punctuality_score for emp in self.employees) / len(self.employees)
        excellent_attendance = len([emp for emp in self.employees if emp.attendance_rate >= 95])
        poor_attendance = len([emp for emp in self.employees if emp.attendance_rate < 85])
        
        summary_text = f"""
Average Attendance Rate: {avg_attendance:.1f}%
Average Punctuality Score: {avg_punctuality:.1f}%

Excellent Attendance (≥95%): {excellent_attendance} employees
Needs Improvement (<85%): {poor_attendance} employees

Total Employees Tracked: {len(self.employees)}
        """.strip()
        
        summary_label = ctk.CTkLabel(
            summary_frame,
            text=summary_text,
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_secondary'],
            justify="left"
        )
        summary_label.pack(pady=(0, 15), padx=20)
        
        # Attendance alerts
        if poor_attendance > 0:
            alert_frame = ctk.CTkFrame(self.attendance_frame, fg_color=self.colors['danger'])
            alert_frame.pack(fill="x", pady=10, padx=10)
            
            alert_label = ctk.CTkLabel(
                alert_frame,
                text=f"⚠️ ATTENTION: {poor_attendance} employees have attendance below 85%",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="white"
            )
            alert_label.pack(pady=15)
    
    def export_labor_report(self):
        """Export labor cost report"""
        try:
            import pandas as pd
            from tkinter import filedialog
            
            if not self.employees:
                messagebox.showwarning("No Data", "No employee data available for export.")
                return
            
            filename = filedialog.asksaveasfilename(
                title="Export Labor Report",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialname=f"Restaurant_Labor_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )
            
            if not filename:
                return
            
            # Prepare labor data
            labor_data = []
            for emp in self.employees:
                labor_data.append({
                    'Employee Name': emp.full_name,
                    'Position': emp.primary_position.value,
                    'Hourly Wage': emp.hourly_wage,
                    'Weekly Hours': emp.max_hours_per_week,
                    'Weekly Labor Cost': emp.weekly_labor_cost,
                    'Status': emp.status.value
                })
            
            # Create DataFrame and export
            df = pd.DataFrame(labor_data)
            df.to_excel(filename, index=False, sheet_name='Labor Costs')
            
            messagebox.showinfo("Export Successful", f"Labor report exported to:\n{filename}")
            self.main_app.update_status(f"Labor report exported to {filename}")
            
        except ImportError:
            messagebox.showerror(
                "Missing Dependency",
                "Excel export requires pandas and openpyxl.\n\nPlease install them with:\npip install pandas openpyxl"
            )
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export report:\n{str(e)}") 