
import pandas as pd
from pyomo.environ import *
from pyomo.opt import SolverFactory

# Load the CSV file
file_path = 'D:/_MIAA/FCCD/Trabalho_FCCD/1Csv.csv'  # Update this with the path to your CSV file
data = pd.read_csv(file_path)

# Define your sets for days and hours
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
hours = ["9", "10", "11", "12", "14", "15", "16", "17"]
rooms = list('ABCDEFGHIJKLMNO')

# Function to solve the scheduling for a single course
def solve_scheduling_for_course(course_data):
    model = ConcreteModel()

    # Sets based on the course data
    subjects = course_data['Subjects'].unique()

    # Variables
    model.timeslots = Set(initialize=[(subject, hour, day, room) for subject in subjects for hour in hours for day in days for room in rooms])
    model.x = Var(model.timeslots, within=Binary)

    # Constraints
    
    def max_hours_rule(model, subject):
        return sum(model.x[subject, hour, day, room] for hour in hours for day in days for room in rooms) == data.loc[data['Subjects'] == subject, 'MaxHours'].values[0]

    #model.max_hours_constraint = Constraint(subjects, rule=max_hours_rule)

    def room_conflict_rule(model, hour, day, room):
        return sum(model.x[subject, hour, day, room] for subject in subjects) <= 1

    model.room_conflict_constraint = Constraint(hours, days, rooms, rule=room_conflict_rule)

    def max_hours_rule(model, subject):
        # Retrieve the MaxHours values for the subject
        max_hours_values = data.loc[data['Subjects'] == subject, 'MaxHours'].values
        
        # Check if max_hours_values is empty, and if so, return a constraint that effectively deactivates the constraint for this subject
        if len(max_hours_values) == 0:
            # Assuming a subject must at least have 0 hours (effectively skipping this constraint)
            return Constraint.Skip
        else:
            # Proceed as normal if there are values
            return sum(model.x[subject, hour, day, room] for hour in hours for day in days for room in rooms) == max_hours_values[0]


    # Solve the model
    solver = SolverFactory('cbc')
    result = solver.solve(model)

    # Process the results
    timetable = []
    for (subject, hour, day, room), value in model.x.items():
        if value.value == 1:
            timetable.append((subject, day, hour, room))

    # Convert to DataFrame for easier viewing
    return pd.DataFrame(timetable, columns=['Subject', 'Day', 'Hour', 'Room'])

# Loop through each course and solve its scheduling
for course_name, group in data.groupby('Course'):
    timetable_df = solve_scheduling_for_course(group)
    print(f"Timetable for {course_name}:")
    print(timetable_df.to_string(index=False))
    print("\n" + "="*50 + "\n")
