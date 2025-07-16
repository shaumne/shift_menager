import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, font
import os
import sys
import logging
from database.db_manager import DatabaseManager
from ui.employee_manager import EmployeeManager
from ui.shift_creator import ShiftCreator  
from ui.calendar_view import CalendarView
from ui.reports_dashboard import ReportsDashboard
from ui.settings_manager import SettingsManager
from utils.demo_data import DemoDataGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class ShiftManager:
    def __init__(self):
        self.root = ctk.CTk()
        self.setup_window()
        self.setup_theme()
        self.root.title("Restaurant Shift Management System")
        
        # Initialize database
        self.db_manager = DatabaseManager("shifts.db")
        
        # Restaurant color scheme
        self.colors = {
            'primary': '#FFC72C',      # Golden Yellow
            'secondary': '#DA020E',    # Red
            'dark_bg': '#1a1a1a',
            'medium_bg': '#2d2d2d', 
            'light_bg': '#404040',
            'text_light': '#ffffff',
            'text_dark': '#333333',
            'success': '#00AA00',
            'warning': '#FF8800',
            'error': '#FF0000'
        }
        
        # Always on top state
        self.always_on_top = False
        
        self.create_sidebar()
        self.create_main_content()
        self.create_status_bar()
        
        # Bind keyboard shortcuts
        self.bind_shortcuts()
        
        # Set default view
        self.show_employee_manager()
        
        logger.info("Restaurant Shift Management System initialized successfully")
    
    def setup_window(self):
        """Configure main window properties"""
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Center window on screen
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_theme(self):
        """Setup application theme"""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
    
    def create_sidebar(self):
        """Create navigation sidebar"""
        # Main container
        self.main_container = ctk.CTkFrame(self.root)
        self.main_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Sidebar frame
        self.sidebar = ctk.CTkFrame(self.main_container, width=250, corner_radius=10)
        self.sidebar.pack(side="left", fill="y", padx=(0, 10), pady=0)
        self.sidebar.pack_propagate(False)
        
        # Logo/Title section
        title_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        title_frame.pack(fill="x", padx=10, pady=(10, 20))
        
        logo_label = ctk.CTkLabel(
            title_frame,
            text="Restaurant",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors['primary']
        )
        logo_label.pack()
        
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="Shift Manager",
            font=ctk.CTkFont(size=16),
            text_color=self.colors['text_light']
        )
        subtitle_label.pack()
        
        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("👥 Employee Manager", self.show_employee_manager),
            ("📅 Shift Creator", self.show_shift_creator),
            ("🗓️ Calendar View", self.show_calendar_view),
            ("📊 Reports", self.show_reports),
            ("⚙️ Settings", self.show_settings),
            ("🎲 Demo Data", self.show_demo_data_dialog)
        ]
        
        for text, command in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=command,
                height=45,
                font=ctk.CTkFont(size=14),
                corner_radius=8,
                fg_color="transparent",
                hover_color=self.colors['light_bg']
            )
            btn.pack(fill="x", padx=15, pady=5)
            self.nav_buttons[text] = btn
            
        # Utility buttons at bottom
        bottom_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        
        # Always on top toggle
        self.always_on_top_var = tk.BooleanVar()
        always_on_top_check = ctk.CTkCheckBox(
            bottom_frame,
            text="Always on Top",
            variable=self.always_on_top_var,
            command=self.toggle_always_on_top,
            font=ctk.CTkFont(size=12)
        )
        always_on_top_check.pack(pady=5)
        
        # Help button
        help_btn = ctk.CTkButton(
            bottom_frame,
            text="❓ Help (F1)",
            command=self.show_help,
            height=35,
            font=ctk.CTkFont(size=12),
            fg_color=self.colors['secondary'],
            hover_color="#B01E0E"
        )
        help_btn.pack(fill="x", pady=5)
    
    def create_main_content(self):
        """Create main content area"""
        self.content_frame = ctk.CTkFrame(self.main_container, corner_radius=10)
        self.content_frame.pack(side="right", fill="both", expand=True)
        
        # Content will be dynamically loaded here
        self.current_view = None
        
    def create_status_bar(self):
        """Create status bar at bottom"""
        self.status_frame = ctk.CTkFrame(self.root, height=30, corner_radius=0)
        self.status_frame.pack(side="bottom", fill="x")
        self.status_frame.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready",
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
        # Version info
        version_label = ctk.CTkLabel(
            self.status_frame,
            text="v1.0.0",
            font=ctk.CTkFont(size=12),
            anchor="e"
        )
        version_label.pack(side="right", padx=10, pady=5)
        
    def update_status(self, message):
        """Update status bar message"""
        self.status_label.configure(text=message)
        self.root.update_idletasks()
        
    def highlight_nav_button(self, active_text):
        """Highlight active navigation button"""
        for text, btn in self.nav_buttons.items():
            if text == active_text:
                btn.configure(fg_color=self.colors['primary'], text_color=self.colors['text_dark'])
            else:
                btn.configure(fg_color="transparent", text_color=self.colors['text_light'])
    
    def clear_content(self):
        """Clear current content"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_employee_manager(self):
        """Show employee management interface"""
        self.clear_content()
        self.highlight_nav_button("👥 Employee Manager")
        self.update_status("Employee Manager")
        
        self.current_view = EmployeeManager(self.content_frame, self.db_manager, self.colors)
        logger.info("Employee Manager view loaded")
    
    def show_shift_creator(self):
        """Show shift creation interface"""
        self.clear_content() 
        self.highlight_nav_button("📅 Shift Creator")
        self.update_status("Shift Creator")
        
        self.current_view = ShiftCreator(self.content_frame, self.db_manager, self.colors)
        logger.info("Shift Creator view loaded")
    
    def show_calendar_view(self):
        """Show calendar interface"""
        self.clear_content()
        self.highlight_nav_button("🗓️ Calendar View")
        self.update_status("Calendar View")
        
        self.current_view = CalendarView(self.content_frame, self.db_manager, self.colors)
        logger.info("Calendar View loaded")
    
    def show_reports(self):
        """Show reports dashboard"""
        self.clear_content()
        self.highlight_nav_button("📊 Reports")
        self.update_status("Reports Dashboard")
        
        self.current_view = ReportsDashboard(self.content_frame, self.db_manager, self.colors)
        logger.info("Reports Dashboard loaded")
    
    def show_settings(self):
        """Show settings interface"""
        self.clear_content()
        self.highlight_nav_button("⚙️ Settings")
        self.update_status("Settings")
        
        self.current_view = SettingsManager(self.content_frame, self.db_manager, self.colors)
        logger.info("Settings view loaded")
    
    def show_demo_data_dialog(self):
        """Show demo data generation dialog"""
        result = messagebox.askyesno(
            "Generate Demo Data",
            "This will add sample restaurant employees and shift templates to your database.\n\n"
            "⚠️ Warning: This will create sample data. Are you sure you want to continue?",
            icon="question"
        )
        
        if result:
            try:
                generator = DemoDataGenerator(self.db_manager)
                generator.generate_all_demo_data()
                
                messagebox.showinfo(
                    "Success",
                    "✅ Demo data generated successfully!\n\n"
                    "• 20 Sample employees created\n"
                    "• Shift templates added\n"
                    "• Sample schedules generated\n\n"
                    "You can now explore all features with realistic data."
                )
                
                # Refresh current view if possible
                if hasattr(self.current_view, 'refresh'):
                    self.current_view.refresh()
                    
                self.update_status("Demo data generated successfully")
                logger.info("Demo data generated successfully")
                
            except Exception as e:
                logger.error(f"Error generating demo data: {e}")
                messagebox.showerror(
                    "Error",
                    f"Failed to generate demo data:\n\n{str(e)}"
                )
    
    def bind_shortcuts(self):
        """Bind keyboard shortcuts"""
        # Navigation shortcuts
        self.root.bind('<Control-Key-1>', lambda e: self.show_employee_manager())
        self.root.bind('<Control-Key-2>', lambda e: self.show_shift_creator())
        self.root.bind('<Control-Key-3>', lambda e: self.show_calendar_view())
        self.root.bind('<Control-Key-4>', lambda e: self.show_reports())
        self.root.bind('<Control-Key-5>', lambda e: self.show_settings())
        self.root.bind('<Control-Key-6>', lambda e: self.show_demo_data_dialog())
        
        # Utility shortcuts
        self.root.bind('<F1>', lambda e: self.show_help())
        self.root.bind('<F5>', lambda e: self.refresh_current_view())
        self.root.bind('<F11>', lambda e: self.toggle_fullscreen())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        
        # Focus the root window to receive key events
        self.root.focus_set()
    
    def refresh_current_view(self):
        """Refresh current view"""
        if hasattr(self.current_view, 'refresh'):
            self.current_view.refresh()
            self.update_status("View refreshed")
        else:
            self.update_status("Current view does not support refresh")
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        current_state = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current_state)
        self.update_status("Fullscreen toggled")
    
    def toggle_always_on_top(self):
        """Toggle always on top"""
        self.always_on_top = self.always_on_top_var.get()
        self.root.attributes('-topmost', self.always_on_top)
        status = "enabled" if self.always_on_top else "disabled"
        self.update_status(f"Always on top {status}")
        
    def show_help(self):
        """Show help dialog with shortcuts"""
        help_text = """
