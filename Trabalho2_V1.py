from pyomo.environ import *

# Create a Pyomo Concrete Model
model = ConcreteModel()

# Define sets for teachers, courses, and time slots
model.Teachers = Set()
model.Courses = Set()
model.TimeSlots = Set()

# Define parameters for the number of hours each course requires
#course_hours = {
#    'course1': 10,
#    'course2': 15,
#    'course3': 12,
#    # add more courses as needed
#}


# Define binary decision variables for scheduling classes
model.Schedule = Var(model.Teachers, model.Courses, model.TimeSlots, within=Binary)

# Define constraints to ensure each course is scheduled exactly once
def course_scheduling_constraint(model, course):
    return sum(model.Schedule[teacher, course, time] for teacher in model.Teachers for time in model.TimeSlots) == 1

model.CourseSchedulingConstraint = Constraint(model.Courses, rule=course_scheduling_constraint)

# Define constraints to ensure each teacher is scheduled at most once per time slot
def teacher_scheduling_constraint(model, teacher, time):
    return sum(model.Schedule[teacher, course, time] for course in model.Courses) <= 1

model.TeacherSchedulingConstraint = Constraint(model.Teachers, model.TimeSlots, rule=teacher_scheduling_constraint)

# Add any additional constraints based on the project requirements


# Define the objective function (minimize or maximize as per your requirements)
model.obj = Objective(expr=sum(model.Schedule[teacher, course, time] for teacher in model.Teachers
                               for course in model.Courses for time in model.TimeSlots), sense=maximize)




# Create a solver object (using Gurobi in this case)
solver = SolverFactory('gurobi')
solver.options['TimeLimit'] = 300  # Set a time limit in seconds
solver.options['MIPGap'] = 0.01  # Adjust the MIP gap tolerance
res = solver.solve(model, tee=True)  # Add tee=True for displaying solver logs
print(res)


# Solve the model
solver.solve(model)

# Print the results
for teacher in model.Teachers:
    for course in model.Courses:
        for time in model.TimeSlots:
            if value(model.Schedule[teacher, course, time]) == 1:
                print(f"Teacher: {teacher}, Course: {course}, Time: {time}")





