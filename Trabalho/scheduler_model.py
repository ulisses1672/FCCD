import pyomo.environ as pyo
import numpy as np
import pyomo.kernel as pmo
import pandas as pd

class course_scheduler:
    def __init__(self, days, hours, quantity_per_subject_per_class, max_quantity_subjects_per_day, turmas, classes_per_subject):
        self.days = days
        self.hours = hours
        self.turmas = turmas
        self.quantity_per_subject_per_class = quantity_per_subject_per_class
        self.classes_per_subject = classes_per_subject
        self.max_quantity_subjects_per_day = max_quantity_subjects_per_day
        self.model = None
        self.schedule = None
        
    def create_model(self):
        # MODEL DEFINITION ----------------------------------------------------------
        model = pyo.ConcreteModel()

        # Sets
        model.sDays = pyo.Set(initialize=self.days, ordered=True)
        model.sHours = pyo.Set(initialize=self.hours, ordered=True)
        model.sSubjectsPerClass = pyo.Set(initialize=self.classes_per_subject.values())
        model.sTurmas = pyo.Set(initialize=self.turmas)

        # Parameters
        # Initialize pHoursPerSubject, pMinDaysPerSubject, and pMaxDaysPerSubject based on quantity_per_subject_per_class
        model.pHoursPerSubject = pyo.Param(model.sTurmas, initialize=lambda model, turma: self.quantity_per_subject_per_class[turma])
        model.pMinDaysPerSubject = pyo.Param(model.sTurmas, initialize=lambda model, turma: self.quantity_per_subject_per_class[turma])
        model.pMaxDaysPerSubject = pyo.Param(model.sTurmas, initialize=lambda model, turma: self.quantity_per_subject_per_class[turma])

        model.pPreferences = pyo.Param(model.sTurmas,model.sDays, model.sHours, model.sSubjectsPerClass, initialize = 1.0, mutable = True)

        # Decision variable
        model.vbSubjectSchedule = pyo.Var(model.sTurmas,model.sDays, model.sHours, model.sSubjectsPerClass, domain=pmo.Binary)

        # Helper variables
        model.vbSubjectDaysFlags = pyo.Var(model.sTurmas,model.sDays, model.sSubjectsPerClass, domain=pmo.Binary)
        model.vIcumulatedHours = pyo.Var(model.sTurmas,model.sDays, model.sHours, model.sSubjectsPerClass, domain=pyo.NonNegativeIntegers)
        model.vIsubjectTotalDays = pyo.Var(domain=pyo.NonNegativeIntegers)
        model.vbSubjectSwitches = pyo.Var(model.sTurmas,model.sDays, model.sHours, model.sSubjectsPerClass, domain=pmo.Binary)

        # Constraints 
        #-------- hourly constraints
        # :: All the scheduled hours for a subject must be exactly the total weekly number of hours
        model.ctCoverAllHours = pyo.ConstraintList()
        for o in model.sTurmas:
            for k in model.sSubjectsPerClass:
                for g in model.pHoursPerSubject[o]:
                    model.ctCoverAllHours.add(sum(model.vbSubjectSchedule[o,i,j,k] for i in model.sDays for j in model.sHours) <= g)
                    model.ctCoverAllHours.add(sum(model.vbSubjectSchedule[o,i,j,k] for i in model.sDays for j in model.sHours) >= g)

        #-------- daily constraints
        # :: Each subject can be assigned to at most hours/max hours DAYS and at least 1 hour on each of the days it has been scheduled.
        model.ctSubjectDays = pyo.ConstraintList()
        for o in model.sTurmas:
            for k in model.sSubjectsPerClass:
                for g in model.pMaxDaysPerSubject[o]:
                    model.ctSubjectDays.add(sum(model.vbSubjectDaysFlags[o,i,k] for i in model.sDays) <= g)
                    model.ctSubjectDays.add(sum(model.vbSubjectDaysFlags[o,i,k] for i in model.sDays) >= g)

        
        #--------- block constraints
        # :: Cumulative constraints
        model.ctCumulativeHours = pyo.ConstraintList()

        for o in model.sTurmas:
            for k in model.sSubjectsPerClass:
                for i in model.sDays:
                    for j in model.sHours:
                        if j != model.sHours.first():
                            model.ctCumulativeHours.add(model.vIcumulatedHours[o,i,j,k] == model.vIcumulatedHours[o,i,model.sHours.prev(j),k]+model.vbSubjectSchedule[o,i,j,k])
                            model.ctCumulativeHours.add(model.vIcumulatedHours[o,i,j,k] >= model.vbSubjectSchedule[o,i,j,k])
                        else:
                            model.ctCumulativeHours.add(model.vIcumulatedHours[o,i,j,k] == 0)

        # :: Each subject must be given in consecutive blocks
        model.ctSubjectSwitches = pyo.ConstraintList()
        for o in model.sTurmas:
            for k in model.sSubjectsPerClass:
                for i in model.sDays:
                    for j in model.sHours:
                        model.ctSubjectSwitches.add(model.vbSubjectSchedule[o,i,j,k] - model.vbSubjectSchedule[o,i,model.sHours.prevw(j), k] <= model.vbSubjectSwitches[o,i,j,k])
                        model.ctSubjectSwitches.add(-model.vbSubjectSchedule[o,i,j,k] + model.vbSubjectSchedule[o,i,model.sHours.prevw(j), k] <= model.vbSubjectSwitches[o,i,j,k])
                    model.ctSubjectSwitches.add(sum(model.vbSubjectSwitches[o,i,j,k] for j in model.sHours) == 2*model.vbSubjectDaysFlags[o,i,k])

                    # :: Unless a subject can be allocated to a whole day session, the first and last hour of the day cannot be assigned to the same subject
                    if len(model.sHours) > 1:
                        model.ctSubjectSwitches.add(model.vbSubjectSchedule[o,i,model.sHours.first(), k] + model.vbSubjectSchedule[o,i,model.sHours.last(), k]  <= 1)

        #---------- assignment constraints
        # :: try to chunk subjects in as few days as possible, penalizing additional days
        model.ctCumulativeHours.add(model.vIsubjectTotalDays == sum(model.vbSubjectDaysFlags[o,i,k] for o in model.sTurmas for i in model.sDays for k in model.sSubjectsPerClass) - sum(g for k in model.sTurmas for g in model.pMinDaysPerSubject[k]))
        penalty = -5

        # Objective function
        maximize = 1
        #model.objSchedule = pyo.Objective(sense=-maximize, expr=penalty*(model.vIsubjectTotalDays) + sum(model.pPreferences[o,i,j,k]*model.vbSubjectSchedule[o,i,j,k] for i in model.sDays for j in model.sHours for k in model.sSubjectsPerClass for o in model.sTurmas))
        model.objSchedule= pyo.Objective(sense = -maximize, expr =  penalty*(model.vIsubjectTotalDays)+ sum(model.pPreferences[o,i,j,k]*model.vbSubjectSchedule[o,i,j,k] for o in model.sTurmas for i in model.sDays for j in model.sHours for k in model.sSubjectsPerClass))
        
        self.model = model

    def update_preferences(self, preferences):
        # Update preference constraints
        for turma, day, hour, subject, preference_value in preferences:
            self.model.pPreferences[turma, day, hour, subject] = preference_value

    def update_constraints(self, constraints):
        # Update constraint list
        self.model.ctFixedSlots = pyo.ConstraintList()
        # Update constraint expressions
        for turma, day, hour, subject, constraint_value in constraints:
            if constraint_value == 1:
                self.model.ctFixedSlots.add(expr=self.model.vbSubjectSchedule[turma, day, hour, subject] == constraint_value)
            else:
                self.model.ctFixedSlots.add(expr=self.model.vbSubjectSchedule[turma, day, hour, subject] <= 0)

    def solve_schedule(self):
        # Solve the scheduling problem
        opt = pyo.SolverFactory('cbc')
        res = opt.solve(self.model)
        print(res)

    def print_schedule(self):
        # Collect schedule information
        schedule_info = []
        for turma in self.model.sTurmas:
            for day in self.model.sDays:
                for hour in self.model.sHours:
                    for subject in self.model.sSubjectsPerClass:
                        schedule_info.append({
                            'turma': turma,
                            'day': day,
                            'hour': hour,
                            'subject': subject,
                            'class': self.model.vbSubjectSchedule[turma, day, hour, subject].value
                        })

        # Create a DataFrame to represent the schedule
        df_schedule = pd.DataFrame(schedule_info)
        df_schedule = df_schedule[df_schedule['class'] > 0].pivot_table(index=['hour', 'turma'], columns='day', values='subject')

        return df_schedule.loc[[h for h in self.model.sHours], [d for d in self.model.sDays]]

