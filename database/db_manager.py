"""
Database manager for Restaurant Shift Management System

This module provides database operations for managing employees, shifts, and schedules.
"""

import sqlite3
import json
from datetime import datetime, date, time
from typing import List, Optional, Dict, Any
from pathlib import Path
import logging
from contextlib import contextmanager

# Import models
import sys
sys.path.append('..')
from models.employee import Employee, Position, EmploymentStatus, SkillLevel, Availability
from models.shift import (Shift, ShiftTemplate, ShiftAssignment, WeeklySchedule, 
                         ShiftType, ShiftPriority, PositionRequirement, WeekDay)

class DatabaseManager:
    def __init__(self, db_path: str = "shifts.db"):
        self.db_path = db_path
        self.setup_logging()
        self.create_tables()
    
    def setup_logging(self):
        """Setup logging for database operations"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def create_tables(self):
        """Create all necessary tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Employees table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_number TEXT UNIQUE NOT NULL,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    address TEXT,
                    hire_date TEXT NOT NULL,
                    status TEXT NOT NULL,
                    hourly_wage REAL NOT NULL,
                    primary_position TEXT NOT NULL,
                    secondary_positions TEXT,  -- JSON array
                    skill_levels TEXT,  -- JSON object
                    max_hours_per_week INTEGER,
                    min_hours_per_week INTEGER,
                    preferred_shifts TEXT,  -- JSON array
                    attendance_rate REAL,
                    punctuality_score REAL,
                    customer_rating REAL,
                    training_completed TEXT,  -- JSON array
                    cannot_work_with TEXT,  -- JSON array of employee IDs
                    special_requirements TEXT,
                    notes TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Employee availability table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employee_availability (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER NOT NULL,
                    day_of_week INTEGER NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    is_preferred BOOLEAN DEFAULT 0,
                    FOREIGN KEY (employee_id) REFERENCES employees (id)
                )
            """)
            
            # Shift templates table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS shift_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    shift_type TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    break_duration_minutes INTEGER,
                    lunch_duration_minutes INTEGER,
                    minimum_break_coverage INTEGER,
                    is_peak_hours BOOLEAN DEFAULT 0,
                    priority TEXT NOT NULL,
                    special_requirements TEXT,
                    applicable_days TEXT,  -- JSON array
                    estimated_labor_cost REAL,
                    overtime_threshold_hours REAL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Position requirements table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS position_requirements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_id INTEGER NOT NULL,
                    position TEXT NOT NULL,
                    minimum_required INTEGER NOT NULL,
                    maximum_allowed INTEGER NOT NULL,
                    preferred_skill_level TEXT,
                    must_have_training TEXT,  -- JSON array
                    supervisor_required BOOLEAN DEFAULT 0,
                    FOREIGN KEY (template_id) REFERENCES shift_templates (id)
                )
            """)
            
            # Shifts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS shifts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_id INTEGER,
                    date TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    is_published BOOLEAN DEFAULT 0,
                    is_completed BOOLEAN DEFAULT 0,
                    actual_start_time TEXT,
                    actual_end_time TEXT,
                    sales_target REAL,
                    actual_sales REAL,
                    customer_count INTEGER,
                    average_wait_time REAL,
                    scheduled_labor_cost REAL,
                    actual_labor_cost REAL,
                    overtime_hours REAL,
                    manager_notes TEXT,
                    issues_reported TEXT,  -- JSON array
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    created_by INTEGER,
                    FOREIGN KEY (template_id) REFERENCES shift_templates (id),
                    FOREIGN KEY (created_by) REFERENCES employees (id)
                )
            """)
            
            # Shift assignments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS shift_assignments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    shift_id INTEGER NOT NULL,
                    employee_id INTEGER NOT NULL,
                    position TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    is_overtime BOOLEAN DEFAULT 0,
                    break_times TEXT,  -- JSON array of time pairs
                    notes TEXT,
                    FOREIGN KEY (shift_id) REFERENCES shifts (id),
                    FOREIGN KEY (employee_id) REFERENCES employees (id)
                )
            """)
            
            # Weekly schedules table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS weekly_schedules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    week_start_date TEXT NOT NULL,
                    is_published BOOLEAN DEFAULT 0,
                    is_finalized BOOLEAN DEFAULT 0,
                    total_labor_hours REAL,
                    total_labor_cost REAL,
                    created_by INTEGER,
                    approved_by INTEGER,
                    approval_date TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (created_by) REFERENCES employees (id),
                    FOREIGN KEY (approved_by) REFERENCES employees (id)
                )
            """)
            
            # Restaurant settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS restaurant_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setting_name TEXT UNIQUE NOT NULL,
                    setting_value TEXT NOT NULL,
                    description TEXT,
                    updated_at TEXT NOT NULL
                )
            """)
            
            conn.commit()
            self.logger.info("Database tables created successfully")
    
    # Employee CRUD operations
    def add_employee(self, employee: Employee) -> int:
        """Add new employee to database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO employees (
                    employee_number, first_name, last_name, email, phone, address,
                    hire_date, status, hourly_wage, primary_position, secondary_positions,
                    skill_levels, max_hours_per_week, min_hours_per_week, preferred_shifts,
                    attendance_rate, punctuality_score, customer_rating, training_completed,
                    cannot_work_with, special_requirements, notes, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                employee.employee_number, employee.first_name, employee.last_name,
                employee.email, employee.phone, employee.address,
                employee.hire_date.isoformat(), employee.status.value, employee.hourly_wage,
                employee.primary_position.value, json.dumps([pos.value for pos in employee.secondary_positions]),
                json.dumps({pos.value: skill.value for pos, skill in employee.skill_levels.items()}),
                employee.max_hours_per_week, employee.min_hours_per_week,
                json.dumps(employee.preferred_shifts), employee.attendance_rate,
                employee.punctuality_score, employee.customer_rating,
                json.dumps(employee.training_completed), json.dumps(employee.cannot_work_with),
                employee.special_requirements, employee.notes,
                employee.created_at.isoformat(), employee.updated_at.isoformat()
            ))
            
            employee_id = cursor.lastrowid
            
            # Add availability records
            for availability in employee.availability:
                cursor.execute("""
                    INSERT INTO employee_availability (
                        employee_id, day_of_week, start_time, end_time, is_preferred
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    employee_id, availability.day_of_week,
                    availability.start_time.isoformat(),
                    availability.end_time.isoformat(),
                    availability.is_preferred
                ))
            
            conn.commit()
            self.logger.info(f"Added employee: {employee.full_name} (ID: {employee_id})")
            return employee_id
    
    def get_employee(self, employee_id: int) -> Optional[Employee]:
        """Get employee by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM employees WHERE id = ?", (employee_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # Get availability
            cursor.execute("""
                SELECT day_of_week, start_time, end_time, is_preferred 
                FROM employee_availability WHERE employee_id = ?
            """, (employee_id,))
            availability_rows = cursor.fetchall()
            
            availability = []
            for av_row in availability_rows:
                availability.append(Availability(
                    day_of_week=av_row['day_of_week'],
                    start_time=time.fromisoformat(av_row['start_time']),
                    end_time=time.fromisoformat(av_row['end_time']),
                    is_preferred=bool(av_row['is_preferred'])
                ))
            
            # Convert row to Employee object
            employee = Employee(
                id=row['id'],
                employee_number=row['employee_number'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                email=row['email'],
                phone=row['phone'],
                address=row['address'],
                hire_date=datetime.fromisoformat(row['hire_date']),
                status=EmploymentStatus(row['status']),
                hourly_wage=row['hourly_wage'],
                primary_position=Position(row['primary_position']),
                secondary_positions=[Position(pos) for pos in json.loads(row['secondary_positions'] or '[]')],
                skill_levels={Position(pos): SkillLevel(skill) for pos, skill in json.loads(row['skill_levels'] or '{}').items()},
                max_hours_per_week=row['max_hours_per_week'],
                min_hours_per_week=row['min_hours_per_week'],
                availability=availability,
                preferred_shifts=json.loads(row['preferred_shifts'] or '[]'),
                attendance_rate=row['attendance_rate'],
                punctuality_score=row['punctuality_score'],
                customer_rating=row['customer_rating'],
                training_completed=json.loads(row['training_completed'] or '[]'),
                cannot_work_with=json.loads(row['cannot_work_with'] or '[]'),
                special_requirements=row['special_requirements'],
                notes=row['notes'],
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at'])
            )
            
            return employee
    
    def get_all_employees(self, status: Optional[EmploymentStatus] = None) -> List[Employee]:
        """Get all employees, optionally filtered by status"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if status:
                cursor.execute("SELECT id FROM employees WHERE status = ?", (status.value,))
            else:
                cursor.execute("SELECT id FROM employees")
            
            employee_ids = [row['id'] for row in cursor.fetchall()]
            employees = []
            
            for emp_id in employee_ids:
                employee = self.get_employee(emp_id)
                if employee:
                    employees.append(employee)
            
            return employees
    
    def update_employee(self, employee: Employee) -> bool:
        """Update existing employee"""
        if not employee.id:
            return False
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Update main employee record
            cursor.execute("""
                UPDATE employees SET
                    employee_number = ?, first_name = ?, last_name = ?, email = ?,
                    phone = ?, address = ?, hire_date = ?, status = ?, hourly_wage = ?,
                    primary_position = ?, secondary_positions = ?, skill_levels = ?,
                    max_hours_per_week = ?, min_hours_per_week = ?, preferred_shifts = ?,
                    attendance_rate = ?, punctuality_score = ?, customer_rating = ?,
                    training_completed = ?, cannot_work_with = ?, special_requirements = ?,
                    notes = ?, updated_at = ?
                WHERE id = ?
            """, (
                employee.employee_number, employee.first_name, employee.last_name,
                employee.email, employee.phone, employee.address,
                employee.hire_date.isoformat(), employee.status.value, employee.hourly_wage,
                employee.primary_position.value, json.dumps([pos.value for pos in employee.secondary_positions]),
                json.dumps({pos.value: skill.value for pos, skill in employee.skill_levels.items()}),
                employee.max_hours_per_week, employee.min_hours_per_week,
                json.dumps(employee.preferred_shifts), employee.attendance_rate,
                employee.punctuality_score, employee.customer_rating,
                json.dumps(employee.training_completed), json.dumps(employee.cannot_work_with),
                employee.special_requirements, employee.notes,
                datetime.now().isoformat(), employee.id
            ))
            
            # Update availability
            cursor.execute("DELETE FROM employee_availability WHERE employee_id = ?", (employee.id,))
            for availability in employee.availability:
                cursor.execute("""
                    INSERT INTO employee_availability (
                        employee_id, day_of_week, start_time, end_time, is_preferred
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    employee.id, availability.day_of_week,
                    availability.start_time.isoformat(),
                    availability.end_time.isoformat(),
                    availability.is_preferred
                ))
            
            conn.commit()
            self.logger.info(f"Updated employee: {employee.full_name}")
            return True
    
    def delete_employee(self, employee_id: int) -> bool:
        """Delete employee (soft delete by setting status to TERMINATED)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE employees SET status = ?, updated_at = ? WHERE id = ?
            """, (EmploymentStatus.TERMINATED.value, datetime.now().isoformat(), employee_id))
            
            conn.commit()
            self.logger.info(f"Terminated employee ID: {employee_id}")
            return cursor.rowcount > 0
    
    # Shift template CRUD operations
    def add_shift_template(self, template: ShiftTemplate) -> int:
        """Add new shift template"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO shift_templates (
                    name, shift_type, start_time, end_time, break_duration_minutes,
                    lunch_duration_minutes, minimum_break_coverage, is_peak_hours,
                    priority, special_requirements, applicable_days, estimated_labor_cost,
                    overtime_threshold_hours, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                template.name, template.shift_type.value,
                template.start_time.isoformat(), template.end_time.isoformat(),
                template.break_duration_minutes, template.lunch_duration_minutes,
                template.minimum_break_coverage, template.is_peak_hours,
                template.priority.value, template.special_requirements,
                json.dumps([day.value for day in template.applicable_days]),
                template.estimated_labor_cost, template.overtime_threshold_hours,
                datetime.now().isoformat(), datetime.now().isoformat()
            ))
            
            template_id = cursor.lastrowid
            
            # Add position requirements
            for req in template.position_requirements:
                cursor.execute("""
                    INSERT INTO position_requirements (
                        template_id, position, minimum_required, maximum_allowed,
                        preferred_skill_level, must_have_training, supervisor_required
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    template_id, req.position.value, req.minimum_required,
                    req.maximum_allowed, req.preferred_skill_level,
                    json.dumps(req.must_have_training), req.supervisor_required
                ))
            
            conn.commit()
            self.logger.info(f"Added shift template: {template.name} (ID: {template_id})")
            return template_id
    
    # Additional CRUD methods for shifts, schedules, etc. would follow similar patterns...
    
    def get_restaurant_setting(self, setting_name: str) -> Optional[str]:
        """Get restaurant setting value"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT setting_value FROM restaurant_settings WHERE setting_name = ?", (setting_name,))
            row = cursor.fetchone()
            return row['setting_value'] if row else None
    
    def set_restaurant_setting(self, setting_name: str, setting_value: str, description: str = ""):
        """Set restaurant setting"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO restaurant_settings (setting_name, setting_value, description, updated_at)
                VALUES (?, ?, ?, ?)
            """, (setting_name, setting_value, description, datetime.now().isoformat()))
            conn.commit()
    
    def backup_database(self, backup_path: str) -> bool:
        """Create database backup"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            self.logger.info(f"Database backed up to: {backup_path}")
            return True
        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            return False 