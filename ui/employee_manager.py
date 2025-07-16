import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, time
from typing import List, Optional
import threading

from models.employee import Employee, Position, EmploymentStatus, SkillLevel, Availability
from database.db_manager import DatabaseManager

class EmployeeManagerFrame(ctk.CTkFrame):
    def __init__(self, parent, db_manager: DatabaseManager, main_app):
        super().__init__(parent)
        
        self.db_manager = db_manager
        self.main_app = main_app
        self.employees: List[Employee] = []
        self.selected_employee: Optional[Employee] = None
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Colors from main app
        self.colors = main_app.colors
        
        # Create UI
        self.create_employee_list()
        self.create_employee_details()
        self.create_toolbar()
        
        # Load employees
        self.load_employees()
    
    def create_toolbar(self):
        """Create toolbar with action buttons"""
        toolbar_frame = ctk.CTkFrame(self, fg_color="transparent")
        toolbar_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        # Add Employee button
        self.add_btn = ctk.CTkButton(
            toolbar_frame,
            text="➕ Add Employee",
            command=self.add_employee_dialog,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors['success'],
            hover_color="#229954",
            height=40
        )
        self.add_btn.pack(side="left", padx=(0, 10))
        
        # Edit Employee button
        self.edit_btn = ctk.CTkButton(
            toolbar_frame,
            text="✏️ Edit Employee",
            command=self.edit_employee_dialog,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors['primary'],
            height=40,
            state="disabled"
        )
        self.edit_btn.pack(side="left", padx=(0, 10))
        
        # Delete Employee button  
        self.delete_btn = ctk.CTkButton(
            toolbar_frame,
            text="🗑️ Remove Employee",
            command=self.delete_employee,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors['danger'],
            hover_color="#C0392B",
            height=40,
            state="disabled"
        )
        self.delete_btn.pack(side="left", padx=(0, 10))
        
        # Export to Excel button
        self.export_btn = ctk.CTkButton(
            toolbar_frame,
            text="📊 Export Excel",
            command=self.export_to_excel,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors['success'],
            hover_color="#229954",
            height=40
        )
        self.export_btn.pack(side="right", padx=(0, 10))

        # Refresh button
        self.refresh_btn = ctk.CTkButton(
            toolbar_frame,
            text="🔄 Refresh",
            command=self.load_employees,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="transparent",
            text_color=self.colors['text_primary'],
            border_width=2,
            border_color=self.colors['text_secondary'],
            height=40
        )
        self.refresh_btn.pack(side="right")
    
    def create_employee_list(self):
        """Create employee list with search and filters"""
        # Left panel for employee list
        list_frame = ctk.CTkFrame(self, width=400)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        list_frame.grid_rowconfigure(2, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Search and filter section
        search_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        search_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=15)
        search_frame.grid_columnconfigure(0, weight=1)
        
        # Search entry
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_employees)
        
        search_label = ctk.CTkLabel(
            search_frame,
            text="Search Employees:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors['text_primary']
        )
        search_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="Search by name, employee number, or position...",
            font=ctk.CTkFont(size=12),
            height=35
        )
        self.search_entry.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        # Filter by status
        status_label = ctk.CTkLabel(
            search_frame,
            text="Filter by Status:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors['text_primary']
        )
        status_label.grid(row=2, column=0, sticky="w", pady=(0, 5))
        
        self.status_filter = ctk.CTkOptionMenu(
            search_frame,
            values=["All"] + [status.value for status in EmploymentStatus],
            command=self.filter_employees,
            font=ctk.CTkFont(size=12),
            height=35
        )
        self.status_filter.grid(row=3, column=0, sticky="ew")
        
        # Employee count label
        self.count_label = ctk.CTkLabel(
            list_frame,
            text="Total Employees: 0",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_secondary']
        )
        self.count_label.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="w")
        
        # Employee list
        list_container = ctk.CTkFrame(list_frame)
        list_container.grid(row=2, column=0, sticky="nsew", padx=15, pady=(0, 15))
        list_container.grid_rowconfigure(0, weight=1)
        list_container.grid_columnconfigure(0, weight=1)
        
        # Create treeview for employee list
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#ffffff", foreground="#333333", fieldbackground="#ffffff")
        style.configure("Treeview.Heading", background=self.colors['primary'], foreground="white")
        style.map("Treeview", background=[('selected', self.colors['primary'])])
        
        self.employee_tree = ttk.Treeview(
            list_container,
            columns=("name", "position", "status", "wage"),
            show="headings",
            style="Treeview"
        )
        
        # Configure columns
        self.employee_tree.heading("name", text="Name")
        self.employee_tree.heading("position", text="Position")
        self.employee_tree.heading("status", text="Status")
        self.employee_tree.heading("wage", text="Wage/hr")
        
        self.employee_tree.column("name", width=120, minwidth=100)
        self.employee_tree.column("position", width=100, minwidth=80)
        self.employee_tree.column("status", width=80, minwidth=60)
        self.employee_tree.column("wage", width=80, minwidth=60)
        
        # Scrollbar for treeview
        tree_scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.employee_tree.yview)
        self.employee_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Grid treeview and scrollbar
        self.employee_tree.grid(row=0, column=0, sticky="nsew")
        tree_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Bind selection event
        self.employee_tree.bind("<<TreeviewSelect>>", self.on_employee_select)
    
    def create_employee_details(self):
        """Create employee details panel"""
        # Right panel for employee details
        details_frame = ctk.CTkFrame(self)
        details_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        details_frame.grid_columnconfigure(0, weight=1)
        details_frame.grid_rowconfigure(0, weight=1)
        
        # Scrollable frame for details
        self.details_scroll = ctk.CTkScrollableFrame(
            details_frame,
            label_text="Employee Details",
            label_font=ctk.CTkFont(size=18, weight="bold")
        )
        self.details_scroll.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.details_scroll.grid_columnconfigure(1, weight=1)
        
        # No selection message
        self.no_selection_label = ctk.CTkLabel(
            self.details_scroll,
            text="Select an employee from the list to view details",
            font=ctk.CTkFont(size=16),
            text_color=self.colors['text_secondary']
        )
        self.no_selection_label.grid(row=0, column=0, columnspan=2, pady=50)
    
    def show_employee_details(self, employee: Employee):
        """Show detailed employee information"""
        # Clear existing details
        for widget in self.details_scroll.winfo_children():
            widget.destroy()
        
        row = 0
        
        # Personal Information Section
        personal_title = ctk.CTkLabel(
            self.details_scroll,
            text="Personal Information",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['secondary']
        )
        personal_title.grid(row=row, column=0, columnspan=2, sticky="w", pady=(0, 15))
        row += 1
        
        # Create info fields
        info_fields = [
            ("Employee Number:", employee.employee_number),
            ("Full Name:", employee.full_name),
            ("Email:", employee.email),
            ("Phone:", employee.phone),
            ("Address:", employee.address),
            ("Hire Date:", employee.hire_date.strftime("%B %d, %Y")),
            ("Status:", employee.status.value)
        ]
        
        for label, value in info_fields:
            # Label
            label_widget = ctk.CTkLabel(
                self.details_scroll,
                text=label,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.colors['text_primary']
            )
            label_widget.grid(row=row, column=0, sticky="w", padx=(0, 20), pady=2)
            
            # Value
            value_widget = ctk.CTkLabel(
                self.details_scroll,
                text=str(value),
                font=ctk.CTkFont(size=12),
                text_color=self.colors['text_secondary']
            )
            value_widget.grid(row=row, column=1, sticky="w", pady=2)
            row += 1
        
        # Employment Details Section
        employment_title = ctk.CTkLabel(
            self.details_scroll,
            text="Employment Details",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['secondary']
        )
        employment_title.grid(row=row, column=0, columnspan=2, sticky="w", pady=(20, 15))
        row += 1
        
        employment_fields = [
            ("Hourly Wage:", f"${employee.hourly_wage:.2f}"),
            ("Primary Position:", employee.primary_position.value),
            ("Weekly Hours:", f"{employee.min_hours_per_week} - {employee.max_hours_per_week} hours"),
            ("Weekly Labor Cost:", f"${employee.weekly_labor_cost:.2f}"),
        ]
        
        for label, value in employment_fields:
            label_widget = ctk.CTkLabel(
                self.details_scroll,
                text=label,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.colors['text_primary']
            )
            label_widget.grid(row=row, column=0, sticky="w", padx=(0, 20), pady=2)
            
            value_widget = ctk.CTkLabel(
                self.details_scroll,
                text=str(value),
                font=ctk.CTkFont(size=12),
                text_color=self.colors['text_secondary']
            )
            value_widget.grid(row=row, column=1, sticky="w", pady=2)
            row += 1
        
        # Secondary Positions
        if employee.secondary_positions:
            secondary_label = ctk.CTkLabel(
                self.details_scroll,
                text="Secondary Positions:",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.colors['text_primary']
            )
            secondary_label.grid(row=row, column=0, sticky="w", padx=(0, 20), pady=2)
            
            positions_text = ", ".join([pos.value for pos in employee.secondary_positions])
            secondary_value = ctk.CTkLabel(
                self.details_scroll,
                text=positions_text,
                font=ctk.CTkFont(size=12),
                text_color=self.colors['text_secondary']
            )
            secondary_value.grid(row=row, column=1, sticky="w", pady=2)
            row += 1
        
        # Performance Metrics Section
        performance_title = ctk.CTkLabel(
            self.details_scroll,
            text="Performance Metrics",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['secondary']
        )
        performance_title.grid(row=row, column=0, columnspan=2, sticky="w", pady=(20, 15))
        row += 1
        
        performance_fields = [
            ("Attendance Rate:", f"{employee.attendance_rate:.1f}%"),
            ("Punctuality Score:", f"{employee.punctuality_score:.1f}%"),
            ("Customer Rating:", f"{employee.customer_rating:.1f}/5.0"),
        ]
        
        for label, value in performance_fields:
            label_widget = ctk.CTkLabel(
                self.details_scroll,
                text=label,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.colors['text_primary']
            )
            label_widget.grid(row=row, column=0, sticky="w", padx=(0, 20), pady=2)
            
            value_widget = ctk.CTkLabel(
                self.details_scroll,
                text=str(value),
                font=ctk.CTkFont(size=12),
                text_color=self.colors['text_secondary']
            )
            value_widget.grid(row=row, column=1, sticky="w", pady=2)
            row += 1
        
        # Notes Section
        if employee.notes or employee.special_requirements:
            notes_title = ctk.CTkLabel(
                self.details_scroll,
                text="Notes & Requirements",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=self.colors['secondary']
            )
            notes_title.grid(row=row, column=0, columnspan=2, sticky="w", pady=(20, 15))
            row += 1
            
            if employee.special_requirements:
                req_label = ctk.CTkLabel(
                    self.details_scroll,
                    text="Special Requirements:",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=self.colors['text_primary']
                )
                req_label.grid(row=row, column=0, sticky="nw", padx=(0, 20), pady=2)
                
                req_value = ctk.CTkLabel(
                    self.details_scroll,
                    text=employee.special_requirements,
                    font=ctk.CTkFont(size=12),
                    text_color=self.colors['text_secondary'],
                    wraplength=300
                )
                req_value.grid(row=row, column=1, sticky="w", pady=2)
                row += 1
            
            if employee.notes:
                notes_label = ctk.CTkLabel(
                    self.details_scroll,
                    text="Notes:",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=self.colors['text_primary']
                )
                notes_label.grid(row=row, column=0, sticky="nw", padx=(0, 20), pady=2)
                
                notes_value = ctk.CTkLabel(
                    self.details_scroll,
                    text=employee.notes,
                    font=ctk.CTkFont(size=12),
                    text_color=self.colors['text_secondary'],
                    wraplength=300
                )
                notes_value.grid(row=row, column=1, sticky="w", pady=2)
                row += 1
    
    def load_employees(self):
        """Load employees from database"""
        def load_data():
            try:
                employees = self.db_manager.get_all_employees()
                # Update UI in main thread
                self.after(0, lambda: self.update_employee_list(employees))
            except Exception as e:
                self.after(0, lambda: self.main_app.update_status(f"Error loading employees: {str(e)}"))
        
        # Load in background thread
        threading.Thread(target=load_data, daemon=True).start()
        self.main_app.update_status("Loading employees...")
    
    def update_employee_list(self, employees: List[Employee]):
        """Update employee list in UI"""
        self.employees = employees
        
        # Clear existing items
        for item in self.employee_tree.get_children():
            self.employee_tree.delete(item)
        
        # Add employees to tree
        for employee in employees:
            self.employee_tree.insert("", "end", values=(
                employee.full_name,
                employee.primary_position.value,
                employee.status.value,
                f"${employee.hourly_wage:.2f}"
            ), tags=(str(employee.id),))
        
        # Update count
        self.count_label.configure(text=f"Total Employees: {len(employees)}")
        
        # Update main app stats
        active_count = len([emp for emp in employees if emp.status == EmploymentStatus.ACTIVE])
        self.main_app.update_stats(active_count)
        
        self.main_app.update_status(f"Loaded {len(employees)} employees")
    
    def filter_employees(self, *args):
        """Filter employees based on search and status"""
        search_text = self.search_var.get().lower()
        status_filter = self.status_filter.get()
        
        filtered_employees = []
        for employee in self.employees:
            # Status filter
            if status_filter != "All" and employee.status.value != status_filter:
                continue
            
            # Search filter
            if search_text:
                searchable_text = f"{employee.full_name} {employee.employee_number} {employee.primary_position.value}".lower()
                if search_text not in searchable_text:
                    continue
            
            filtered_employees.append(employee)
        
        # Update tree view
        for item in self.employee_tree.get_children():
            self.employee_tree.delete(item)
        
        for employee in filtered_employees:
            self.employee_tree.insert("", "end", values=(
                employee.full_name,
                employee.primary_position.value,
                employee.status.value,
                f"${employee.hourly_wage:.2f}"
            ), tags=(str(employee.id),))
        
        # Update count
        self.count_label.configure(text=f"Filtered Employees: {len(filtered_employees)} / {len(self.employees)}")
    
    def on_employee_select(self, event):
        """Handle employee selection"""
        selection = self.employee_tree.selection()
        if not selection:
            self.selected_employee = None
            self.edit_btn.configure(state="disabled")
            self.delete_btn.configure(state="disabled")
            # Show no selection message
            for widget in self.details_scroll.winfo_children():
                widget.destroy()
            self.no_selection_label = ctk.CTkLabel(
                self.details_scroll,
                text="Select an employee from the list to view details",
                font=ctk.CTkFont(size=16),
                text_color=self.colors['text_secondary']
            )
            self.no_selection_label.grid(row=0, column=0, columnspan=2, pady=50)
            return
        
        # Get selected employee
        item = selection[0]
        employee_id = int(self.employee_tree.item(item)["tags"][0])
        
        self.selected_employee = None
        for employee in self.employees:
            if employee.id == employee_id:
                self.selected_employee = employee
                break
        
        if self.selected_employee:
            self.show_employee_details(self.selected_employee)
            self.edit_btn.configure(state="normal")
            self.delete_btn.configure(state="normal")
    
    def add_employee_dialog(self):
        """Open add employee dialog"""
        dialog = EmployeeDialog(self, self.db_manager, self.main_app, "Add Employee")
        if dialog.result:
            self.load_employees()
    
    def edit_employee_dialog(self):
        """Open edit employee dialog"""
        if not self.selected_employee:
            return
        
        dialog = EmployeeDialog(self, self.db_manager, self.main_app, "Edit Employee", self.selected_employee)
        if dialog.result:
            self.load_employees()
    
    def delete_employee(self):
        """Delete selected employee"""
        if not self.selected_employee:
            return
        
        # Confirm deletion
        result = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to remove {self.selected_employee.full_name}?\n\n"
            "This will set their status to 'Terminated' and they will no longer appear in active schedules.",
            icon="warning"
        )
        
        if result:
            try:
                self.db_manager.delete_employee(self.selected_employee.id)
                self.main_app.update_status(f"Employee {self.selected_employee.full_name} removed")
                self.load_employees()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to remove employee:\n{str(e)}")
    
    def export_to_excel(self):
        """Export employee data to Excel file"""
        try:
            import pandas as pd
            from tkinter import filedialog
            from datetime import datetime
            
            if not self.employees:
                messagebox.showwarning("No Data", "No employees to export. Please load employee data first.")
                return
            
            # Ask user for save location
            filename = filedialog.asksaveasfilename(
                title="Export Employees",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialname=f"Restaurant_Employees_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )
            
            if not filename:
                return
            
            # Prepare data for export
            export_data = []
            for employee in self.employees:
                row = {
                    'Employee Number': employee.employee_number,
                    'First Name': employee.first_name,
                    'Last Name': employee.last_name,
                    'Email': employee.email,
                    'Phone': employee.phone,
                    'Address': employee.address,
                    'Hire Date': employee.hire_date.strftime('%Y-%m-%d'),
                    'Status': employee.status.value,
                    'Hourly Wage': f"${employee.hourly_wage:.2f}",
                    'Primary Position': employee.primary_position.value,
                    'Secondary Positions': ', '.join([pos.value for pos in employee.secondary_positions]),
                    'Min Hours/Week': employee.min_hours_per_week,
                    'Max Hours/Week': employee.max_hours_per_week,
                    'Attendance Rate': f"{employee.attendance_rate:.1f}%",
                    'Punctuality Score': f"{employee.punctuality_score:.1f}%",
                    'Customer Rating': f"{employee.customer_rating:.1f}/5.0",
                    'Training Completed': ', '.join(employee.training_completed),
                    'Special Requirements': employee.special_requirements,
                    'Notes': employee.notes,
                    'Weekly Labor Cost': f"${employee.weekly_labor_cost:.2f}"
                }
                export_data.append(row)
            
            # Create DataFrame and export
            df = pd.DataFrame(export_data)
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Main employee data
                df.to_excel(writer, sheet_name='Employee Data', index=False)
                
                # Summary statistics
                summary_data = {
                    'Metric': [
                        'Total Employees',
                        'Active Employees', 
                        'Inactive/On Leave',
                        'Average Wage',
                        'Total Weekly Labor Cost',
                        'Average Attendance Rate',
                        'Average Customer Rating'
                    ],
                    'Value': [
                        len(self.employees),
                        len([emp for emp in self.employees if emp.status == EmploymentStatus.ACTIVE]),
                        len([emp for emp in self.employees if emp.status != EmploymentStatus.ACTIVE]),
                        f"${sum(emp.hourly_wage for emp in self.employees) / len(self.employees):.2f}",
                        f"${sum(emp.weekly_labor_cost for emp in self.employees):.2f}",
                        f"{sum(emp.attendance_rate for emp in self.employees) / len(self.employees):.1f}%",
                        f"{sum(emp.customer_rating for emp in self.employees) / len(self.employees):.1f}/5.0"
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Position breakdown
                position_counts = {}
                for emp in self.employees:
                    pos = emp.primary_position.value
                    position_counts[pos] = position_counts.get(pos, 0) + 1
                
                position_data = {
                    'Position': list(position_counts.keys()),
                    'Count': list(position_counts.values())
                }
                position_df = pd.DataFrame(position_data)
                position_df.to_excel(writer, sheet_name='Position Breakdown', index=False)
            
            self.main_app.update_status(f"Employee data exported to {filename}")
            messagebox.showinfo(
                "Export Successful", 
                f"Employee data has been exported to:\n{filename}\n\n"
                f"The file contains {len(self.employees)} employees across 3 sheets:\n"
                "• Employee Data (detailed information)\n"
                "• Summary (key statistics)\n"
                "• Position Breakdown (staffing by role)"
            )
            
        except ImportError:
            messagebox.showerror(
                "Missing Dependency", 
                "Excel export requires pandas and openpyxl.\n\n"
                "Please install them with:\npip install pandas openpyxl"
            )
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data:\n{str(e)}")

class EmployeeDialog:
    def __init__(self, parent, db_manager: DatabaseManager, main_app, title: str, employee: Optional[Employee] = None):
        self.db_manager = db_manager
        self.main_app = main_app
        self.employee = employee
        self.result = None
        
        # Create dialog window
        self.window = ctk.CTkToplevel(parent)
        self.window.title(title)
        self.window.geometry("600x700")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Center the window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.window.winfo_screenheight() // 2) - (700 // 2)
        self.window.geometry(f"600x700+{x}+{y}")
        
        self.colors = main_app.colors
        self.create_form()
        
        if employee:
            self.populate_form()
        
        # Wait for dialog to close
        self.window.wait_window()
    
    def create_form(self):
        """Create employee form"""
        # Main frame with scrolling
        main_frame = ctk.CTkScrollableFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_columnconfigure(1, weight=1)
        
        row = 0
        
        # Personal Information
        personal_title = ctk.CTkLabel(
            main_frame,
            text="Personal Information",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['secondary']
        )
        personal_title.grid(row=row, column=0, columnspan=2, sticky="w", pady=(0, 15))
        row += 1
        
        # Employee Number
        ctk.CTkLabel(main_frame, text="Employee Number:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.employee_number_entry = ctk.CTkEntry(main_frame, width=200)
        self.employee_number_entry.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1
        
        # First Name
        ctk.CTkLabel(main_frame, text="First Name:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.first_name_entry = ctk.CTkEntry(main_frame, width=200)
        self.first_name_entry.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1
        
        # Last Name
        ctk.CTkLabel(main_frame, text="Last Name:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.last_name_entry = ctk.CTkEntry(main_frame, width=200)
        self.last_name_entry.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1
        
        # Email
        ctk.CTkLabel(main_frame, text="Email:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.email_entry = ctk.CTkEntry(main_frame, width=200)
        self.email_entry.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1
        
        # Phone
        ctk.CTkLabel(main_frame, text="Phone:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.phone_entry = ctk.CTkEntry(main_frame, width=200)
        self.phone_entry.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1
        
        # Employment Details
        employment_title = ctk.CTkLabel(
            main_frame,
            text="Employment Details",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['secondary']
        )
        employment_title.grid(row=row, column=0, columnspan=2, sticky="w", pady=(20, 15))
        row += 1
        
        # Hourly Wage
        ctk.CTkLabel(main_frame, text="Hourly Wage ($):", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.wage_entry = ctk.CTkEntry(main_frame, width=200)
        self.wage_entry.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1
        
        # Primary Position
        ctk.CTkLabel(main_frame, text="Primary Position:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.position_menu = ctk.CTkOptionMenu(
            main_frame,
            values=[pos.value for pos in Position],
            width=200
        )
        self.position_menu.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1
        
        # Status
        ctk.CTkLabel(main_frame, text="Status:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.status_menu = ctk.CTkOptionMenu(
            main_frame,
            values=[status.value for status in EmploymentStatus],
            width=200
        )
        self.status_menu.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1
        
        # Min Hours per Week
        ctk.CTkLabel(main_frame, text="Min Hours/Week:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.min_hours_entry = ctk.CTkEntry(main_frame, width=200)
        self.min_hours_entry.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1
        
        # Max Hours per Week
        ctk.CTkLabel(main_frame, text="Max Hours/Week:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.max_hours_entry = ctk.CTkEntry(main_frame, width=200)
        self.max_hours_entry.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1
        
        # Notes
        ctk.CTkLabel(main_frame, text="Notes:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=row, column=0, sticky="nw", padx=(0, 10), pady=5)
        self.notes_textbox = ctk.CTkTextbox(main_frame, height=80, width=200)
        self.notes_textbox.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="Save",
            command=self.save_employee,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors['success'],
            width=120
        )
        save_btn.pack(side="left", padx=(0, 10))
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.window.destroy,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors['text_secondary'],
            width=120
        )
        cancel_btn.pack(side="left")
    
    def populate_form(self):
        """Populate form with existing employee data"""
        if not self.employee:
            return
        
        self.employee_number_entry.insert(0, self.employee.employee_number)
        self.first_name_entry.insert(0, self.employee.first_name)
        self.last_name_entry.insert(0, self.employee.last_name)
        self.email_entry.insert(0, self.employee.email)
        self.phone_entry.insert(0, self.employee.phone)
        self.wage_entry.insert(0, str(self.employee.hourly_wage))
        self.position_menu.set(self.employee.primary_position.value)
        self.status_menu.set(self.employee.status.value)
        self.min_hours_entry.insert(0, str(self.employee.min_hours_per_week))
        self.max_hours_entry.insert(0, str(self.employee.max_hours_per_week))
        self.notes_textbox.insert("1.0", self.employee.notes)
    
    def save_employee(self):
        """Save employee to database"""
        try:
            # Validate required fields
            if not all([
                self.employee_number_entry.get().strip(),
                self.first_name_entry.get().strip(),
                self.last_name_entry.get().strip(),
                self.wage_entry.get().strip()
            ]):
                messagebox.showerror("Validation Error", "Please fill in all required fields.")
                return
            
            # Validate wage
            try:
                wage = float(self.wage_entry.get())
                if wage <= 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Validation Error", "Please enter a valid hourly wage.")
                return
            
            # Validate hours
            try:
                min_hours = int(self.min_hours_entry.get() or "0")
                max_hours = int(self.max_hours_entry.get() or "40")
                if min_hours < 0 or max_hours <= 0 or min_hours > max_hours:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Validation Error", "Please enter valid hour ranges.")
                return
            
            # Create or update employee
            if self.employee:
                # Update existing
                self.employee.employee_number = self.employee_number_entry.get().strip()
                self.employee.first_name = self.first_name_entry.get().strip()
                self.employee.last_name = self.last_name_entry.get().strip()
                self.employee.email = self.email_entry.get().strip()
                self.employee.phone = self.phone_entry.get().strip()
                self.employee.hourly_wage = wage
                self.employee.primary_position = Position(self.position_menu.get())
                self.employee.status = EmploymentStatus(self.status_menu.get())
                self.employee.min_hours_per_week = min_hours
                self.employee.max_hours_per_week = max_hours
                self.employee.notes = self.notes_textbox.get("1.0", "end-1c")
                self.employee.updated_at = datetime.now()
                
                self.db_manager.update_employee(self.employee)
                self.main_app.update_status(f"Updated employee: {self.employee.full_name}")
            else:
                # Create new
                new_employee = Employee(
                    employee_number=self.employee_number_entry.get().strip(),
                    first_name=self.first_name_entry.get().strip(),
                    last_name=self.last_name_entry.get().strip(),
                    email=self.email_entry.get().strip(),
                    phone=self.phone_entry.get().strip(),
                    hourly_wage=wage,
                    primary_position=Position(self.position_menu.get()),
                    status=EmploymentStatus(self.status_menu.get()),
                    min_hours_per_week=min_hours,
                    max_hours_per_week=max_hours,
                    notes=self.notes_textbox.get("1.0", "end-1c")
                )
                
                employee_id = self.db_manager.add_employee(new_employee)
                self.main_app.update_status(f"Added employee: {new_employee.full_name}")
            
            self.result = True
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save employee:\n{str(e)}") 