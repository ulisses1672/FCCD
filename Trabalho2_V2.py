from pyomo.environ import *

# Create a Pyomo model
model = ConcreteModel()

# Define sets
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
timeslots = ['9:00-11:00', '11:00-13:00', '13:00-15:00', '15:00-17:00']
courses = ['Math 101', 'History 202', 'CS 301']
teachers = ['Smith', 'Johnson', 'Lee']
rooms = ['Room A', 'Room B', 'Room C']

# Decision variables
model.x = Var(days, timeslots, courses, within=Binary)

# Constraints
def no_overlap_rule(model, d, t):
    return sum(model.x[d, t, c] for c in courses) <= 1
model.no_overlap = Constraint(days, timeslots, rule=no_overlap_rule)

# Objective function (minimize conflicts)
model.obj = Objective(expr=sum(model.x[d, t, c] for d in days for t in timeslots for c in courses), sense=minimize)

# Solver setup (Gurobi in this case)
opt = SolverFactory('gurobi')
results = opt.solve(model)
res = opt.solve(model, tee=True)  # Add tee=True for displaying solver logs
print(res)

# Print the timetable
for d in days:
    print(f"\n{d}:")
    for t in timeslots:
        for c in courses:
            if model.x[d, t, c].value == 1:
                print(f"{t} - {c}")