Restaurant Shift Management System - Keyboard Shortcuts

Navigation:
• Ctrl+1: Employee Manager
• Ctrl+2: Shift Creator  
• Ctrl+3: Calendar View
• Ctrl+4: Reports
• Ctrl+5: Settings
• Ctrl+6: Generate Demo Data

Utility:
• F1: Show this help
• F5: Refresh current view
• F11: Toggle fullscreen
• Ctrl+Q: Quit application

Mouse:
• Right-click: Context menus (where available)
• Double-click: Quick actions (where available)

Tips:
• Use demo data to explore features
• Check status bar for current operations
• All data is automatically saved
"""
        
        # Create help window
        help_window = ctk.CTkToplevel(self.root)
        help_window.title("Help - Keyboard Shortcuts")
        help_window.geometry("500x400")
        help_window.transient(self.root)
        help_window.grab_set()
        
        # Center on parent
        help_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (500 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (400 // 2)
        help_window.geometry(f"500x400+{x}+{y}")
        
        # Help content
        text_widget = ctk.CTkTextbox(
            help_window,
            font=ctk.CTkFont(family="Consolas", size=12),
            wrap="word"
        )
        text_widget.pack(fill="both", expand=True, padx=20, pady=20)
        text_widget.insert("0.0", help_text)
        text_widget.configure(state="disabled")
        
        # Close button
        close_btn = ctk.CTkButton(
            help_window,
            text="Close",
            command=help_window.destroy,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        close_btn.pack(pady=(0, 20))
        
        # You could add a restaurant icon here
        
    def run(self):
        """Start the application"""
        logger.info("Starting Restaurant Shift Management System...")
        self.root.mainloop()

if __name__ == "__main__":
    app = ShiftManager()
    app.run() 