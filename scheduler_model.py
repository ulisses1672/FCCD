import pyomo.environ as pyo
import numpy as np
import pandas as pd

class course_scheduler:
    def __init__(self, days, hours, course_units_miaa, course_units_leec, max_hours_per_day):
        self.days = days
        self.hours = hours
        self.course_units_miaa = course_units_miaa
        self.course_units_leec = course_units_leec
        self.max_hours_per_day = max_hours_per_day
        self.model = pyo.ConcreteModel()
        self.schedule = None

    

    def create_model(self):
        model = self.model
        # Sets
        model.days = pyo.Set(initialize=self.days)
        model.hours = pyo.Set(initialize=self.hours)
        model.courses_miaa = pyo.Set(initialize=self.course_units_miaa.keys())
        model.courses_leec = pyo.Set(initialize=self.course_units_leec.keys())

        # Parameters
        model.hours_per_course_miaa = pyo.Param(model.courses_miaa, initialize=self.course_units_miaa)
        model.hours_per_course_leec = pyo.Param(model.courses_leec, initialize=self.course_units_leec)
        model.max_hours_per_day = self.max_hours_per_day

        # Variables
        model.schedule_miaa = pyo.Var(model.days, model.hours, model.courses_miaa, domain=pyo.Binary)
        model.schedule_leec = pyo.Var(model.days, model.hours, model.courses_leec, domain=pyo.Binary)

        # Objective: For demonstration, let's just maximize the total scheduled hours (this may vary based on actual needs)
        def objective_rule(model):
            return sum(model.schedule_miaa[d, h, c] * model.hours_per_course_miaa[c] for d in model.days for h in model.hours for c in model.courses_miaa) + \
                   sum(model.schedule_leec[d, h, c] * model.hours_per_course_leec[c] for d in model.days for h in model.hours for c in model.courses_leec)
        model.objective = pyo.Objective(rule=objective_rule, sense=pyo.maximize)

        # Constraints: Add basic constraints, e.g., max hours per day
        def max_hours_per_day_rule(model, d):
            return sum(model.schedule_miaa[d, h, c] for h in model.hours for c in model.courses_miaa) + \
                   sum(model.schedule_leec[d, h, c] for h in model.hours for c in model.courses_leec) <= model.max_hours_per_day
        model.max_hours_per_day_constraint = pyo.Constraint(model.days, rule=max_hours_per_day_rule)

        # Additional constraints can be added here

    def solve(self):
        #solver = pyo.SolverFactory('glpk')
        solver = pyo.SolverFactory('cbc')
        result = solver.solve(self.model)
        return result
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
        self._create_course_abbreviations()  # Ensure abbreviations are ready

        # Calculate the maximum width needed for any day, abbreviation, or time
        max_day_width = max(len(day) for day in self.days)
        max_course_width = max(max(len(abb) for abb in self.abbreviations_miaa.values()), max(len(abb) for abb in self.abbreviations_leec.values()))
        max_width = max(max_day_width, max_course_width, 10)  # 10 for the time column width

        # Initialize an empty schedule grid for MIAA and LEEC
        schedule_grid_miaa = {h: {d: '' for d in self.days} for h in self.hours}
        schedule_grid_leec = {h: {d: '' for d in self.days} for h in self.hours}

        # Fill in the schedule grid based on the optimization results
        for d in self.model.days:
            for h in self.model.hours:
                for c in self.model.courses_miaa:
                    if pyo.value(self.model.schedule_miaa[d, h, c]) > 0.5:
                        schedule_grid_miaa[h][d] = self.abbreviations_miaa[c]
                for c in self.model.courses_leec:
                    if pyo.value(self.model.schedule_leec[d, h, c]) > 0.5:
                        schedule_grid_leec[h][d] = self.abbreviations_leec[c]

        # Print the schedule grid for MIAA
        print("MIAA Schedule:")
        header = "Time".ljust(max_width) + " | " + " | ".join(day.ljust(max_width) for day in self.days)
        print(header)
        print("-" * len(header))
        for h in self.hours:
            print(f"{h.ljust(max_width)} | " + " | ".join(schedule_grid_miaa[h][d].ljust(max_width) for d in self.days))
        print("\n")

        # Print the schedule grid for LEEC
        print("LEEC Schedule:")
        print(header)  # Reuse the header defined above
        print("-" * len(header))
        for h in self.hours:
            print(f"{h.ljust(max_width)} | " + " | ".join(schedule_grid_leec[h][d].ljust(max_width) for d in self.days))
        print("\n")
