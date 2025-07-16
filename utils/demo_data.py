"""
Demo Data Generator for Restaurant Shift Management System

This module generates realistic sample data for testing and demonstration purposes.
"""

import random
from datetime import datetime, date, time, timedelta
from typing import List, Tuple
from database.db_manager import DatabaseManager
from models.employee import Employee, Position, EmploymentStatus, EmploymentType, SkillLevel
from models.shift import ShiftTemplate

class DemoDataGenerator:
    """Generates demo data for the Restaurant Shift Management System"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    # Sample employee data with realistic names and contact info
    SAMPLE_EMPLOYEES = [
        ("James", "Wilson", "james.wilson@restaurant.com", "+1-555-0101"),
        ("Sarah", "Johnson", "sarah.johnson@restaurant.com", "+1-555-0102"),
        ("Michael", "Brown", "michael.brown@restaurant.com", "+1-555-0103"),
        ("Emily", "Davis", "emily.davis@restaurant.com", "+1-555-0104"),
        ("David", "Miller", "david.miller@restaurant.com", "+1-555-0105"),
        ("Jessica", "Garcia", "jessica.garcia@restaurant.com", "+1-555-0106"),
        ("Christopher", "Rodriguez", "chris.rodriguez@restaurant.com", "+1-555-0107"),
        ("Ashley", "Martinez", "ashley.martinez@restaurant.com", "+1-555-0108"),
        ("Matthew", "Anderson", "matthew.anderson@restaurant.com", "+1-555-0109"),
        ("Amanda", "Taylor", "amanda.taylor@restaurant.com", "+1-555-0110"),
        ("Daniel", "Thomas", "daniel.thomas@restaurant.com", "+1-555-0111"),
        ("Stephanie", "Jackson", "stephanie.jackson@restaurant.com", "+1-555-0112"),
        ("Ryan", "White", "ryan.white@restaurant.com", "+1-555-0113"),
        ("Nicole", "Harris", "nicole.harris@restaurant.com", "+1-555-0114"),
        ("Brandon", "Clark", "brandon.clark@restaurant.com", "+1-555-0115"),
        ("Lauren", "Lewis", "lauren.lewis@restaurant.com", "+1-555-0116"),
        ("Justin", "Walker", "justin.walker@restaurant.com", "+1-555-0117"),
        ("Megan", "Hall", "megan.hall@restaurant.com", "+1-555-0118"),
        ("Kevin", "Allen", "kevin.allen@restaurant.com", "+1-555-0119"),
        ("Rachel", "Young", "rachel.young@restaurant.com", "+1-555-0120")
    ]
    
    # Position distribution for realistic staffing
    POSITION_DISTRIBUTION = {
        Position.MANAGER: 0.10,        # 10% managers
        Position.CASHIER: 0.35,        # 35% cashiers
        Position.KITCHEN: 0.30,        # 30% kitchen staff
        Position.DRIVE_THRU: 0.15,     # 15% drive-thru
        Position.CLEANING_CREW: 0.10   # 10% cleaning crew
    }
    
    # Skill level distribution (more realistic - not everyone is expert)
    SKILL_DISTRIBUTION = {
        SkillLevel.BEGINNER: 0.30,     # 30% beginners
        SkillLevel.INTERMEDIATE: 0.45,  # 45% intermediate
        SkillLevel.ADVANCED: 0.20,     # 20% advanced
        SkillLevel.EXPERT: 0.05        # 5% experts
    }
    
    # Employment type distribution
    EMPLOYMENT_TYPE_DISTRIBUTION = {
        EmploymentType.FULL_TIME: 0.40,  # 40% full-time
        EmploymentType.PART_TIME: 0.50,  # 50% part-time
        EmploymentType.TEMPORARY: 0.10   # 10% temporary
    }
    
    def generate_realistic_availability(self, employment_type: EmploymentType) -> str:
        """Generate realistic availability based on employment type"""
        # Base availability (7 days, 24 hours format)
        # Format: "day:start_hour-end_hour,day:start_hour-end_hour"
        
        if employment_type == EmploymentType.FULL_TIME:
            # Full-time: 5-6 days, longer shifts
            available_days = random.sample(
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                k=random.randint(5, 6)
            )
            availability = []
            for day in available_days:
                start_hour = random.choice([6, 7, 8, 9])
                end_hour = start_hour + random.randint(8, 10)  # 8-10 hour shifts
                if end_hour > 23:
                    end_hour = 23
                availability.append(f"{day}:{start_hour:02d}:00-{end_hour:02d}:00")
                
        elif employment_type == EmploymentType.PART_TIME:
            # Part-time: 3-5 days, shorter shifts
            available_days = random.sample(
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                k=random.randint(3, 5)
            )
            availability = []
            for day in available_days:
                start_hour = random.choice([10, 11, 14, 15, 16, 17])
                end_hour = start_hour + random.randint(4, 6)  # 4-6 hour shifts
                if end_hour > 22:
                    end_hour = 22
                availability.append(f"{day}:{start_hour:02d}:00-{end_hour:02d}:00")
                
        else:  # TEMPORARY
            # Temporary: 2-4 days, flexible hours
            available_days = random.sample(
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                k=random.randint(2, 4)
            )
            availability = []
            for day in available_days:
                start_hour = random.choice([8, 10, 12, 14, 16])
                end_hour = start_hour + random.randint(3, 8)  # Variable shifts
                if end_hour > 22:
                    end_hour = 22
                availability.append(f"{day}:{start_hour:02d}:00-{end_hour:02d}:00")
        
        return ",".join(availability)
    
    def generate_realistic_performance_metrics(self, skill_level: SkillLevel, position: Position) -> dict:
        """Generate realistic performance metrics based on skill level and position"""
        base_attendance = {
            SkillLevel.BEGINNER: random.uniform(0.75, 0.85),
            SkillLevel.INTERMEDIATE: random.uniform(0.85, 0.92),
            SkillLevel.ADVANCED: random.uniform(0.90, 0.96),
            SkillLevel.EXPERT: random.uniform(0.94, 0.99)
        }
        
        base_punctuality = {
            SkillLevel.BEGINNER: random.uniform(0.70, 0.85),
            SkillLevel.INTERMEDIATE: random.uniform(0.85, 0.93),
            SkillLevel.ADVANCED: random.uniform(0.90, 0.97),
            SkillLevel.EXPERT: random.uniform(0.95, 0.99)
        }
        
        base_customer_rating = {
            SkillLevel.BEGINNER: random.uniform(3.0, 3.8),
            SkillLevel.INTERMEDIATE: random.uniform(3.5, 4.2),
            SkillLevel.ADVANCED: random.uniform(4.0, 4.6),
            SkillLevel.EXPERT: random.uniform(4.3, 4.9)
        }
        
        # Adjust ratings based on position
        position_modifiers = {
            Position.MANAGER: {"attendance": 0.05, "punctuality": 0.08, "customer_rating": 0.3},
            Position.CASHIER: {"attendance": 0.02, "punctuality": 0.03, "customer_rating": 0.2},
            Position.KITCHEN: {"attendance": 0.0, "punctuality": 0.0, "customer_rating": 0.1},
            Position.DRIVE_THRU: {"attendance": 0.01, "punctuality": 0.02, "customer_rating": 0.15},
            Position.CLEANING_CREW: {"attendance": -0.02, "punctuality": -0.01, "customer_rating": 0.0}
        }
        
        modifier = position_modifiers.get(position, {"attendance": 0, "punctuality": 0, "customer_rating": 0})
        
        attendance = min(0.99, base_attendance[skill_level] + modifier["attendance"])
        punctuality = min(0.99, base_punctuality[skill_level] + modifier["punctuality"])
        customer_rating = min(5.0, base_customer_rating[skill_level] + modifier["customer_rating"])
        
        return {
            "attendance_rate": round(attendance, 3),
            "punctuality_rate": round(punctuality, 3),
            "customer_rating": round(customer_rating, 1),
            "performance_notes": self.generate_performance_notes(skill_level, position)
        }
    
    def generate_performance_notes(self, skill_level: SkillLevel, position: Position) -> str:
        """Generate realistic performance notes"""
        skill_notes = {
            SkillLevel.BEGINNER: [
                "New employee, showing good potential",
                "Learning quickly, needs occasional guidance",
                "Eager to learn and improve",
                "Making steady progress in training"
            ],
            SkillLevel.INTERMEDIATE: [
                "Reliable team member",
                "Handles routine tasks well",
                "Good work ethic and attitude",
                "Occasionally helps train new staff"
            ],
            SkillLevel.ADVANCED: [
                "Excellent performance consistently",
                "Often goes above and beyond",
                "Strong leadership potential",
                "Mentors newer employees effectively"
            ],
            SkillLevel.EXPERT: [
                "Outstanding performer and role model",
                "Expert in all areas of responsibility",
                "Natural leader and mentor",
                "Consistently exceeds expectations"
            ]
        }
        
        position_notes = {
            Position.MANAGER: ["Strong leadership skills", "Excellent decision-making", "Great team coordinator"],
            Position.CASHIER: ["Friendly customer service", "Accurate cash handling", "Upselling specialist"],
            Position.KITCHEN: ["Fast food preparation", "Maintains quality standards", "Efficient workflow"],
            Position.DRIVE_THRU: ["Quick order processing", "Clear communication", "Multitasking expert"],
            Position.CLEANING_CREW: ["Maintains high standards", "Detail-oriented", "Proactive approach"]
        }
        
        # Combine skill and position notes
        notes = []
        notes.append(random.choice(skill_notes[skill_level]))
        if random.random() > 0.5:  # 50% chance to add position-specific note
            notes.append(random.choice(position_notes[position]))
        
        return "; ".join(notes)
    
    def weighted_choice(self, choices: dict):
        """Make a weighted random choice from a dictionary of choices and weights"""
        items = list(choices.keys())
        weights = list(choices.values())
        return random.choices(items, weights=weights, k=1)[0]
    
    def generate_employees(self) -> List[int]:
        """Generate sample employees and return their IDs"""
        employee_ids = []
        
        for i, (first_name, last_name, email, phone) in enumerate(self.SAMPLE_EMPLOYEES):
            # Assign position based on distribution
            position = self.weighted_choice(self.POSITION_DISTRIBUTION)
            
            # Assign skill level based on distribution
            skill_level = self.weighted_choice(self.SKILL_DISTRIBUTION)
            
            # Assign employment type based on distribution
            employment_type = self.weighted_choice(self.EMPLOYMENT_TYPE_DISTRIBUTION)
            
            # Generate hire date (within last 2 years)
            hire_date = date.today() - timedelta(days=random.randint(1, 730))
            
            # Generate wage based on position and skill level
            base_wages = {
                Position.MANAGER: 22.00,
                Position.CASHIER: 15.00,
                Position.KITCHEN: 16.00,
                Position.DRIVE_THRU: 15.50,
                Position.CLEANING_CREW: 14.00
            }
            
            skill_multipliers = {
                SkillLevel.BEGINNER: 1.0,
                SkillLevel.INTERMEDIATE: 1.15,
                SkillLevel.ADVANCED: 1.35,
                SkillLevel.EXPERT: 1.55
            }
            
            hourly_wage = base_wages[position] * skill_multipliers[skill_level]
            hourly_wage += random.uniform(-0.50, 0.50)  # Add some variance
            hourly_wage = round(hourly_wage, 2)
            
            # Generate availability
            availability = self.generate_realistic_availability(employment_type)
            
            # Generate performance metrics
            performance_metrics = self.generate_realistic_performance_metrics(skill_level, position)
            
            # Create employee
            employee = Employee(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                position=position,
                employment_status=EmploymentStatus.ACTIVE,
                employment_type=employment_type,
                hire_date=hire_date,
                hourly_wage=hourly_wage,
                skill_level=skill_level,
                availability=availability,
                performance_metrics=performance_metrics
            )
            
            # Add to database
            employee_id = self.db_manager.add_employee(employee)
            employee_ids.append(employee_id)
            
        return employee_ids
    
    def generate_shift_templates(self) -> List[int]:
        """Generate standard restaurant shift templates"""
        templates = [
            # Morning shifts
            ShiftTemplate(
                name="Opening Shift",
                start_time=time(6, 0),
                end_time=time(14, 0),
                positions_required={
                    Position.MANAGER: 1,
                    Position.CASHIER: 2,
                    Position.KITCHEN: 2,
                    Position.DRIVE_THRU: 1
                },
                total_hours=8.0,
                is_active=True,
                description="Early morning opening shift - breakfast rush coverage"
            ),
            
            # Mid-day shifts
            ShiftTemplate(
                name="Mid Shift",
                start_time=time(10, 0),
                end_time=time(18, 0),
                positions_required={
                    Position.MANAGER: 1,
                    Position.CASHIER: 3,
                    Position.KITCHEN: 3,
                    Position.DRIVE_THRU: 2
                },
                total_hours=8.0,
                is_active=True,
                description="Lunch rush coverage - high volume period"
            ),
            
            # Evening shifts
            ShiftTemplate(
                name="Closing Shift",
                start_time=time(16, 0),
                end_time=time(24, 0),
                positions_required={
                    Position.MANAGER: 1,
                    Position.CASHIER: 2,
                    Position.KITCHEN: 2,
                    Position.DRIVE_THRU: 1,
                    Position.CLEANING_CREW: 1
                },
                total_hours=8.0,
                is_active=True,
                description="Dinner rush and closing procedures"
            ),
            
            # Weekend shifts
            ShiftTemplate(
                name="Weekend Double",
                start_time=time(8, 0),
                end_time=time(20, 0),
                positions_required={
                    Position.MANAGER: 1,
                    Position.CASHIER: 4,
                    Position.KITCHEN: 4,
                    Position.DRIVE_THRU: 2,
                    Position.CLEANING_CREW: 1
                },
                total_hours=12.0,
                is_active=True,
                description="Extended weekend shift - busy periods"
            ),
            
            # Part-time shifts
            ShiftTemplate(
                name="Part-Time Morning",
                start_time=time(9, 0),
                end_time=time(13, 0),
                positions_required={
                    Position.CASHIER: 1,
                    Position.KITCHEN: 1
                },
                total_hours=4.0,
                is_active=True,
                description="Part-time morning support shift"
            ),
            
            ShiftTemplate(
                name="Part-Time Evening",
                start_time=time(17, 0),
                end_time=time(21, 0),
                positions_required={
                    Position.CASHIER: 1,
                    Position.DRIVE_THRU: 1
                },
                total_hours=4.0,
                is_active=True,
                description="Part-time evening support shift"
            )
        ]
        
        template_ids = []
        for template in templates:
            template_id = self.db_manager.add_shift_template(template)
            template_ids.append(template_id)
            
        return template_ids
    
    def generate_all_demo_data(self) -> Tuple[List[int], List[int]]:
        """Generate all demo data and return employee and template IDs"""
        print("🍟 Restaurant Demo Data Generator")
        print("=" * 50)
        
        # Generate employees
        print("👥 Generating employees...")
        employee_ids = self.generate_employees()
        print(f"   ✅ Created {len(employee_ids)} employees")
        
        # Generate shift templates
        print("📅 Generating shift templates...")
        template_ids = self.generate_shift_templates()
        print(f"   ✅ Created {len(template_ids)} shift templates")
        
        print("=" * 50)
        print("📊 Demo Data Summary:")
        print(f"   • {len(employee_ids)} employees created")
        print(f"   • {len(template_ids)} shift templates created")
        print(f"   • Realistic performance metrics")
        print(f"   • Diverse skill levels and positions")
        print(f"   • Proper availability schedules")
        print("")
        print("🚀 You can now explore the Restaurant Shift Management System with realistic data.")
        print("   Navigate to different sections to see employees, shifts, and reports.")
        
        return employee_ids, template_ids

def main():
    """Standalone demo data generation"""
    print("Restaurant Shift Management - Demo Data Generator")
    print("This will generate sample data for testing purposes.")
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Generate demo data
    generator = DemoDataGenerator(db_manager)
    employee_ids, template_ids = generator.generate_all_demo_data()
    
    print(f"\nDemo data generation complete!")
    print(f"Generated {len(employee_ids)} employees and {len(template_ids)} shift templates.")

if __name__ == "__main__":
    main() 