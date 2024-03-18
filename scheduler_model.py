import pyomo.environ as pyo
import numpy as np
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

class course_scheduler:
    def __init__(self, days, hours, courses_overall, max_hours_per_day, teachers_Subject, preferencas_dias_professores, salas, discPreferenciasSala):
        self.days = days
        self.hours = hours
        self.courses_overall = courses_overall
        self.max_hours_per_day = max_hours_per_day
        self.teachers_Subject = dict(teachers_Subject)
        self.preferencas_dias_professores = dict(preferencas_dias_professores)
        self.salas = dict(salas)
        self.discPreferenciasSala = dict(discPreferenciasSala)
        self.models = []

    def create_model(self):
        for courses in self.courses_overall:
            model = pyo.ConcreteModel()
            # Sets
            model.days = pyo.Set(initialize=self.days)
            model.hours = pyo.Set(initialize=self.hours)
            model.courses = pyo.Set(initialize=courses.keys())

            # Parameters
            model.teacher_indices = pyo.Set(initialize=self.teachers_Subject.keys())
            model.teacher = pyo.Param(model.teacher_indices, initialize=self.teachers_Subject)

            model.rooms = pyo.Set(initialize=self.salas.keys())

            # Parameters
            model.hours_per_course = pyo.Param(model.courses, initialize=courses)
            model.max_hours_per_day = self.max_hours_per_day
            # Max hours per week per course
            model.max_hours_per_week = {course: hours for course, hours in courses.items()}

            # Variables
            model.schedule = pyo.Var(model.days, model.hours, model.courses, domain=pyo.Binary)
            model.room_assignment = pyo.Var(model.days, model.hours, model.courses, model.rooms, domain=pyo.Binary)

           

            def max_hours_per_week_rule(model, c):
                return sum(model.schedule[d, h, c] for d in model.days for h in model.hours) <= model.max_hours_per_week[c]

            def max_hours_per_day_per_course_rule(model, d, c):
                return sum(model.schedule[d, h, c] for h in model.hours) <= 2  # Limit each subject to 2 hours per day


            def room_availability_rule(model, d, h, c):
                return sum(model.room_assignment[d, h, c, room] for room in model.rooms) == 1

            def room_preferences_rule(model, d, h, c):
                course_preferences = self.discPreferenciasSala.get(c, [])
                if course_preferences:
                    return sum(model.room_assignment[d, h, c, room] for room in course_preferences) >= model.schedule[d, h, c]
                else:
                    return pyo.Constraint.Skip  # Skip constraint if there are no preferences

            def consecutive_blocks_rule(model, d, h, c):
                if model.max_hours_per_week[c] % 2 == 1:
                    # If the total hours for the week are odd, allow solo classes
                    return pyo.Constraint.Skip
                else:
                    # Otherwise, enforce consecutive blocks
                    # Check if the current hour is the first hour of the day
                    if h == model.hours.first():
                        return model.schedule[d, h, c] <= model.schedule[d, model.hours.next(h), c]
                    # Check if the current hour is the last hour of the day
                    elif h == model.hours.last():
                        return model.schedule[d, h, c] <= model.schedule[d, model.hours.prev(h), c]
                    else:
                        # If not the first or last hour, check if the course is scheduled consecutively
                        return model.schedule[d, h, c] <= model.schedule[d, model.hours.next(h), c] + model.schedule[d, model.hours.prev(h), c]

                # Teacher preferences constraint
            # Define constraint to enforce teacher availability
            def teacher_availability_constraint_rule(model, d, h, c):
                assigned_teacher = model.teacher[c]  # Get the assigned teacher for the course
                if assigned_teacher in self.preferencas_dias_professores:
                    # If the assigned teacher is in the preferences dictionary
                    if d in self.preferencas_dias_professores[assigned_teacher]:
                        # If the assigned teacher is available on the scheduled day, return True
                        return model.schedule[d, h, c] <= 1
                    else:
                        # If the assigned teacher is not available on the scheduled day, return False
                        return model.schedule[d, h, c] <= 0
                else:
                    # If the assigned teacher is not in the preferences dictionary, return True
                    return model.schedule[d, h, c] <= 1

            # Add the constraint to the model
            model.teacher_availability_constraint = pyo.Constraint(model.days, model.hours, model.courses, rule=teacher_availability_constraint_rule)

            model.room_availability_constraint = pyo.Constraint(model.days, model.hours, model.courses, rule=room_availability_rule)
            model.room_preferences_constraint = pyo.Constraint(model.days, model.hours, model.courses, rule=room_preferences_rule)

            model.consecutive_blocks_constraint = pyo.Constraint(model.days, model.hours, model.courses, rule=consecutive_blocks_rule)

            model.max_hours_per_day_per_course_constraint = pyo.Constraint(model.days, model.courses, rule=max_hours_per_day_per_course_rule)
            model.max_hours_per_week_constraint = pyo.Constraint(model.courses, rule=max_hours_per_week_rule)


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

        for idx, model in enumerate(self.models):
            print(f"Schedule for Class {idx+1}:")
            print("+" + "-" * 150 + "+")
            print("| {:^25} |".format("Time/Day"), end="")
            for day in model.days:
                print(" {:^12} |".format(day), end="")
            print("\n+" + "-" * 150 + "+")
            for hour in model.hours:
                print("| {:^25} |".format(hour), end="")
                for day in model.days:
                    for course in model.courses:
                        if model.schedule[day, hour, course].value == 1:
                            course_abbr = self.abbreviations_miaa.get(course, self.abbreviations_leec.get(course, course))
                            room_assigned = None
                            for room in model.rooms:
                                if model.room_assignment[day, hour, course, room].value == 1:
                                    room_assigned = room
                                    break
                            print(" {:^10}({:^10}) |".format(course_abbr, room_assigned), end="")
                            break
                    else:
                        print(" {:^22} |".format("No class"), end="")
                print("\n+" + "-" * 150 + "+")
        print()


        
    def print_and_export_schedule(self):
        filename = 'schedule.pdf'
        # Create course abbreviations
        self._create_course_abbreviations()

        # Prepare the data for the PDF
        data = []

        for idx, model in enumerate(self.models):
            # Add the header row to the data
            data.append(["Schedule for Class", f"{idx+1}"])

            # Add the Time/Day row to the data
            data.append(["Time/Day"] + [day for day in model.days])

            # Loop over each hour
            for hour in model.hours:
                row = [hour]
                # Loop over each day
                for day in model.days:
                    # Loop over each course
                    for course in model.courses:
                        # Check if the course is scheduled for this hour and day
                        if model.schedule[day, hour, course].value == 1:
                            # Get the abbreviation of the course
                            course_abbr = self.abbreviations_miaa.get(course, self.abbreviations_leec.get(course, course))
                            room_assigned = None
                            # Find the room assigned to the course for this hour and day
                            for room in model.rooms:
                                if model.room_assignment[day, hour, course, room].value == 1:
                                    room_assigned = room
                                    break
                            # Add the course abbreviation and room assignment to the row
                            row.append(f"{course_abbr}({room_assigned})")
                            break
                    else:
                        # If no course is scheduled for this hour and day, add "No class" to the row
                        row.append("No class")
                # Add the row to the data
                data.append(row)

        # Create the PDF
        pdf = SimpleDocTemplate(filename, pagesize=letter)
        table = Table(data)
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BACKGROUND', (0, 0), (-1, 1), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 1), colors.whitesmoke),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elems = [table]
        pdf.build(elems)





