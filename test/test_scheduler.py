from scheduler_model import course_scheduler
import numpy as np 
import random
if __name__ == "__main__":
    # Args 
    days = ['Segunda','Terca','Quarta','Quinta', 'Sexta','Segunda2','Terca2','Quarta2','Quinta2', 'Sexta2']
    hours = [f"h_{i}" for i in np.array([8, 10, 14, 16])]
    subjects = ["Matematica", "Portugues", "Frances", "Programacao"]
    classes_per_subject = {'Class1': ("Matematica", "Portugues"), 'Class2': ("Frances", "Programacao")}
    turmas = ["Class1", "Class2"]

    # Initialize an empty list to store subject-class combinations
    subject_class_combinations = []

    # Iterate over classes and subjects to create combinations
    for turma in turmas:
        for subject in classes_per_subject[turma]:
            subject_class_combinations.append(f"{subject} {turma}")

    hours_per_subject = {subject: 2 for subject in subject_class_combinations}

    # Update hours for each class
    for turma in turmas:
        for subject in classes_per_subject[turma]:
            hours_per_subject[f"{subject} {turma}"] = random.randint(4, 7)

    max_hours_per_day = 2

    preferences = [
    ]

    constraints = [
    ]

    SCHEDULE = course_scheduler(days, hours, hours_per_subject, max_hours_per_day)
    SCHEDULE.create_model()
    SCHEDULE.update_preferences(preferences)
    SCHEDULE.update_constraints(constraints)
    SCHEDULE.solve_schedule()

    print(SCHEDULE.print_schedule())
