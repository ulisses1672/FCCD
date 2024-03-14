import pyomo.environ as pyo
import numpy as np
import pandas as pd

class course_scheduler:
    def __init__(self, days, hours, courses_overall, max_hours_per_day,teachers_Subject , preferencas_dias_professores):
        self.days = days
        self.hours = hours
        self.courses_overall = courses_overall
        self.max_hours_per_day = max_hours_per_day
        self.teachers_SubjectT = teachers_Subject
        self.teachers_Subject = dict(teachers_Subject)
        self.preferencas_dias_professores = dict(preferencas_dias_professores)

        self.models = []

class course_scheduler:
    def __init__(self, days, hours, courses_overall, max_hours_per_day, teachers_Subject, preferencas_dias_professores):
        self.days = days
        self.hours = hours
        self.courses_overall = courses_overall
        self.max_hours_per_day = max_hours_per_day
        self.teachers_SubjectT = teachers_Subject
        self.teachers_Subject = dict(teachers_Subject)
        self.preferencas_dias_professores = dict(preferencas_dias_professores)

        self.models = []

    def create_model(self):
        for courses in self.courses_overall:
            model = pyo.ConcreteModel()
            # Sets
            model.days = pyo.Set(initialize=self.days)
            model.hours = pyo.Set(initialize=self.hours)
            model.courses = pyo.Set(initialize=courses.keys())
            model.teachers = pyo.Set(initialize={teacher for teachers in self.teachers_Subject.values() for teacher in teachers})
            model.teachersSubj = pyo.Set(initialize=self.teachers_Subject.keys())

            # Parameters
            model.hours_per_course = pyo.Param(model.courses, initialize=courses)
            model.max_hours_per_day = self.max_hours_per_day
            # Max hours per week per course
            model.max_hours_per_week = {course: hours for course, hours in courses.items()}

            # Variables
            model.schedule = pyo.Var(model.days, model.hours, model.courses, domain=pyo.Binary)

            # Constraints
            def max_hours_per_day_rule(model, d):
                return sum(model.schedule[d, h, c] for h in model.hours for c in model.courses) <= model.max_hours_per_day

            def max_hours_per_week_rule(model, c):
                return sum(model.schedule[d, h, c] for d in model.days for h in model.hours) <= model.max_hours_per_week[c]
            
            def max_hours_per_day_per_course_rule(model, d, c):
                return sum(model.schedule[d, h, c] for h in model.hours) <= 2
            
            def teacher_availability_rule(model, d, h, c):
                available_teachers = [teacher for teacher in self.teachers_Subject[c] if d in self.preferencas_dias_professores[teacher]]
                return sum(model.schedule[d, h, c] for teacher in available_teachers) >= model.schedule[d, h, c]

            model.max_hours_per_day_constraint = pyo.Constraint(model.days, rule=max_hours_per_day_rule)
            model.max_hours_per_week_constraint = pyo.Constraint(model.courses, rule=max_hours_per_week_rule)
            model.max_hours_per_day_per_course_constraint = pyo.Constraint(model.days, model.courses, rule=max_hours_per_day_per_course_rule)
            model.teacher_availability_constraint = pyo.Constraint(model.days, model.hours, model.courses, rule=teacher_availability_rule)

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
            print("+" + "-" * 120 + "+")
            print("| {:^20} |".format("Time/Day"), end="")
            for day in model.days:
                print(" {:^12} |".format(day), end="")
            print("\n+" + "-" * 120 + "+")
            for hour in model.hours:
                print("| {:^20} |".format(hour), end="")
                for day in model.days:
                    course_found = False
                    for course in model.courses:
                        if model.schedule[day, hour, course].value == 1:
                            course_abbr = self.abbreviations_miaa.get(course, self.abbreviations_leec.get(course, course))
                            print(" {:^12} |".format(course_abbr), end="")
                            course_found = True
                            break
                    if not course_found:
                        print(" {:^12} |".format("No class"), end="")
                print("\n+" + "-" * 120 + "+")
        print()



