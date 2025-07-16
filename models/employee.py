from dataclasses import dataclass, field
from datetime import datetime, time
from typing import List, Optional, Dict
from enum import Enum

class Position(Enum):
    CASHIER = "Cashier"
    KITCHEN = "Kitchen Crew"
    DRIVE_THRU = "Drive-Thru"
    MANAGER = "Manager"
    SHIFT_SUPERVISOR = "Shift Supervisor"
    CLEANING_CREW = "Cleaning Crew"
    MAINTENANCE = "Maintenance"
    TRAINEE = "Trainee"

class EmploymentStatus(Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    ON_LEAVE = "On Leave"
    TERMINATED = "Terminated"

class SkillLevel(Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    EXPERT = "Expert"

@dataclass
class Availability:
    day_of_week: int  # 0=Monday, 6=Sunday
    start_time: time
    end_time: time
    is_preferred: bool = False

@dataclass
class Employee:
    id: Optional[int] = None
    employee_number: str = ""
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: str = ""
    address: str = ""
    
    # Employment details
    hire_date: datetime = field(default_factory=datetime.now)
    status: EmploymentStatus = EmploymentStatus.ACTIVE
    hourly_wage: float = 15.00
    
    # Position and skills
    primary_position: Position = Position.CASHIER
    secondary_positions: List[Position] = field(default_factory=list)
    skill_levels: Dict[Position, SkillLevel] = field(default_factory=dict)
    
    # Scheduling preferences
    max_hours_per_week: int = 40
    min_hours_per_week: int = 20
    availability: List[Availability] = field(default_factory=list)
    preferred_shifts: List[str] = field(default_factory=list)  # morning, afternoon, evening, night
    
    # Performance metrics
    attendance_rate: float = 100.0  # percentage
    punctuality_score: float = 100.0  # percentage
    customer_rating: float = 5.0  # 1-5 scale
    training_completed: List[str] = field(default_factory=list)
    
    # Restrictions and notes
    cannot_work_with: List[int] = field(default_factory=list)  # employee IDs
    special_requirements: str = ""
    notes: str = ""
    
    # System fields
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    @property
    def can_supervise(self) -> bool:
        return self.primary_position in [Position.MANAGER, Position.SHIFT_SUPERVISOR]
    
    @property
    def weekly_labor_cost(self) -> float:
        """Calculate estimated weekly labor cost"""
        avg_hours = (self.min_hours_per_week + self.max_hours_per_week) / 2
        return avg_hours * self.hourly_wage
    
    def can_work_position(self, position: Position) -> bool:
        """Check if employee can work in specific position"""
        if self.primary_position == position:
            return True
        return position in self.secondary_positions
    
    def get_skill_level(self, position: Position) -> SkillLevel:
        """Get skill level for specific position"""
        return self.skill_levels.get(position, SkillLevel.BEGINNER)
    
    def is_available(self, day_of_week: int, start_time: time, end_time: time) -> bool:
        """Check if employee is available for specific time slot"""
        for availability in self.availability:
            if (availability.day_of_week == day_of_week and 
                availability.start_time <= start_time and 
                availability.end_time >= end_time):
                return True
        return False 