# Restaurant Shift Management System

Professional Windows desktop application for managing employee schedules, shifts, and labor costs designed for restaurant operations.

## Features

### 🎯 Core Management
- **Employee Management**: Complete employee profiles with positions, skills, and availability
- **Shift Creation**: Flexible shift templates with position requirements
- **Schedule Planning**: Interactive calendar view with drag-and-drop scheduling
- **Labor Cost Tracking**: Real-time labor cost calculations and budget management

### 📊 Analytics & Reporting
- **Performance Metrics**: Employee attendance, punctuality, and performance tracking
- **Labor Analytics**: Detailed cost analysis and optimization suggestions
- **Schedule Reports**: Comprehensive scheduling reports with export capabilities
- **Dashboard Overview**: Real-time business metrics and KPIs

### 💼 Professional Features
- **Advanced Filtering**: Multi-criteria employee and shift filtering
- **Excel Export**: Export employee data and reports to Excel
- **Backup & Restore**: Complete database backup and restoration
- **Keyboard Shortcuts**: Efficient navigation with professional hotkeys

### 🎨 User Experience
- **Modern UI**: Clean, professional interface with restaurant branding
- **Dark Theme**: Professional appearance with golden yellow and red accents
- **Responsive Design**: Optimized for Windows desktop environments
- **Status Tracking**: Real-time status updates and operation feedback

### 🔧 Technical Excellence
- **Restaurant Branding**: Professional color scheme and design language
- **Production Ready**: Enterprise-grade code quality and error handling
- **Scalable Architecture**: Clean separation of concerns with modular design
- **Data Integrity**: Comprehensive validation and database management

## Installation

### Requirements
- Windows 10/11
- Python 3.8 or higher
- 4GB RAM minimum
- 100MB free disk space

### Quick Start
1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd shift-management
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Application**
   ```bash
   python main.py
   ```

### First Time Setup
1. Launch the application
2. Click "🎲 Demo Data" to populate with sample employees
3. Explore all features with realistic test data
4. Configure settings for your restaurant

## Usage Guide

### Employee Management
- **Add Employees**: Complete profiles with contact info, positions, and skills
- **Track Performance**: Monitor attendance, punctuality, and customer ratings
- **Manage Availability**: Set employee availability schedules
- **Export Data**: Generate Excel reports for payroll and HR

### Shift Planning
- **Create Templates**: Design reusable shift patterns
- **Assign Staff**: Match employees to shifts based on skills and availability
- **Calculate Costs**: Real-time labor cost tracking and budget management
- **Schedule Optimization**: Intelligent suggestions for optimal staffing

### Reporting & Analytics
- **Performance Dashboard**: Real-time metrics and KPIs
- **Labor Cost Analysis**: Detailed breakdown of labor expenses
- **Schedule Reports**: Comprehensive shift and employee reports
- **Export Capabilities**: Excel export for all major reports

### Settings & Configuration
- **Restaurant Info**: Configure restaurant details and branding
- **Operational Settings**: Set peak hours, labor targets, and preferences
- **Appearance**: Customize UI themes and display options
- **Data Management**: Backup and restore database functionality

## Keyboard Shortcuts

### Navigation
- `Ctrl+1`: Employee Manager
- `Ctrl+2`: Shift Creator
- `Ctrl+3`: Calendar View
- `Ctrl+4`: Reports Dashboard
- `Ctrl+5`: Settings
- `Ctrl+6`: Generate Demo Data

### Utility
- `F1`: Help Dialog
- `F5`: Refresh Current View
- `F11`: Toggle Fullscreen
- `Ctrl+Q`: Quit Application

## Architecture

### Technology Stack
- **Frontend**: CustomTkinter (Modern UI)
- **Database**: SQLite (Local storage)
- **Reports**: Pandas + OpenPyXL (Excel export)
- **Charts**: Matplotlib (Data visualization)
- **Architecture**: Clean Architecture with separation of concerns

### Project Structure
```
├── main.py                 # Application entry point
├── database/
│   └── db_manager.py       # Database operations
├── models/
│   ├── employee.py         # Employee data models
│   └── shift.py           # Shift and schedule models
├── ui/
│   ├── employee_manager.py # Employee management UI
│   ├── shift_creator.py   # Shift creation UI
│   ├── calendar_view.py   # Calendar interface
│   ├── reports_dashboard.py # Reports and analytics
│   └── settings_manager.py # Application settings
└── utils/
    └── demo_data.py       # Sample data generation
```

## Demo Data

The application includes a comprehensive demo data generator that creates:
- **20 Sample Employees** with realistic profiles and performance metrics
- **6 Shift Templates** covering all operational periods
- **Performance Data** with attendance, punctuality, and ratings
- **Availability Schedules** with realistic work patterns

Click "🎲 Demo Data" in the sidebar to populate the system for exploration.

## Advanced Features

### Performance Tracking
- **Attendance Monitoring**: Automatic tracking of employee attendance rates
- **Punctuality Metrics**: Monitor on-time arrival and shift compliance
- **Customer Ratings**: Track customer service performance scores
- **Performance Notes**: Detailed feedback and improvement tracking

### Labor Cost Management
- **Real-time Calculations**: Instant labor cost updates with schedule changes
- **Budget Tracking**: Monitor labor costs against budget targets
- **Cost Optimization**: Suggestions for reducing labor expenses
- **Variance Analysis**: Compare actual vs. planned labor costs

### Scheduling Intelligence
- **Availability Matching**: Automatically match employees to suitable shifts
- **Skill-based Assignment**: Ensure proper skill coverage for all positions
- **Conflict Detection**: Identify and resolve scheduling conflicts
- **Optimization Suggestions**: Recommendations for improved scheduling

## Support & Development

This system is built with restaurant operational requirements in mind:
- **Scalable Design**: Handles small cafes to large restaurant chains
- **Professional Quality**: Enterprise-grade reliability and performance
- **User-Focused**: Designed by restaurant industry professionals
- **Continuous Improvement**: Regular updates and feature enhancements

For technical support or feature requests, please create an issue in the repository.

## License

Proprietary software designed specifically for restaurant operations.

---

**Built for Restaurant Management** 