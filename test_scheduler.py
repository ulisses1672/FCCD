from scheduler_model import course_scheduler

if __name__ == "__main__":
    #days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    #hours = [f"Hour_{i}" for i in range(8, 18)]
    # Adjusting hours to reflect actual time slots for readability
    #hours = ["9:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "1:00 PM", "2:00 PM", "3:00 PM", "4:00 PM", "5:00 PM", "6:00 PM"]
    # Define days, hours, and course units for both programs (simplified here)
    
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    hours = ["9:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "1:00 PM", "2:00 PM", "3:00 PM", "4:00 PM"]
    course_units_miaa = {'CTDS': 3, 'MFAI': 3, 'FAI': 4, 'SMAI': 2, 'MLA': 4}
    course_units_leec = {'CAL': 4, 'MDAL': 3, 'TCE': 3, 'SD': 3, 'PI': 4}
    max_hours_per_day = 6


    # Define a list of teachers
    teachers = [
    "Celia Oliveira", "Natalia Costa", "Carla Ferreira", "Beatriz Rodrigues", "Ana Oliveira",
    "Clara Pereira", "Olga Costa", "Matilde Carvalho", "Carla Sousa", "Celia Santos",
    "Silvia Fernandes", "Clara Varzim", "Maria Rodrigues", "Clara Oliveira", "Carla Martins",
    "Bruna Martins", "Marisa Oliveira", "Matilde Silva"
    ]


    course_units_miaa = {
        'Computational Tools for Data Science': 3,
        'Mathematical Foundations for Artificial Intelligence': 3,
        'Fundamentals of Artificial Intelligence': 4,
        'Statistical Models for AI': 2,
        'Machine Learning Algorithms': 4,
    }

    course_units_leec = {
        'Cálculo': 4,
        'Matemática Discreta e Álgebra Linear': 3,
        'Teoria dos Circuitos Elétricos': 3,
        'Sistemas Digitais': 3,
        'Programação Imperativa': 4,
    }

    max_hours_per_day = 6

    # Assume course_units_miaa, course_units_leec, days, hours, and max_hours_per_day are already defined
    scheduler = course_scheduler(days, hours, course_units_miaa, course_units_leec, max_hours_per_day)

    #scheduler = course_scheduler(days, hours, course_units_miaa, course_units_leec, max_hours_per_day)
    scheduler.create_model()
    result = scheduler.solve()
    scheduler.print_schedule()  # Add this line to print the schedule

    