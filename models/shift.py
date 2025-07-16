from dataclasses import dataclass, field
from datetime import datetime, date, time, timedelta
from typing import List, Optional, Dict, Set
from enum import Enum
from .employee import Position, Employee

class ShiftType(Enum):
    MORNING = "Morning Shift"
    AFTERNOON = "Afternoon Shift" 
    EVENING = "Evening Shift"
    NIGHT = "Night Shift"
    SPLIT = "Split Shift"
    DOUBLE = "Double Shift"

class ShiftPriority(Enum):
    LOW = "Low"
    NORMAL = "Normal"
    HIGH = "High"
    CRITICAL = "Critical"

class WeekDay(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

@dataclass
class PositionRequirement:
    position: Position
    minimum_required: int
    maximum_allowed: int
    preferred_skill_level: Optional[str] = None
    must_have_training: List[str] = field(default_factory=list)
    supervisor_required: bool = False

@dataclass
class ShiftTemplate:
    id: Optional[int] = None
    name: str = ""
    shift_type: ShiftType = ShiftType.MORNING
    start_time: time = time(9, 0)
    end_time: time = time(17, 0)
    
    # Position requirements
    position_requirements: List[PositionRequirement] = field(default_factory=list)
    
    # Operational details
    break_duration_minutes: int = 30
    lunch_duration_minutes: int = 60
    minimum_break_coverage: int = 1
    
    # Business rules
    is_peak_hours: bool = False
    priority: ShiftPriority = ShiftPriority.NORMAL
    special_requirements: str = ""
    
    # Days this template applies to
    applicable_days: Set[WeekDay] = field(default_factory=set)
    
    # Labor cost estimates
    estimated_labor_cost: float = 0.0
    overtime_threshold_hours: float = 8.0
    
    @property
    def duration_hours(self) -> float:
        """Calculate shift duration in hours"""
        start_minutes = self.start_time.hour * 60 + self.start_time.minute
        end_minutes = self.end_time.hour * 60 + self.end_time.minute
        
        # Handle overnight shifts
        if end_minutes <= start_minutes:
            end_minutes += 24 * 60
            
        duration_minutes = end_minutes - start_minutes
        return duration_minutes / 60
    
    @property
    def total_positions_needed(self) -> int:
        """Calculate total minimum positions needed"""
        return sum(req.minimum_required for req in self.position_requirements)
    
    def get_position_requirement(self, position: Position) -> Optional[PositionRequirement]:
        """Get requirement for specific position"""
        for req in self.position_requirements:
            if req.position == position:
                return req
        return None

@dataclass
class ShiftAssignment:
    employee_id: int
    position: Position
    start_time: time
    end_time: time
    is_overtime: bool = False
    break_times: List[tuple[time, time]] = field(default_factory=list)
    notes: str = ""
    
    @property
    def duration_hours(self) -> float:
        """Calculate assignment duration in hours"""
        start_minutes = self.start_time.hour * 60 + self.start_time.minute
        end_minutes = self.end_time.hour * 60 + self.end_time.minute
        
        if end_minutes <= start_minutes:
            end_minutes += 24 * 60
            
        duration_minutes = end_minutes - start_minutes
        return duration_minutes / 60

@dataclass
class Shift:
    id: Optional[int] = None
    template_id: Optional[int] = None
    date: date = field(default_factory=date.today)
    start_time: time = time(9, 0)
    end_time: time = time(17, 0)
    
    # Staff assignments
    assignments: List[ShiftAssignment] = field(default_factory=list)
    
    # Status and tracking
    is_published: bool = False
    is_completed: bool = False
    actual_start_time: Optional[time] = None
    actual_end_time: Optional[time] = None
    
    # Performance metrics
    sales_target: float = 0.0
    actual_sales: float = 0.0
    customer_count: int = 0
    average_wait_time: float = 0.0
    
    # Labor tracking
    scheduled_labor_cost: float = 0.0
    actual_labor_cost: float = 0.0
    overtime_hours: float = 0.0
    
    # Notes and issues
    manager_notes: str = ""
    issues_reported: List[str] = field(default_factory=list)
    
    # System fields
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: Optional[int] = None  # manager employee ID
    
    @property
    def duration_hours(self) -> float:
        """Calculate shift duration in hours"""
        start_minutes = self.start_time.hour * 60 + self.start_time.minute
        end_minutes = self.end_time.hour * 60 + self.end_time.minute
        
        if end_minutes <= start_minutes:
            end_minutes += 24 * 60
            
        duration_minutes = end_minutes - start_minutes
        return duration_minutes / 60
    
    @property
    def total_scheduled_employees(self) -> int:
        """Get total number of scheduled employees"""
        return len(self.assignments)
    
    @property
    def positions_filled(self) -> Dict[Position, int]:
        """Get count of employees per position"""
        position_count = {}
        for assignment in self.assignments:
            position = assignment.position
            position_count[position] = position_count.get(position, 0) + 1
        return position_count
    
    @property
    def is_understaffed(self) -> bool:
        """Check if shift is understaffed based on template requirements"""
        # This would need template requirements to compare against
        return self.total_scheduled_employees < 3  # Basic check
    
    def get_employee_assignment(self, employee_id: int) -> Optional[ShiftAssignment]:
        """Get assignment for specific employee"""
        for assignment in self.assignments:
            if assignment.employee_id == employee_id:
                return assignment
        return None
    
    def calculate_labor_cost(self, employees: List[Employee]) -> float:
        """Calculate total labor cost for this shift"""
        total_cost = 0.0
        employee_dict = {emp.id: emp for emp in employees}
        
        for assignment in self.assignments:
            employee = employee_dict.get(assignment.employee_id)
            if employee:
                hours = assignment.duration_hours
                regular_hours = min(hours, 8.0)
                overtime_hours = max(0, hours - 8.0)
                
                cost = (regular_hours * employee.hourly_wage + 
                       overtime_hours * employee.hourly_wage * 1.5)
                total_cost += cost
        
        return total_cost
    
    def add_assignment(self, employee_id: int, position: Position, 
                      start_time: Optional[time] = None, 
                      end_time: Optional[time] = None):
        """Add employee assignment to shift"""
        assignment = ShiftAssignment(
            employee_id=employee_id,
            position=position,
            start_time=start_time or self.start_time,
            end_time=end_time or self.end_time
        )
        self.assignments.append(assignment)
    
    def remove_assignment(self, employee_id: int):
        """Remove employee assignment from shift"""
        self.assignments = [a for a in self.assignments if a.employee_id != employee_id]

@dataclass 
class WeeklySchedule:
    id: Optional[int] = None
    week_start_date: date = field(default_factory=lambda: date.today())
    shifts: Dict[date, List[Shift]] = field(default_factory=dict)
    
    # Schedule metadata
    is_published: bool = False
    is_finalized: bool = False
    total_labor_hours: float = 0.0
    total_labor_cost: float = 0.0
    
    # Manager info
    created_by: Optional[int] = None
    approved_by: Optional[int] = None
    approval_date: Optional[datetime] = None
    
    # System fields
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    @property
    def week_end_date(self) -> date:
        """Get end date of the week"""
        return self.week_start_date + timedelta(days=6)
    
    @property
    def week_dates(self) -> List[date]:
        """Get all dates in the week"""
        return [self.week_start_date + timedelta(days=i) for i in range(7)]
    
    def get_shifts_for_date(self, target_date: date) -> List[Shift]:
        """Get all shifts for specific date"""
        return self.shifts.get(target_date, [])
    
    def add_shift(self, shift: Shift):
        """Add shift to schedule"""
        if shift.date not in self.shifts:
            self.shifts[shift.date] = []
        self.shifts[shift.date].append(shift)
    
    def get_employee_total_hours(self, employee_id: int) -> float:
        """Get total scheduled hours for employee this week"""
        total_hours = 0.0
        for shifts_list in self.shifts.values():
            for shift in shifts_list:
                assignment = shift.get_employee_assignment(employee_id)
                if assignment:
                    total_hours += assignment.duration_hours
        return total_hours
    
    def calculate_weekly_labor_cost(self, employees: List[Employee]) -> float:
        """Calculate total labor cost for the week"""
        total_cost = 0.0
        for shifts_list in self.shifts.values():
            for shift in shifts_list:
                total_cost += shift.calculate_labor_cost(employees)
        return total_cost 