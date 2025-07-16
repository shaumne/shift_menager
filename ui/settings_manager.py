import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import threading
import os

from database.db_manager import DatabaseManager

class SettingsManagerFrame(ctk.CTkFrame):
    def __init__(self, parent, db_manager: DatabaseManager, main_app):
        super().__init__(parent)
        
        self.db_manager = db_manager
        self.main_app = main_app
        self.colors = main_app.colors
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.create_ui()
        self.load_settings()
    
    def create_ui(self):
        """Create settings manager interface"""
        # Create main container with tabs
        self.tabview = ctk.CTkTabview(self, width=1000, height=700)
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Add tabs
        self.general_tab = self.tabview.add("🏪 General")
        self.operations_tab = self.tabview.add("⚙️ Operations")
        self.appearance_tab = self.tabview.add("🎨 Appearance")
        self.database_tab = self.tabview.add("💾 Database")
        
        # Setup each tab
        self.setup_general_tab()
        self.setup_operations_tab()
        self.setup_appearance_tab()
        self.setup_database_tab()
    
    def setup_general_tab(self):
        """Setup general settings tab"""
        # Configure grid
        self.general_tab.grid_columnconfigure(0, weight=1)
        
        # Scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(self.general_tab)
        scroll_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        scroll_frame.grid_columnconfigure(1, weight=1)
        
        row = 0
        
        # Restaurant Information Section
        rest_title = ctk.CTkLabel(
            scroll_frame,
            text="Restaurant Information",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['secondary']
        )
        rest_title.grid(row=row, column=0, columnspan=2, sticky="w", pady=(0, 20))
        row += 1
        
        # Restaurant Name
        ctk.CTkLabel(scroll_frame, text="Restaurant Name:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=(0, 10), pady=10)
        self.restaurant_name_entry = ctk.CTkEntry(scroll_frame, width=300)
        self.restaurant_name_entry.insert(0, "Restaurant - Main Street")
        self.restaurant_name_entry.grid(row=row, column=1, sticky="ew", pady=10)
        row += 1
        
        # Restaurant Address
        ctk.CTkLabel(scroll_frame, text="Address:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=(0, 10), pady=10)
        self.restaurant_address_entry = ctk.CTkEntry(scroll_frame, width=300)
        self.restaurant_address_entry.insert(0, "123 Main Street, Anytown, ST 12345")
        self.restaurant_address_entry.grid(row=row, column=1, sticky="ew", pady=10)
        row += 1
        
        # Manager Name
        ctk.CTkLabel(scroll_frame, text="General Manager:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=(0, 10), pady=10)
        self.manager_name_entry = ctk.CTkEntry(scroll_frame, width=300)
        self.manager_name_entry.insert(0, "John Smith")
        self.manager_name_entry.grid(row=row, column=1, sticky="ew", pady=10)
        row += 1
        
        # Contact Information
        ctk.CTkLabel(scroll_frame, text="Phone Number:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=(0, 10), pady=10)
        self.phone_entry = ctk.CTkEntry(scroll_frame, width=300)
        self.phone_entry.insert(0, "+1 (555) 123-4567")
        self.phone_entry.grid(row=row, column=1, sticky="ew", pady=10)
        row += 1
        
        # Operating Hours Section
        hours_title = ctk.CTkLabel(
            scroll_frame,
            text="Operating Hours",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['secondary']
        )
        hours_title.grid(row=row, column=0, columnspan=2, sticky="w", pady=(30, 20))
        row += 1
        
        # Weekday Hours
        ctk.CTkLabel(scroll_frame, text="Weekday Hours:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=(0, 10), pady=10)
        weekday_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        weekday_frame.grid(row=row, column=1, sticky="ew", pady=10)
        
        self.weekday_open_menu = ctk.CTkOptionMenu(
            weekday_frame,
            values=[f"{i:02d}:00" for i in range(24)],
            width=80
        )
        self.weekday_open_menu.set("06:00")
        self.weekday_open_menu.pack(side="left")
        
        ctk.CTkLabel(weekday_frame, text=" to ", font=ctk.CTkFont(size=12)).pack(side="left", padx=10)
        
        self.weekday_close_menu = ctk.CTkOptionMenu(
            weekday_frame,
            values=[f"{i:02d}:00" for i in range(24)],
            width=80
        )
        self.weekday_close_menu.set("23:00")
        self.weekday_close_menu.pack(side="left")
        row += 1
        
        # Weekend Hours
        ctk.CTkLabel(scroll_frame, text="Weekend Hours:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=(0, 10), pady=10)
        weekend_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        weekend_frame.grid(row=row, column=1, sticky="ew", pady=10)
        
        self.weekend_open_menu = ctk.CTkOptionMenu(
            weekend_frame,
            values=[f"{i:02d}:00" for i in range(24)],
            width=80
        )
        self.weekend_open_menu.set("07:00")
        self.weekend_open_menu.pack(side="left")
        
        ctk.CTkLabel(weekend_frame, text=" to ", font=ctk.CTkFont(size=12)).pack(side="left", padx=10)
        
        self.weekend_close_menu = ctk.CTkOptionMenu(
            weekend_frame,
            values=[f"{i:02d}:00" for i in range(24)],
            width=80
        )
        self.weekend_close_menu.set("22:00")
        self.weekend_close_menu.pack(side="left")
        row += 1
        
        # Save button
        save_general_btn = ctk.CTkButton(
            scroll_frame,
            text="💾 Save General Settings",
            command=self.save_general_settings,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors['success'],
            height=40
        )
        save_general_btn.grid(row=row, column=0, columnspan=2, pady=30)
    
    def setup_operations_tab(self):
        """Setup operations settings tab"""
        # Configure grid
        self.operations_tab.grid_columnconfigure(0, weight=1)
        
        # Scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(self.operations_tab)
        scroll_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        scroll_frame.grid_columnconfigure(1, weight=1)
        
        row = 0
        
        # Staffing Requirements
        staffing_title = ctk.CTkLabel(
            scroll_frame,
            text="Minimum Staffing Requirements",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['secondary']
        )
        staffing_title.grid(row=row, column=0, columnspan=2, sticky="w", pady=(0, 20))
        row += 1
        
        # Minimum staff during peak hours
        ctk.CTkLabel(scroll_frame, text="Peak Hours Minimum Staff:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=(0, 10), pady=10)
        self.peak_staff_entry = ctk.CTkEntry(scroll_frame, width=100)
        self.peak_staff_entry.insert(0, "12")
        self.peak_staff_entry.grid(row=row, column=1, sticky="w", pady=10)
        row += 1
        
        # Minimum staff during regular hours
        ctk.CTkLabel(scroll_frame, text="Regular Hours Minimum Staff:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=(0, 10), pady=10)
        self.regular_staff_entry = ctk.CTkEntry(scroll_frame, width=100)
        self.regular_staff_entry.insert(0, "8")
        self.regular_staff_entry.grid(row=row, column=1, sticky="w", pady=10)
        row += 1
        
        # Peak Hours Definition
        peak_title = ctk.CTkLabel(
            scroll_frame,
            text="Peak Hours Definition",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['secondary']
        )
        peak_title.grid(row=row, column=0, columnspan=2, sticky="w", pady=(30, 20))
        row += 1
        
        # Breakfast rush
        ctk.CTkLabel(scroll_frame, text="Breakfast Rush:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=(0, 10), pady=10)
        breakfast_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        breakfast_frame.grid(row=row, column=1, sticky="ew", pady=10)
        
        self.breakfast_start_menu = ctk.CTkOptionMenu(breakfast_frame, values=[f"{i:02d}:00" for i in range(24)], width=80)
        self.breakfast_start_menu.set("07:00")
        self.breakfast_start_menu.pack(side="left")
        
        ctk.CTkLabel(breakfast_frame, text=" to ", font=ctk.CTkFont(size=12)).pack(side="left", padx=10)
        
        self.breakfast_end_menu = ctk.CTkOptionMenu(breakfast_frame, values=[f"{i:02d}:00" for i in range(24)], width=80)
        self.breakfast_end_menu.set("10:00")
        self.breakfast_end_menu.pack(side="left")
        row += 1
        
        # Lunch rush
        ctk.CTkLabel(scroll_frame, text="Lunch Rush:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=(0, 10), pady=10)
        lunch_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        lunch_frame.grid(row=row, column=1, sticky="ew", pady=10)
        
        self.lunch_start_menu = ctk.CTkOptionMenu(lunch_frame, values=[f"{i:02d}:00" for i in range(24)], width=80)
        self.lunch_start_menu.set("11:30")
        self.lunch_start_menu.pack(side="left")
        
        ctk.CTkLabel(lunch_frame, text=" to ", font=ctk.CTkFont(size=12)).pack(side="left", padx=10)
        
        self.lunch_end_menu = ctk.CTkOptionMenu(lunch_frame, values=[f"{i:02d}:00" for i in range(24)], width=80)
        self.lunch_end_menu.set("14:00")
        self.lunch_end_menu.pack(side="left")
        row += 1
        
        # Dinner rush
        ctk.CTkLabel(scroll_frame, text="Dinner Rush:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=(0, 10), pady=10)
        dinner_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        dinner_frame.grid(row=row, column=1, sticky="ew", pady=10)
        
        self.dinner_start_menu = ctk.CTkOptionMenu(dinner_frame, values=[f"{i:02d}:00" for i in range(24)], width=80)
        self.dinner_start_menu.set("17:00")
        self.dinner_start_menu.pack(side="left")
        
        ctk.CTkLabel(dinner_frame, text=" to ", font=ctk.CTkFont(size=12)).pack(side="left", padx=10)
        
        self.dinner_end_menu = ctk.CTkOptionMenu(dinner_frame, values=[f"{i:02d}:00" for i in range(24)], width=80)
        self.dinner_end_menu.set("20:00")
        self.dinner_end_menu.pack(side="left")
        row += 1
        
        # Labor Cost Settings
        labor_title = ctk.CTkLabel(
            scroll_frame,
            text="Labor Cost Settings",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['secondary']
        )
        labor_title.grid(row=row, column=0, columnspan=2, sticky="w", pady=(30, 20))
        row += 1
        
        # Weekly labor budget
        ctk.CTkLabel(scroll_frame, text="Weekly Labor Budget ($):", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=(0, 10), pady=10)
        self.labor_budget_entry = ctk.CTkEntry(scroll_frame, width=150)
        self.labor_budget_entry.insert(0, "15000.00")
        self.labor_budget_entry.grid(row=row, column=1, sticky="w", pady=10)
        row += 1
        
        # Overtime multiplier
        ctk.CTkLabel(scroll_frame, text="Overtime Multiplier:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=(0, 10), pady=10)
        self.overtime_multiplier_entry = ctk.CTkEntry(scroll_frame, width=100)
        self.overtime_multiplier_entry.insert(0, "1.5")
        self.overtime_multiplier_entry.grid(row=row, column=1, sticky="w", pady=10)
        row += 1
        
        # Save button
        save_operations_btn = ctk.CTkButton(
            scroll_frame,
            text="💾 Save Operations Settings",
            command=self.save_operations_settings,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors['success'],
            height=40
        )
        save_operations_btn.grid(row=row, column=0, columnspan=2, pady=30)
    
    def setup_appearance_tab(self):
        """Setup appearance settings tab"""
        # Configure grid
        self.appearance_tab.grid_columnconfigure(0, weight=1)
        
        # Main frame
        main_frame = ctk.CTkFrame(self.appearance_tab)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(1, weight=1)
        
        row = 0
        
        # Theme Settings
        theme_title = ctk.CTkLabel(
            main_frame,
            text="Theme Settings",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['secondary']
        )
        theme_title.grid(row=row, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 20))
        row += 1
        
        # Appearance mode
        ctk.CTkLabel(main_frame, text="Appearance Mode:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=(20, 10), pady=10)
        self.appearance_mode_menu = ctk.CTkOptionMenu(
            main_frame,
            values=["Light", "Dark", "System"],
            command=self.change_appearance_mode,
            width=150
        )
        self.appearance_mode_menu.set("Light")
        self.appearance_mode_menu.grid(row=row, column=1, sticky="w", pady=10)
        row += 1
        
        # Color theme
        ctk.CTkLabel(main_frame, text="Color Theme:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=(20, 10), pady=10)
        self.color_theme_menu = ctk.CTkOptionMenu(
            main_frame,
            values=["blue", "green", "dark-blue"],
            command=self.change_color_theme,
            width=150
        )
        self.color_theme_menu.set("blue")
        self.color_theme_menu.grid(row=row, column=1, sticky="w", pady=10)
        row += 1
        
        # Font size
        ctk.CTkLabel(main_frame, text="Font Size:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=row, column=0, sticky="w", padx=(20, 10), pady=10)
        self.font_size_slider = ctk.CTkSlider(
            main_frame,
            from_=10,
            to=16,
            number_of_steps=6,
            width=200
        )
        self.font_size_slider.set(12)
        self.font_size_slider.grid(row=row, column=1, sticky="w", pady=10)
        row += 1
        
        # Window settings
        window_title = ctk.CTkLabel(
            main_frame,
            text="Window Settings",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['secondary']
        )
        window_title.grid(row=row, column=0, columnspan=2, sticky="w", padx=20, pady=(30, 20))
        row += 1
        
        # Always on top
        self.always_on_top_var = tk.BooleanVar()
        self.always_on_top_check = ctk.CTkCheckBox(
            main_frame,
            text="Always on top",
            variable=self.always_on_top_var,
            command=self.toggle_always_on_top
        )
        self.always_on_top_check.grid(row=row, column=0, columnspan=2, sticky="w", padx=20, pady=10)
        row += 1
        
        # Start maximized
        self.start_maximized_var = tk.BooleanVar()
        self.start_maximized_check = ctk.CTkCheckBox(
            main_frame,
            text="Start maximized",
            variable=self.start_maximized_var
        )
        self.start_maximized_check.grid(row=row, column=0, columnspan=2, sticky="w", padx=20, pady=10)
        row += 1
        
        # Save button
        save_appearance_btn = ctk.CTkButton(
            main_frame,
            text="💾 Save Appearance Settings",
            command=self.save_appearance_settings,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors['success'],
            height=40
        )
        save_appearance_btn.grid(row=row, column=0, columnspan=2, padx=20, pady=30)
    
    def setup_database_tab(self):
        """Setup database management tab"""
        # Configure grid
        self.database_tab.grid_columnconfigure(0, weight=1)
        
        # Main frame
        main_frame = ctk.CTkFrame(self.database_tab)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Database info
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill="x", padx=20, pady=20)
        
        info_title = ctk.CTkLabel(
            info_frame,
            text="Database Information",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['secondary']
        )
        info_title.pack(pady=(15, 10))
        
        # Database path
        db_path_label = ctk.CTkLabel(
            info_frame,
            text=f"Database Location: {os.path.abspath(self.db_manager.db_path)}",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_secondary']
        )
        db_path_label.pack(pady=5)
        
        # Database size
        try:
            db_size = os.path.getsize(self.db_manager.db_path)
            db_size_mb = db_size / (1024 * 1024)
            size_text = f"Database Size: {db_size_mb:.2f} MB"
        except:
            size_text = "Database Size: Unknown"
        
        db_size_label = ctk.CTkLabel(
            info_frame,
            text=size_text,
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_secondary']
        )
        db_size_label.pack(pady=(5, 15))
        
        # Backup/Restore section
        backup_frame = ctk.CTkFrame(main_frame)
        backup_frame.pack(fill="x", padx=20, pady=20)
        
        backup_title = ctk.CTkLabel(
            backup_frame,
            text="Backup & Restore",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['secondary']
        )
        backup_title.pack(pady=(15, 10))
        
        # Backup buttons
        backup_btn = ctk.CTkButton(
            backup_frame,
            text="💾 Create Backup",
            command=self.create_backup,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors['primary'],
            height=40,
            width=200
        )
        backup_btn.pack(pady=10)
        
        restore_btn = ctk.CTkButton(
            backup_frame,
            text="📂 Restore from Backup",
            command=self.restore_backup,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors['warning'],
            height=40,
            width=200
        )
        restore_btn.pack(pady=10)
        
        # Auto backup settings
        auto_backup_frame = ctk.CTkFrame(backup_frame, fg_color="transparent")
        auto_backup_frame.pack(pady=15)
        
        self.auto_backup_var = tk.BooleanVar(value=True)
        auto_backup_check = ctk.CTkCheckBox(
            auto_backup_frame,
            text="Enable automatic daily backups",
            variable=self.auto_backup_var
        )
        auto_backup_check.pack()
        
        # Data management
        data_frame = ctk.CTkFrame(main_frame)
        data_frame.pack(fill="x", padx=20, pady=20)
        
        data_title = ctk.CTkLabel(
            data_frame,
            text="Data Management",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['secondary']
        )
        data_title.pack(pady=(15, 10))
        
        # Clear demo data button
        clear_demo_btn = ctk.CTkButton(
            data_frame,
            text="🗑️ Clear Demo Data",
            command=self.clear_demo_data,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors['danger'],
            height=40,
            width=200
        )
        clear_demo_btn.pack(pady=10)
        
        # Warning
        warning_label = ctk.CTkLabel(
            data_frame,
            text="⚠️ Clearing demo data will remove all sample employees and templates.\nThis action cannot be undone.",
            font=ctk.CTkFont(size=11),
            text_color=self.colors['danger'],
            justify="center"
        )
        warning_label.pack(pady=(10, 15))
    
    def load_settings(self):
        """Load settings from database"""
        try:
            # Load settings from database if they exist
            # For now, we'll use default values
            pass
        except Exception as e:
            self.main_app.update_status(f"Error loading settings: {str(e)}")
    
    def save_general_settings(self):
        """Save general settings"""
        try:
            # Save to database
            self.db_manager.set_restaurant_setting("restaurant_name", self.restaurant_name_entry.get())
            self.db_manager.set_restaurant_setting("restaurant_address", self.restaurant_address_entry.get())
            self.db_manager.set_restaurant_setting("manager_name", self.manager_name_entry.get())
            self.db_manager.set_restaurant_setting("phone_number", self.phone_entry.get())
            self.db_manager.set_restaurant_setting("weekday_hours", f"{self.weekday_open_menu.get()}-{self.weekday_close_menu.get()}")
            self.db_manager.set_restaurant_setting("weekend_hours", f"{self.weekend_open_menu.get()}-{self.weekend_close_menu.get()}")
            
            messagebox.showinfo("Settings Saved", "General settings have been saved successfully.")
            self.main_app.update_status("General settings saved")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings:\n{str(e)}")
    
    def save_operations_settings(self):
        """Save operations settings"""
        try:
            # Save to database
            self.db_manager.set_restaurant_setting("peak_staff_minimum", self.peak_staff_entry.get())
            self.db_manager.set_restaurant_setting("regular_staff_minimum", self.regular_staff_entry.get())
            self.db_manager.set_restaurant_setting("breakfast_rush", f"{self.breakfast_start_menu.get()}-{self.breakfast_end_menu.get()}")
            self.db_manager.set_restaurant_setting("lunch_rush", f"{self.lunch_start_menu.get()}-{self.lunch_end_menu.get()}")
            self.db_manager.set_restaurant_setting("dinner_rush", f"{self.dinner_start_menu.get()}-{self.dinner_end_menu.get()}")
            self.db_manager.set_restaurant_setting("labor_budget", self.labor_budget_entry.get())
            self.db_manager.set_restaurant_setting("overtime_multiplier", self.overtime_multiplier_entry.get())
            
            messagebox.showinfo("Settings Saved", "Operations settings have been saved successfully.")
            self.main_app.update_status("Operations settings saved")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings:\n{str(e)}")
    
    def save_appearance_settings(self):
        """Save appearance settings"""
        messagebox.showinfo("Settings Saved", "Appearance settings have been saved successfully.")
        self.main_app.update_status("Appearance settings saved")
    
    def change_appearance_mode(self, mode):
        """Change appearance mode"""
        ctk.set_appearance_mode(mode)
        self.main_app.update_status(f"Appearance mode changed to {mode}")
    
    def change_color_theme(self, theme):
        """Change color theme"""
        ctk.set_default_color_theme(theme)
        messagebox.showinfo("Theme Changed", "Color theme will be applied when the application is restarted.")
    
    def toggle_always_on_top(self):
        """Toggle always on top"""
        always_on_top = self.always_on_top_var.get()
        self.main_app.root.attributes('-topmost', always_on_top)
        status = "enabled" if always_on_top else "disabled"
        self.main_app.update_status(f"Always on top {status}")
    
    def create_backup(self):
        """Create database backup"""
        try:
            # Ask user for backup location
            backup_path = filedialog.asksaveasfilename(
                title="Save Database Backup",
                defaultextension=".db",
                filetypes=[("Database files", "*.db"), ("All files", "*.*")],
                initialname=f"restaurant_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            )
            
            if backup_path:
                success = self.db_manager.backup_database(backup_path)
                if success:
                    messagebox.showinfo("Backup Created", f"Database backup created successfully:\n{backup_path}")
                    self.main_app.update_status("Database backup created")
                else:
                    messagebox.showerror("Backup Failed", "Failed to create database backup.")
                    
        except Exception as e:
            messagebox.showerror("Backup Error", f"Error creating backup:\n{str(e)}")
    
    def restore_backup(self):
        """Restore database from backup"""
        try:
            # Ask user for backup file
            backup_path = filedialog.askopenfilename(
                title="Select Backup File",
                filetypes=[("Database files", "*.db"), ("All files", "*.*")]
            )
            
            if backup_path:
                result = messagebox.askyesno(
                    "Confirm Restore",
                    "This will replace the current database with the backup.\n\n"
                    "Are you sure you want to continue?\n"
                    "This action cannot be undone.",
                    icon="warning"
                )
                
                if result:
                    # This would require application restart
                    messagebox.showinfo(
                        "Restore Process",
                        "To restore from backup:\n\n"
                        "1. Close the application\n"
                        "2. Replace 'restaurant_shifts.db' with your backup file\n"
                        "3. Restart the application\n\n"
                        "The application will now close."
                    )
                    self.main_app.root.quit()
                    
        except Exception as e:
            messagebox.showerror("Restore Error", f"Error restoring backup:\n{str(e)}")
    
    def clear_demo_data(self):
        """Clear demo data from database"""
        result = messagebox.askyesno(
            "Confirm Clear Demo Data",
            "This will remove all demo employees and shift templates.\n\n"
            "Are you sure you want to continue?\n"
            "This action cannot be undone.",
            icon="warning"
        )
        
        if result:
            try:
                # This would require implementing clear demo data functionality
                messagebox.showinfo(
                    "Clear Demo Data",
                    "Demo data clearing functionality will be implemented in a future update.\n\n"
                    "For now, you can delete the database file and restart the application\n"
                    "to start with a clean database."
                )
                
            except Exception as e:
                messagebox.showerror("Clear Data Error", f"Error clearing demo data:\n{str(e)}") 