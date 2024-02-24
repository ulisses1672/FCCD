from scheduler_model import course_scheduler
import numpy as np 

if __name__ == "__main__":
    # Args 
    days = ['Segunda','Terca','Quarta','Quinta', 'Sexta']
    hours = [f"h_{i}" for i in np.array([8, 10, 14, 16])]
    subjects = ["Matematica","Portugues","Frances","Programacao","Artes"]

    length_of_subjects = len(subjects)

    hours_per_subject = dict(zip(subjects, [2 for i in range(length_of_subjects)]))

    for i in np.random.choice(subjects, length_of_subjects):
        hours_per_subject[i]+=1

    max_hours_per_day = 4

    turma = ["Class1","Class2","Class3"]

    TamanhoTurmas = dict(zip(turma, [20 for i in range(20)]))

    for i in np.random.choice(turma, 3):
        TamanhoTurmas[i]+=1

    preferences = [
        ('Quarta', f"h_{14}", 'Frances', 4)
    ]

    constraints = [
        ('Segunda', f"h_{10}", 'Matematica',  1)
    ]

    SCHEDULE = course_scheduler(days, hours, hours_per_subject, max_hours_per_day)
    SCHEDULE.create_model()
    SCHEDULE.update_preferences(preferences)
    SCHEDULE.update_constraints(constraints)
    SCHEDULE.solve_schedule()

    print(SCHEDULE.print_schedule())
