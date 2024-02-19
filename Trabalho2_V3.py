from pyomo.environ import *

# Define sets
model = ConcreteModel()

model.courses = Set()  # Set of courses
model.teachers = Set()  # Set of teachers
model.rooms = Set()  # Set of classrooms
model.timeslots = Set()  # Set of timeslots (assuming daily slots)

# Define parameters
model.course_duration = Param(model.courses, within=PositiveIntegers)  # Duration of each course (8-20 hours)
model.room_capacity = Param(model.rooms, within=PositiveIntegers)  # Capacity of each room (fixed to 30)
model.teacher_availability = Param(model.teachers, model.timeslots, within=Binary)  # All teachers available (fixed to 1)
model.course_requirements = Param(model.courses, model.teachers, within=Binary)  # All courses require a teacher (fixed to 1)

# Define decision variables
model.assignment = Var(model.courses, model.timeslots, model.rooms, within=Binary)  # Assign course to timeslot and room

# Define objective function (optional, e.g., minimize number of used rooms)
# model.minimize = Objective(expr=sum(model.assignment[c, t, r] for c in model.courses for t in model.timeslots for r in model.rooms))

# Define constraints
# Ensure only one course assigned per timeslot and room
#model.one_course_per_slot_room = Constraint(model.timeslots, model.rooms, rule=sum(model.assignment[c, t, r] for c in model.courses) <= 1)
# Ensure only one course assigned per timeslot and room (corrected)
model.one_course_per_slot_room = Constraint(model.timeslots, model.rooms, rule=lambda model, t, r: sum(model.assignment[c, t, r] for c in model.courses) <= 1)


# Ensure no teacher conflicts (all available)
model.no_teacher_conflicts = Constraint(model.courses, model.timeslots, rule=lambda model, c, t: sum(model.assignment[c, t, r] * model.course_requirements[c, teacher] for teacher in model.teachers for r in model.rooms) <= 1)

# Ensure room capacity not exceeded
model.room_capacity_constraint = Constraint(model.timeslots, model.rooms, rule=lambda model, t, r: sum(model.assignment[c, t, r] * model.course_requirements[c, teacher] * model.course_duration[c] for c in model.courses for teacher in model.teachers) <= model.room_capacity[r])

# Course duration requirement (example)
model.course_duration_constraint = Constraint(model.courses, rule=lambda model, c: sum(model.assignment[c, t, r] for t in model.timeslots for r in model.rooms) * model.course_duration[c] >= 8)

# Create a solver instance (e.g., for Gurobi)
solver = SolverFactory('gurobi')

# Solve the model
result = solver.solve(model)
res = solver.solve(model, tee=True)  # Add tee=True for displaying solver logs
print(res)

# Print the results (if solution found)
if result.solver.status == SolverStatus.ok:
    for c in model.courses:
        for t in model.timeslots:
            for r in model.rooms:
                if model.assignment[c, t, r].value > 0.5:
                    print(f"Course {c} assigned to timeslot {t} in room {r}")
else:
    print("No feasible solution found!")
