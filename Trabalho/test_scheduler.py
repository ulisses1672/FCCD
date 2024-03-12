from scheduler_model import course_scheduler
import numpy as np 

if __name__ == "__main__":
    # Args 


    days = ['Segunda','Terca','Quarta','Quinta', 'Sexta']
    hours = [f"h_{i}" for i in np.array([8, 10, 14, 16])]
    subjects = ["Matematica","Portugues","Frances","Programacao","Artes"]

    length_of_subjects = len(subjects)

    # Define your subjects

    # Define your classes
    turmas = ["Class1", "Class2", "Class3"]

    classes_per_subject = {'Class1': ["Matematica", "Portugues" ,"Artes"],
                       "Class2":["Programacao", "Portugues" ,"Artes"],
                       "Class3":["Programacao", "Frances" ,"Matematica"]}

    # Initialize an empty dictionary to store the quantity of subjects for each class
    quantity_per_subject = {turma: [2 for _ in range(len(classes_per_subject[turma]))] for turma in turmas}

# Update the quantity of subjects for each class
    for turma in turmas:
        for _ in range(4):
            index = np.random.randint(0, len(classes_per_subject[turma]))
            quantity_per_subject[turma][index] += 1


    max_quantity_subjects_per_day = 2

    
    TamanhoTurmas = dict(zip(turmas, [20 for i in range(20)]))

    for i in np.random.choice(turmas, 3):
        TamanhoTurmas[i]+=1

    # Initialize an empty dictionary to store subjects for each class
    turmasComSubjects = {}

    for turma in turmas:
        # Randomly select 1 to 3 subjects for each turma
        num_subjects = np.random.randint(1, 4)
        selected_subjects = np.random.choice(subjects, num_subjects, replace=False).tolist()
        
        # Store the selected subjects for the current turma
        turmasComSubjects[turma] = selected_subjects

    preferences = [
        # ('Quarta', f"h_{14}", 'Frances', 4)
    ]

    constraints = [
       #  ('Segunda', f"h_{10}", 'Matematica',  1)
    ]

    SCHEDULE = course_scheduler(days, hours, quantity_per_subject, max_quantity_subjects_per_day,turmas , classes_per_subject)
    SCHEDULE.create_model()
    SCHEDULE.update_preferences(preferences)
    SCHEDULE.update_constraints(constraints)
    SCHEDULE.solve_schedule()

    print(SCHEDULE.print_schedule())
