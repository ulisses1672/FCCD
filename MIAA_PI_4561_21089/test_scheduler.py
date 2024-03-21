from scheduler_model import course_scheduler
import random
import csv


def assign_teachers_to_courses(teachers_Subject, preferencas_dias_professores):
    """
    Assigns one respective teacher for each course based on teacher availability preferences.
    """
    course_teachers = {}
    for course, teachers in teachers_Subject.items():
        available_teachers = [teacher for teacher in teachers if preferencas_dias_professores.get(teacher)]
        if available_teachers:
            selected_teacher = random.choice(available_teachers)
            course_teachers[course] = selected_teacher
        else:
            # If no available teacher found, assign None
            course_teachers[course] = None
    return course_teachers


def csv_getvalues_courses(csv_file, encoding='utf-8'):
    courses_overall = {}
    with open(csv_file, newline='', encoding=encoding) as csvfile:
        reader = csv.DictReader(csvfile, dialect='excel')
        for row in reader:
            course = row['\ufeffcourse']
            subject = row['subj']
            quantity = int(row['quantityOfClasses'])
            if course not in courses_overall:
                courses_overall[course] = {subject: quantity}
            else:
                if subject in courses_overall[course]:
                    courses_overall[course][subject] += quantity
                else:
                    courses_overall[course][subject] = quantity
    return courses_overall


def read_rooms_from_csv(csv_file, encoding='utf-8'):
    
    rooms = {}
    with open(csv_file, newline='', encoding=encoding) as csvfile:
        reader = csv.DictReader(csvfile, dialect='excel')
        for row in reader:
            room = row['\ufeffsala']
            capacity = int(row['size'])
            rooms[room] = capacity
    return rooms

def read_course_room_preferences_from_csv(csv_file, encoding='utf-8'):
    
    preferences = {}
    with open(csv_file, newline='', encoding=encoding) as csvfile:
        reader = csv.DictReader(csvfile, dialect='excel')
        for row in reader:
            course = row['\ufeffsubj']
            room = row['salas']
            if course in preferences:
                preferences[course].append(room)
            else:
                preferences[course] = [room]
    return preferences

def read_teacher_course_preferences_from_csv(csv_file, encoding='utf-8'):
    
    preferences = {}
    with open(csv_file, newline='', encoding=encoding) as csvfile:
        reader = csv.DictReader(csvfile, dialect='excel')
        for row in reader:
            course = row['\ufeffsubj']
            teacher = row['professores']
            if course in preferences:
                preferences[course].append(teacher)
            else:
                preferences[course] = [teacher]
    return preferences



def read_teacher_availability_from_csv(csv_file, encoding='utf-8'):
    
    availability = {}
    with open(csv_file, newline='', encoding=encoding) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            teacher = row['\ufeffprofessores']
            day = row['dias']
            if teacher in availability:
                availability[teacher].append(day)
            else:
                availability[teacher] = [day]
    return availability

if __name__ == "__main__":
  

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    hours = [9, 10, 11, 12,13, 14, 15, 16, 17]

    salas = read_rooms_from_csv("salas.csv")
    discPreferenciasSala = read_course_room_preferences_from_csv("subjects_preferencias.csv")
    teachers_Subject = read_teacher_course_preferences_from_csv("subjects_professores.csv")
    preferencas_dias_professores = read_teacher_availability_from_csv("professores_preferencias.csv")
    courses_overall = csv_getvalues_courses("courses.csv")

    quantity_students = [20,20,22,20]
    
    max_hours_per_day = 8

    teachers_chosen = {}

    # Use the new function to assign teachers to courses
    assigned_teachers = assign_teachers_to_courses(teachers_Subject, preferencas_dias_professores)
    print("Assigned Teachers to Courses:")
    for course, teacher in assigned_teachers.items():
        print(f"{course}: {teacher}")
        teachers_chosen[course] = teacher

    # Create the scheduler and solve the model
    scheduler = course_scheduler(days, hours, courses_overall, max_hours_per_day,teachers_chosen, preferencas_dias_professores,salas,discPreferenciasSala,quantity_students)
    scheduler.create_model()
    result = scheduler.solve()

    # Print the schedule
    scheduler.print_schedule()  # Add this line to print the schedule
    scheduler.print_and_export_schedule()
    