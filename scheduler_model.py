import pyomo.environ as pyo
import numpy as np
import pandas as pd

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import random

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.platypus import Spacer
from reportlab.lib.enums import TA_CENTER

class course_scheduler:
    def __init__(self, days, hours, courses_overall, max_hours_per_day, teachers_Subject, preferencas_dias_professores, salas, discPreferenciasSala , quantity_students):
        self.days = days
        self.hours = hours
        self.courses_overall = courses_overall
        self.max_hours_per_day = max_hours_per_day
        self.teachers_Subject = dict(teachers_Subject)
        self.preferencas_dias_professores = dict(preferencas_dias_professores)
        self.salas = dict(salas)
        self.discPreferenciasSala = dict(discPreferenciasSala)
        self.models = []
        self.quantity_students = dict(quantity_students)
    

    def create_model(self):
        for courses in self.courses_overall.values():

            model = pyo.ConcreteModel()
            # Sets
            model.days = pyo.Set(initialize=self.days, ordered = True)
            # Define continuous hour set starting from 9:00 AM
            model.hours = pyo.Set(initialize=self.hours , ordered = True)

            
            model.courses = pyo.Set(initialize=courses.keys())

            # Parameters
            model.teacher_indices = pyo.Set(initialize=self.teachers_Subject.keys())
            model.teacher = pyo.Param(model.teacher_indices, initialize=self.teachers_Subject, within=pyo.Any)
            model.rooms = pyo.Set(initialize=self.salas.keys())


            model.rooms_quantity = pyo.Param(model.rooms, initialize=self.salas, within=pyo.NonNegativeIntegers)

            
            # Parameters
            model.hours_per_course = pyo.Param(model.courses, initialize=courses)
            model.max_hours_per_day = self.max_hours_per_day


            model.discPreferenciasSala = self.discPreferenciasSala
            # Max hours per week per course
            model.max_hours_per_week = {course: hours for course, hours in courses.items()}
            
            model.preferencas_dias_professores = self.preferencas_dias_professores
            # Variables
            model.schedule = pyo.Var(model.days, model.hours, model.courses , domain=pyo.Binary)

            model.room_assignment = pyo.Var(model.days, model.hours, model.courses, model.rooms, domain=pyo.Binary)



            # Constraint: Only one subject can be held in the classroom at the same time
            def single_assignment_constraint(model, day, hour):
                return sum(model.schedule[day, hour, course] for course in model.courses) <= 1
            
            model.single_assignment_constraint = pyo.Constraint(model.days, model.hours, rule=single_assignment_constraint)
            
            # Constraint: Maximum hours for the same subject per day
            def max_hours_per_day_constraint(model, course, day):
                return sum(model.schedule[day, hour, course] for hour in model.hours) <= 2
            
            model.max_hours_per_day_constraint = pyo.Constraint(model.courses, model.days, rule=max_hours_per_day_constraint)
            
            # Constraint: Maximum hours for the same subject per week
            def max_hours_per_week_constraint(model, course):
                return sum(model.schedule[day, hour, course] for day in model.days for hour in model.hours) <= model.max_hours_per_week[course]
            
            model.max_hours_per_week_constraint = pyo.Constraint(model.courses, rule=max_hours_per_week_constraint)


            # Constraint: Subject scheduled only when teacher is available
            def teacher_availability_constraint(model, course, day):
                # Check if teacher for the course is available on the given day
                teacher = model.teacher[course]
                if teacher not in model.preferencas_dias_professores or day not in model.preferencas_dias_professores[teacher]:
                    return sum(model.schedule[day, hour, course] for hour in model.hours) == 0
                return pyo.Constraint.Skip
            
            model.teacher_availability_constraint = pyo.Constraint(model.courses, model.days, rule=teacher_availability_constraint)


            # Constraint: Only one room can be assigned to a course at a given time respecting preferences and room size
            def room_assignment_constraint(model, day, hour, course):
                preferred_rooms = model.discPreferenciasSala[course]  # Get preferred rooms for the course
                random.shuffle(preferred_rooms)
                
                if preferred_rooms:  # If there are preferred rooms
                    suitable_rooms = []  # List to store rooms with sufficient capacity
                    for room in preferred_rooms:
                        if model.rooms_quantity[room] >= self.quantity_students[course]:  # Assuming quantity_students is defined somewhere
                            suitable_rooms.append(room)

                    if suitable_rooms:  # If there are suitable rooms
                        # Assign only suitable rooms
                        return sum(model.room_assignment[day, hour, course, room] for room in suitable_rooms) == 1
                    else:
                        # If no suitable room found among preferred rooms, assign a temporary room
                        return sum(model.room_assignment[day, hour, course, "Temp Room"]) == 1

                else:  # If there are no preferred rooms, allow assignment to any room
                    return sum(model.room_assignment[day, hour, course, room] for room in model.rooms) == 1


            model.room_assignment_constraint = pyo.Constraint(model.days, model.hours, model.courses, rule=room_assignment_constraint)

            # Constraint: Same room for the same subject if scheduled right next to each other
            def same_room_next_to_each_other_constraint(model, day, hour, course, room):
                if hour == model.hours.last():  # If it's the last hour of the day, skip the constraint
                    return pyo.Constraint.Skip
                else:
                    next_hour = model.hours.next(hour)  # Get the next hour
                    return model.room_assignment[day, hour, course, room] == model.room_assignment[day, next_hour, course, room]

            model.same_room_next_to_each_other_constraint = pyo.Constraint(model.days, model.hours, model.courses, model.rooms, rule=same_room_next_to_each_other_constraint)
           
            # Constraint: Remove spaces between subjects by moving them up or down
            def remove_spaces_constraint(model, day, hour, course):
                if hour == model.hours.first():
                    next_hour = model.hours.next(hour)
                    if next_hour in model.hours:
                        return model.schedule[day, hour, course] - model.schedule[day, next_hour, course] <= 0
                    else:
                        return pyo.Constraint.Skip
                elif hour == model.hours.last():
                    prev_hour = model.hours.prev(hour)
                    if prev_hour in model.hours:
                        return model.schedule[day, hour, course] - model.schedule[day, prev_hour, course] <= 0
                    else:
                        return pyo.Constraint.Skip
                else:
                    next_hour = model.hours.next(hour)
                    prev_hour = model.hours.prev(hour)
                    if next_hour in model.hours and prev_hour in model.hours:
                        return model.schedule[day, hour, course] - (model.schedule[day, next_hour, course] + model.schedule[day, prev_hour, course]) <= 0
                    elif next_hour in model.hours:
                        return model.schedule[day, hour, course] - (model.schedule[day, next_hour, course] + model.schedule[day, prev_hour, course]) <= 0
                    elif prev_hour in model.hours:
                        return model.schedule[day, hour, course] - (model.schedule[day, next_hour, course] + model.schedule[day, prev_hour, course]) <= 0
                    else:
                        return pyo.Constraint.Skip

            model.remove_spaces_constraint = pyo.Constraint(model.days, model.hours, model.courses, rule=remove_spaces_constraint)






            # Objective
            def objective_rule(model):
                return sum(model.schedule[d, h, c] * model.hours_per_course[c] for d in model.days for h in model.hours for c in model.courses)

            model.objective = pyo.Objective(rule=objective_rule, sense=pyo.maximize)

            self.models.append(model)


    def solve(self):
        for model in self.models:
            solver = pyo.SolverFactory('cbc')
            result = solver.solve(model)
            print(result)
            

    def _create_course_abbreviations(self):

       
        # Abbreviations for MIAA courses
        self.abbreviations_miaa = {
            'Computational Tools for Data Science': 'CTDS',
            'Mathematical Foundations for Artificial Intelligence': 'MFAI',
            'Fundamentals of Artificial Intelligence': 'FAI',
            'Statistical Models for AI': 'SMAI',
            'Machine Learning Algorithms': 'MLA',
        }
        # Abbreviations for LEEC courses
        self.abbreviations_leec = {
            'Cálculo': 'CAL',
            'Matemática Discreta e Álgebra Linear': 'MDAL',
            'Teoria dos Circuitos Elétricos': 'TCE',
            'Sistemas Digitais': 'SD',
            'Programação Imperativa': 'PI',
        }
    
    

    # Ensure the following method is correctly aligned with the class definition.
    ############################################################################################################
    def print_schedule(self):
        # Create course abbreviations
        self._create_course_abbreviations()
        
        # Dictionary to map model index to class name
        class_names = {
            0: 'MIAA',
            1: 'LEEC',
        }
        
        for idx, model in enumerate(self.models):
            # Get class name from the dictionary based on index, default to 'Class {idx+1}' if not found
            class_name = class_names.get(idx, f'Class {idx+1}')
            
            print(f"Schedule for {class_name}:")
            print("+" + "-" * 150 + "+")
            print("| {:^25} |".format("Time/Day"), end="")
            for day in model.days:
                print(" {:^20} |".format(day), end="")
            print("\n+" + "-" * 150 + "+")
            for hour in model.hours:
                print("| {:^25} |".format(hour), end="")
                for day in model.days:
                    for course in model.courses:
                        if model.schedule[day, hour, course].value == 1:
                            # Lookup course abbreviation based on course name
                            course_abbr = self.abbreviations_miaa.get(course, self.abbreviations_leec.get(course, course))
                            # Get the assigned room for the course
                            assigned_room = None
                            for room in model.rooms:
                                if model.room_assignment[day, hour, course, room].value == 1:
                                    assigned_room = room
                                    break
                            print(" {:^15} ({:^5})|".format(course_abbr, assigned_room), end="")
                            break
                    else:
                        print(" {:^20} |".format("N"), end="")
                print("\n+" + "-" * 150 + "+")
        print()




    ############################################################################################################
    def print_and_export_schedule(self):
        # Create course abbreviations
        filename = "pdfSchedule.pdf"
        # Create course abbreviations
        self._create_course_abbreviations()

        # Styles for the PDF
        styles = getSampleStyleSheet()
        normal_style = styles['Normal']
        center_style = styles['Normal']
        center_style.alignment = TA_CENTER

        # Create the PDF
        pdf = SimpleDocTemplate(filename, pagesize=letter)
        elems = []

        for idx, model in enumerate(self.models):
            # Create a table for each course
            data = [["Time/Day"] + [day for day in model.days]]

            for hour in model.hours:
                row = [hour]
                for day in model.days:
                    course_info = ""
                    for course in model.courses:
                        if model.schedule[day, hour, course].value == 1:
                            course_abbr = self.abbreviations_miaa.get(course, self.abbreviations_leec.get(course, course))
                            assigned_room = None
                            for room in model.rooms:
                                if model.room_assignment[day, hour, course, room].value == 1:
                                    assigned_room = room
                                    break
                            course_info = f"{course_abbr} ({assigned_room})"
                            break
                    row.append(course_info)
                data.append(row)

            # Create the table
            title = Paragraph(f"<b>Schedule for Class {idx+1}:</b>", normal_style)
            table = Table(data)
            table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            # Add the title and table to the PDF elements
            elems.append(title)
            elems.append(table)
            elems.append(Spacer(1, 12))

        # Build elements and add them to the PDF
        pdf.build(elems)

