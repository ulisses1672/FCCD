from scheduler_model import course_scheduler
import random



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




if __name__ == "__main__":
    #days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    #hours = [f"Hour_{i}" for i in range(8, 18)]
    # Adjusting hours to reflect actual time slots for readability
    #hours = ["9:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "1:00 PM", "2:00 PM", "3:00 PM", "4:00 PM", "5:00 PM", "6:00 PM"]
    # Define days, hours, and course units for both programs (simplified here)
    
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    hours = [9, 10, 11, 12,13, 14, 15, 16, 17]
    course_units_miaa = {'CTDS': 3, 'MFAI': 3, 'FAI': 4, 'SMAI': 2, 'MLA': 4}
    course_units_leec = {'CAL': 4, 'MDAL': 3, 'TCE': 3, 'SD': 3, 'PI': 4}
    max_hours_per_day = 6


    salas = {'salaA': 0,'salaB': 0, 'salaC': 0,'salaD': 0,'salaE': 0,'ginasio': 0,'lab': 0,'salaArtes': 0}

    discPreferenciasSala = {"Computational Tools for Data Science" : ["salaA", "salaB"] , 
                        'Mathematical Foundations for Artificial Intelligence': [],
                        'Fundamentals of Artificial Intelligence': [],
                        'Statistical Models for AI': [],
                        'Machine Learning Algorithms': ["salaE"],
                        'Cálculo': ["salaD", "salaC", "salaD"],
                        'Matemática Discreta e Álgebra Linear': ["salaB"],
                        'Teoria dos Circuitos Elétricos': [],
                        'Sistemas Digitais': [],
                        'Programação Imperativa': ["salaA", "lab"],
        }

    teachers_Subject = {"Computational Tools for Data Science" : ["Celia Oliveira", "Natalia Costa", "Carla Ferreira"] , 
                        'Mathematical Foundations for Artificial Intelligence': ["Celia Oliveira", "Beatriz Rodrigues", "Ana Oliveira"],
                        'Fundamentals of Artificial Intelligence': ["Clara Pereira", "Matilde Carvalho", "Ana Oliveira"],
                        'Statistical Models for AI': ["Carla Sousa", "Celia Santos"],
                        'Machine Learning Algorithms': ["Celia Oliveira", "Natalia Costa", "Carla Ferreira"],
                        'Cálculo': ["Silvia Fernandes", "Matilde Silva"],
                        'Matemática Discreta e Álgebra Linear': ["Carla Martins"],
                        'Teoria dos Circuitos Elétricos': ["Carla Sousa", "Maria Rodrigues", "Matilde Carvalho"],
                        'Sistemas Digitais': ["Silvia Fernandes", "Clara Oliveira", "Carla Ferreira"],
                        'Programação Imperativa': ["Clara Varzim", "Carla Ferreira"],
        }
    

    preferencas_dias_professores = {
                        "Celia Oliveira" : ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'] , 
                        'Natalia Costa': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'] ,  
                        'Carla Ferreira': ['Wednesday', 'Thursday', 'Friday'] , 
                        'Beatriz Rodrigues': ['Monday', 'Tuesday'] , 
                        'Ana Oliveira': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'] , 
                        'Clara Pereira': ['Monday', 'Tuesday', 'Wednesday', 'Thursday'] , 
                        'Matilde Carvalho': ['Monday', 'Tuesday', 'Wednesday'] ,  
                        'Carla Sousa': ['Wednesday', 'Thursday', 'Friday'] ,  
                        'Celia Santos': ['Tuesday', 'Wednesday', 'Thursday', 'Friday'] , 
                        'Silvia Fernandes': ['Monday', 'Tuesday', 'Thursday', 'Friday'] ,  
                        'Matilde Silva': ['Monday', 'Tuesday', 'Thursday', 'Friday'] ,  
                        'Marisa Oliveira':['Wednesday', 'Thursday', 'Friday'] , 
                        'Bruna Martins': ['Monday', 'Tuesday', 'Wednesday'] , 
                        'Carla Martins':['Wednesday'] ,  
                        'Maria Rodrigues': ['Monday', 'Tuesday', 'Wednesday', 'Friday'] , 
                        'Matilde Carvalho':['Monday', 'Tuesday', 'Friday'] ,  
                        'Clara Oliveira': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'] ,  
                        'Clara Varzim': [ 'Wednesday', 'Thursday'] , 
    }

    professoresAvaiability = {
                        "Celia Oliveira" : 0 , 
                        'Natalia Costa': 0 ,  
                        'Carla Ferreira': 0, 
                        'Beatriz Rodrigues': 0,
                        'Ana Oliveira': 0,
                        'Clara Pereira': 0, 
                        'Matilde Carvalho': 0, 
                        'Carla Sousa': 0,  
                        'Celia Santos': 0, 
                        'Silvia Fernandes': 0,  
                        'Matilde Silva': 0, 
                        'Marisa Oliveira':0,
                        'Bruna Martins': 0,
                        'Carla Martins':0,
                        'Maria Rodrigues':0,
                        'Matilde Carvalho':0,
                        'Clara Oliveira': 0,
                        'Clara Varzim': 0,
    }


    course_units_miaa = {
        'Computational Tools for Data Science': 3,
        'Mathematical Foundations for Artificial Intelligence': 2,
        'Fundamentals of Artificial Intelligence': 3,
        'Statistical Models for AI': 2,
        'Machine Learning Algorithms': 2,
    }

    course_units_leec = {
        'Cálculo': 4,
        'Matemática Discreta e Álgebra Linear': 2 ,
        'Teoria dos Circuitos Elétricos': 3,
        'Sistemas Digitais': 5,
        'Programação Imperativa': 4,
    }

    courses_overall = [course_units_leec]

    max_hours_per_day = 8

    teachers_chosen = {}

    # Use the new function to assign teachers to courses
    assigned_teachers = assign_teachers_to_courses(teachers_Subject, preferencas_dias_professores)
    print("Assigned Teachers to Courses:")
    for course, teacher in assigned_teachers.items():
        print(f"{course}: {teacher}")
        teachers_chosen[course] = teacher

    # Assume course_units_miaa, course_units_leec, days, hours, and max_hours_per_day are already defined
    scheduler = course_scheduler(days, hours, courses_overall, max_hours_per_day,teachers_chosen, preferencas_dias_professores,salas,discPreferenciasSala)

    #scheduler = course_scheduler(days, hours, course_units_miaa, course_units_leec, max_hours_per_day)
    scheduler.create_model()
    result = scheduler.solve()
    scheduler.print_schedule()  # Add this line to print the schedule

    