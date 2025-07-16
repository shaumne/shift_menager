import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, time, timedelta
from typing import List, Optional
import threading

from database.db_manager import DatabaseManager
from models.shift import ShiftTemplate, ShiftType, ShiftPriority, PositionRequirement, WeekDay
from models.employee import Position

class ShiftCreatorFrame(ctk.CTkFrame):
    def __init__(self, parent, db_manager: DatabaseManager, main_app):
        super().__init__(parent)
        
        self.db_manager = db_manager
        self.main_app = main_app
        self.colors = main_app.colors
        self.shift_templates: List[ShiftTemplate] = []
        self.selected_template: Optional[ShiftTemplate] = None
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.create_ui()
        self.load_shift_templates()
    
    def create_ui(self):
        """Create shift creator interface"""
        # Left panel for template list
        self.create_template_list()
        
        # Right panel for template details/creation
        self.create_template_editor()
        
        # Bottom toolbar
        self.create_toolbar()
    
    def create_template_list(self):
        """Create shift template list"""
        list_frame = ctk.CTkFrame(self, width=350)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        list_frame.grid_rowconfigure(2, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            list_frame,
            text="Shift Templates",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['text_primary']
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Search/filter section
        search_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        search_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15))
        search_frame.grid_columnconfigure(0, weight=1)
        
        # Template count
        self.template_count_label = ctk.CTkLabel(
            search_frame,
            text="Total Templates: 0",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_secondary']
        )
        self.template_count_label.grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        # Filter by shift type
        filter_label = ctk.CTkLabel(
            search_frame,
            text="Filter by Type:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors['text_primary']
        )
        filter_label.grid(row=1, column=0, sticky="w", pady=(0, 5))
        
        self.type_filter = ctk.CTkOptionMenu(
            search_frame,
            values=["All"] + [shift_type.value for shift_type in ShiftType],
            command=self.filter_templates,
            font=ctk.CTkFont(size=12),
            height=30
        )
        self.type_filter.grid(row=2, column=0, sticky="ew")
        
        # Template list
        list_container = ctk.CTkFrame(list_frame)
        list_container.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        list_container.grid_rowconfigure(0, weight=1)
        list_container.grid_columnconfigure(0, weight=1)
        
        # Create treeview for template list
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#ffffff", foreground="#333333", fieldbackground="#ffffff")
        style.configure("Treeview.Heading", background=self.colors['primary'], foreground="white")
        style.map("Treeview", background=[('selected', self.colors['primary'])])
        
        self.template_tree = ttk.Treeview(
            list_container,
            columns=("name", "type", "hours", "cost"),
            show="headings",
            style="Treeview"
        )
        
        # Configure columns
        self.template_tree.heading("name", text="Template Name")
        self.template_tree.heading("type", text="Type")
        self.template_tree.heading("hours", text="Duration")
        self.template_tree.heading("cost", text="Est. Cost")
        
        self.template_tree.column("name", width=120, minwidth=100)
        self.template_tree.column("type", width=80, minwidth=60)
        self.template_tree.column("hours", width=60, minwidth=50)
        self.template_tree.column("cost", width=70, minwidth=60)
        
        # Scrollbar for treeview
        tree_scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.template_tree.yview)
        self.template_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Grid treeview and scrollbar
        self.template_tree.grid(row=0, column=0, sticky="nsew")
        tree_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Bind selection event
        self.template_tree.bind("<<TreeviewSelect>>", self.on_template_select)
    
    def create_template_editor(self):
        """Create template editor panel"""
        editor_frame = ctk.CTkFrame(self)
        editor_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        editor_frame.grid_columnconfigure(0, weight=1)
        editor_frame.grid_rowconfigure(0, weight=1)
        
        # Scrollable frame for editor
        self.editor_scroll = ctk.CTkScrollableFrame(
            editor_frame,
            label_text="Shift Template Editor",
            label_font=ctk.CTkFont(size=18, weight="bold")
        )
        self.editor_scroll.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.editor_scroll.grid_columnconfigure(1, weight=1)
        
        self.create_editor_form()
    
    def create_editor_form(self):
        """Create the template editing form"""
        # Clear existing form
        for widget in self.editor_scroll.winfo_children():
            widget.destroy()
        
        row = 0
        
        # Basic Information Section
        basic_title = ctk.CTkLabel(
            self.editor_scroll,
            text="Basic Information",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['secondary']
        )
        basic_title.grid(row=row, column=0, columnspan=2, sticky="w", pady=(0, 15))
        row += 1
        
        # Template Name
        ctk.CTkLabel(self.editor_scroll, text="Template Name:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.name_entry = ctk.CTkEntry(self.editor_scroll, width=250)
        self.name_entry.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1
        
        # Shift Type
        ctk.CTkLabel(self.editor_scroll, text="Shift Type:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.shift_type_menu = ctk.CTkOptionMenu(
            self.editor_scroll,
            values=[shift_type.value for shift_type in ShiftType],
            width=250
        )
        self.shift_type_menu.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1
        
        # Priority
        ctk.CTkLabel(self.editor_scroll, text="Priority:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.priority_menu = ctk.CTkOptionMenu(
            self.editor_scroll,
            values=[priority.value for priority in ShiftPriority],
            width=250
        )
        self.priority_menu.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1
        
        # Timing Section
        timing_title = ctk.CTkLabel(
            self.editor_scroll,
            text="Timing & Duration",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['secondary']
        )
        timing_title.grid(row=row, column=0, columnspan=2, sticky="w", pady=(20, 15))
        row += 1
        
        # Start Time
        ctk.CTkLabel(self.editor_scroll, text="Start Time:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        start_time_frame = ctk.CTkFrame(self.editor_scroll, fg_color="transparent")
        start_time_frame.grid(row=row, column=1, sticky="ew", pady=5)
        
        self.start_hour_menu = ctk.CTkOptionMenu(
            start_time_frame,
            values=[f"{i:02d}" for i in range(24)],
            width=60
        )
        self.start_hour_menu.pack(side="left")
        
        ctk.CTkLabel(start_time_frame, text=":", font=ctk.CTkFont(size=12)).pack(side="left", padx=5)
        
        self.start_minute_menu = ctk.CTkOptionMenu(
            start_time_frame,
            values=[f"{i:02d}" for i in range(0, 60, 15)],
            width=60
        )
        self.start_minute_menu.pack(side="left")
        row += 1
        
        # End Time
        ctk.CTkLabel(self.editor_scroll, text="End Time:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        end_time_frame = ctk.CTkFrame(self.editor_scroll, fg_color="transparent")
        end_time_frame.grid(row=row, column=1, sticky="ew", pady=5)
        
        self.end_hour_menu = ctk.CTkOptionMenu(
            end_time_frame,
            values=[f"{i:02d}" for i in range(24)],
            width=60
        )
        self.end_hour_menu.pack(side="left")
        
        ctk.CTkLabel(end_time_frame, text=":", font=ctk.CTkFont(size=12)).pack(side="left", padx=5)
        
        self.end_minute_menu = ctk.CTkOptionMenu(
            end_time_frame,
            values=[f"{i:02d}" for i in range(0, 60, 15)],
            width=60
        )
        self.end_minute_menu.pack(side="left")
        row += 1
        
        # Break Settings
        break_title = ctk.CTkLabel(
            self.editor_scroll,
            text="Break & Lunch Settings",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['secondary']
        )
        break_title.grid(row=row, column=0, columnspan=2, sticky="w", pady=(20, 15))
        row += 1
        
        # Break Duration
        ctk.CTkLabel(self.editor_scroll, text="Break Duration (min):", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.break_duration_entry = ctk.CTkEntry(self.editor_scroll, width=250)
        self.break_duration_entry.insert(0, "15")
        self.break_duration_entry.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1
        
        # Lunch Duration
        ctk.CTkLabel(self.editor_scroll, text="Lunch Duration (min):", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.lunch_duration_entry = ctk.CTkEntry(self.editor_scroll, width=250)
        self.lunch_duration_entry.insert(0, "30")
        self.lunch_duration_entry.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1
        
        # Operational Settings
        operational_title = ctk.CTkLabel(
            self.editor_scroll,
            text="Operational Settings",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['secondary']
        )
        operational_title.grid(row=row, column=0, columnspan=2, sticky="w", pady=(20, 15))
        row += 1
        
        # Peak Hours
        self.peak_hours_check = ctk.CTkCheckBox(
            self.editor_scroll,
            text="Peak Hours Shift",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.peak_hours_check.grid(row=row, column=0, columnspan=2, sticky="w", pady=5)
        row += 1
        
        # Estimated Labor Cost
        ctk.CTkLabel(self.editor_scroll, text="Estimated Labor Cost ($):", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        self.labor_cost_entry = ctk.CTkEntry(self.editor_scroll, width=250)
        self.labor_cost_entry.insert(0, "0.00")
        self.labor_cost_entry.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1
        
        # Special Requirements
        ctk.CTkLabel(self.editor_scroll, text="Special Requirements:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=row, column=0, sticky="nw", padx=(0, 10), pady=5)
        self.requirements_textbox = ctk.CTkTextbox(self.editor_scroll, height=60, width=250)
        self.requirements_textbox.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1
        
        # Position Requirements Section
        position_title = ctk.CTkLabel(
            self.editor_scroll,
            text="Position Requirements",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['secondary']
        )
        position_title.grid(row=row, column=0, columnspan=2, sticky="w", pady=(20, 15))
        row += 1
        
        # Position requirements frame
        self.position_frame = ctk.CTkFrame(self.editor_scroll)
        self.position_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=5)
        self.position_frame.grid_columnconfigure(4, weight=1)
        
        # Headers
        headers = ["Position", "Min", "Max", "Supervisor?", ""]
        for i, header in enumerate(headers):
            ctk.CTkLabel(
                self.position_frame,
                text=header,
                font=ctk.CTkFont(size=12, weight="bold")
            ).grid(row=0, column=i, padx=5, pady=5)
        
        self.position_requirements = []
        self.create_position_requirement_row()
        row += 1
        
        # Add Position button
        self.add_position_btn = ctk.CTkButton(
            self.editor_scroll,
            text="+ Add Position Requirement",
            command=self.create_position_requirement_row,
            font=ctk.CTkFont(size=12),
            height=30
        )
        self.add_position_btn.grid(row=row, column=0, columnspan=2, pady=10)
        row += 1
    
    def create_position_requirement_row(self):
        """Create a new position requirement row"""
        row_num = len(self.position_requirements) + 1
        
        # Position selection
        position_menu = ctk.CTkOptionMenu(
            self.position_frame,
            values=[pos.value for pos in Position],
            width=120
        )
        position_menu.grid(row=row_num, column=0, padx=5, pady=5)
        
        # Minimum required
        min_entry = ctk.CTkEntry(self.position_frame, width=50)
        min_entry.insert(0, "1")
        min_entry.grid(row=row_num, column=1, padx=5, pady=5)
        
        # Maximum allowed
        max_entry = ctk.CTkEntry(self.position_frame, width=50)
        max_entry.insert(0, "2")
        max_entry.grid(row=row_num, column=2, padx=5, pady=5)
        
        # Supervisor required
        supervisor_check = ctk.CTkCheckBox(self.position_frame, text="")
        supervisor_check.grid(row=row_num, column=3, padx=5, pady=5)
        
        # Remove button
        remove_btn = ctk.CTkButton(
            self.position_frame,
            text="✕",
            width=30,
            height=30,
            command=lambda: self.remove_position_requirement_row(row_num - 1),
            fg_color=self.colors['danger']
        )
        remove_btn.grid(row=row_num, column=4, padx=5, pady=5, sticky="w")
        
        self.position_requirements.append({
            'position_menu': position_menu,
            'min_entry': min_entry,
            'max_entry': max_entry,
            'supervisor_check': supervisor_check,
            'remove_btn': remove_btn
        })
    
    def remove_position_requirement_row(self, index):
        """Remove position requirement row"""
        if len(self.position_requirements) > 1:  # Keep at least one row
            row_data = self.position_requirements[index]
            for widget in row_data.values():
                widget.destroy()
            self.position_requirements.pop(index)
            
            # Re-grid remaining rows
            for i, row_data in enumerate(self.position_requirements):
                row_num = i + 1
                for j, widget in enumerate(row_data.values()):
                    if hasattr(widget, 'grid'):
                        widget.grid(row=row_num, column=j, padx=5, pady=5)
    
    def create_toolbar(self):
        """Create toolbar with action buttons"""
        toolbar_frame = ctk.CTkFrame(self, fg_color="transparent")
        toolbar_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        # Save Template button
        self.save_btn = ctk.CTkButton(
            toolbar_frame,
            text="💾 Save Template",
            command=self.save_template,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors['success'],
            hover_color="#229954",
            height=40
        )
        self.save_btn.pack(side="left", padx=(0, 10))
        
        # New Template button
        self.new_btn = ctk.CTkButton(
            toolbar_frame,
            text="📄 New Template",
            command=self.new_template,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors['primary'],
            height=40
        )
        self.new_btn.pack(side="left", padx=(0, 10))
        
        # Delete Template button
        self.delete_btn = ctk.CTkButton(
            toolbar_frame,
            text="🗑️ Delete Template",
            command=self.delete_template,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors['danger'],
            hover_color="#C0392B",
            height=40,
            state="disabled"
        )
        self.delete_btn.pack(side="left", padx=(0, 10))
        
        # Refresh button
        self.refresh_btn = ctk.CTkButton(
            toolbar_frame,
            text="🔄 Refresh",
            command=self.load_shift_templates,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="transparent",
            text_color=self.colors['text_primary'],
            border_width=2,
            border_color=self.colors['text_secondary'],
            height=40
        )
        self.refresh_btn.pack(side="right")
    
    def load_shift_templates(self):
        """Load shift templates from database"""
        def load_data():
            try:
                # Since we don't have get_all_shift_templates yet, we'll start with empty list
                # templates = self.db_manager.get_all_shift_templates()
                templates = []
                
                # Update UI in main thread
                self.after(0, lambda: self.update_template_list(templates))
            except Exception as e:
                self.after(0, lambda: self.main_app.update_status(f"Error loading templates: {str(e)}"))
        
        # Load in background thread
        threading.Thread(target=load_data, daemon=True).start()
        self.main_app.update_status("Loading shift templates...")
    
    def update_template_list(self, templates: List[ShiftTemplate]):
        """Update template list in UI"""
        self.shift_templates = templates
        
        # Clear existing items
        for item in self.template_tree.get_children():
            self.template_tree.delete(item)
        
        # Add templates to tree
        for template in templates:
            duration = f"{template.duration_hours:.1f}h"
            cost = f"${template.estimated_labor_cost:.0f}"
            
            self.template_tree.insert("", "end", values=(
                template.name,
                template.shift_type.value,
                duration,
                cost
            ), tags=(str(template.id) if template.id else "new",))
        
        # Update count
        self.template_count_label.configure(text=f"Total Templates: {len(templates)}")
        self.main_app.update_status(f"Loaded {len(templates)} shift templates")
    
    def filter_templates(self, *args):
        """Filter templates based on type"""
        # For now, this is a placeholder since we don't have templates yet
        pass
    
    def on_template_select(self, event):
        """Handle template selection"""
        selection = self.template_tree.selection()
        if not selection:
            self.selected_template = None
            self.delete_btn.configure(state="disabled")
            return
        
        # For now, just enable delete button
        self.delete_btn.configure(state="normal")
        # TODO: Load template details into form
    
    def new_template(self):
        """Create new template"""
        self.selected_template = None
        self.delete_btn.configure(state="disabled")
        self.clear_form()
        self.main_app.update_status("Creating new shift template")
    
    def clear_form(self):
        """Clear the template form"""
        self.name_entry.delete(0, 'end')
        self.shift_type_menu.set(ShiftType.MORNING.value)
        self.priority_menu.set(ShiftPriority.NORMAL.value)
        self.start_hour_menu.set("09")
        self.start_minute_menu.set("00")
        self.end_hour_menu.set("17")
        self.end_minute_menu.set("00")
        self.break_duration_entry.delete(0, 'end')
        self.break_duration_entry.insert(0, "15")
        self.lunch_duration_entry.delete(0, 'end')
        self.lunch_duration_entry.insert(0, "30")
        self.peak_hours_check.deselect()
        self.labor_cost_entry.delete(0, 'end')
        self.labor_cost_entry.insert(0, "0.00")
        self.requirements_textbox.delete("1.0", "end")
    
    def save_template(self):
        """Save template to database"""
        try:
            # Validate required fields
            if not self.name_entry.get().strip():
                messagebox.showerror("Validation Error", "Please enter a template name.")
                return
            
            # Get form data
            template_name = self.name_entry.get().strip()
            shift_type = ShiftType(self.shift_type_menu.get())
            priority = ShiftPriority(self.priority_menu.get())
            
            start_time = time(
                int(self.start_hour_menu.get()),
                int(self.start_minute_menu.get())
            )
            end_time = time(
                int(self.end_hour_menu.get()),
                int(self.end_minute_menu.get())
            )
            
            break_duration = int(self.break_duration_entry.get() or "15")
            lunch_duration = int(self.lunch_duration_entry.get() or "30")
            is_peak_hours = self.peak_hours_check.get()
            estimated_cost = float(self.labor_cost_entry.get() or "0.0")
            special_requirements = self.requirements_textbox.get("1.0", "end-1c")
            
            # Create position requirements
            position_requirements = []
            for req_data in self.position_requirements:
                if req_data['position_menu'].get() and req_data['min_entry'].get():
                    position = Position(req_data['position_menu'].get())
                    min_required = int(req_data['min_entry'].get() or "1")
                    max_allowed = int(req_data['max_entry'].get() or "2")
                    supervisor_required = req_data['supervisor_check'].get()
                    
                    pos_req = PositionRequirement(
                        position=position,
                        minimum_required=min_required,
                        maximum_allowed=max_allowed,
                        supervisor_required=supervisor_required
                    )
                    position_requirements.append(pos_req)
            
            # Create template
            template = ShiftTemplate(
                name=template_name,
                shift_type=shift_type,
                start_time=start_time,
                end_time=end_time,
                break_duration_minutes=break_duration,
                lunch_duration_minutes=lunch_duration,
                is_peak_hours=is_peak_hours,
                priority=priority,
                special_requirements=special_requirements,
                estimated_labor_cost=estimated_cost,
                position_requirements=position_requirements
            )
            
            # Save to database
            template_id = self.db_manager.add_shift_template(template)
            
            self.main_app.update_status(f"Shift template '{template_name}' saved successfully")
            messagebox.showinfo("Success", f"Shift template '{template_name}' has been saved.")
            
            # Refresh template list
            self.load_shift_templates()
            
        except ValueError as e:
            messagebox.showerror("Validation Error", f"Please check your input values:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save template:\n{str(e)}")
    
    def delete_template(self):
        """Delete selected template"""
        if not self.selected_template:
            return
        
        result = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete the template '{self.selected_template.name}'?\n\n"
            "This action cannot be undone.",
            icon="warning"
        )
        
        if result:
            try:
                # TODO: Implement delete_shift_template in database manager
                # self.db_manager.delete_shift_template(self.selected_template.id)
                
                self.main_app.update_status(f"Template '{self.selected_template.name}' deleted")
                self.load_shift_templates()
                self.new_template()  # Clear form
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete template:\n{str(e)}") 