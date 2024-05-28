import random

file = open("late_days.txt", "a")
for i in range(0, 5000):
    name = ""
    if i % 2 == 0:
        name = "ducky"
        grade = "51"
    else:
        name = "rubber"
        grade = "52"

    date = str(random.randint(1, 30)) + "/" + str(random.randint(1, 12)) + "/2024"

    minutes = str(random.randint(1, 100))
    file.write(name + ";" + grade + ";" + date + ";" + minutes + "\n")