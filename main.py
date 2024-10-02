from flask import Flask, render_template, request
import random
import math
from os.path import exists
import time
from unidecode import unidecode

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_student', methods=['POST'])
def send_student():
    name = unidecode(str(request.form['student_name']).lower())
    grade = str(request.form['grade']).lower()
    date = str(request.form['date']).lower()
    minutes = str(request.form['minutes']).lower()
    late_index = 1
    print(name)
    print(grade)
    print(date)
    print(minutes)
    for line in open("late_days.txt", "r", encoding='utf-8').readlines():
        if name in str(line):
            late_index += 1
    output = f'Name: {name}\nGrade: {grade}\nDate: {date}\nMinutes: {minutes}'
    output = output.replace("\n", "<br>")
    open("late_days.txt", "a", encoding='utf-8').write(name + ";" + grade + ";" + date + ";" + minutes + ";" + str(late_index) + "\n")
    return render_template('index.html', output=output)

@app.route('/get_student', methods=['POST'])
def get_student():
    name = request.form['student_name2']
    grade = request.form['grade2']
    output = ""
    late_days = open("late_days.txt", "r").readlines()
    for line in late_days:
        if name in line and line.split(";")[1] == grade:
            data = line.split(";")
            name_ = data[0]
            grade = data[1]
            date = data[2]
            minutes = data[3]
            output += name_ + " atrasou " + minutes + " minutos dia " + date + "<br>"
    return render_template('index.html', output=output)

def sort_students_by_late_days(student_list):
    def late_days_key(student):
        return int(student[1])
    sorted_student_list = sorted(student_list, key=late_days_key, reverse=True)
    
    return sorted_student_list
    
def sort_students_by_minutes(student_list):
    def late_days_key(student):
        return int(student[2])
    sorted_student_list = sorted(student_list, key=late_days_key, reverse=True)
    
    return sorted_student_list

@app.route('/frequency_rank', methods=['POST'])
def frequency_rank():
    output = ""
    late_days = open("late_days.txt", "r").readlines()
    minutes_total = 0
    
    students = {}
    
    for line in late_days:
        data = line.split(";")
        name = data[0]
            
        new_student = {
        "late_days": 0,
        "minutes": 0
        }
        students[name] = new_student
    
    for line in late_days:
        data = line.split(";")
        name = data[0]
        grade = data[1]
        date = data[2]
        minutes = data[3]
        minutes_total += int(minutes)
        late_days_ = data[4]
        students[name]["late_days"] += 1
        students[name]["minutes"] += int(minutes)
            
    student_list = []
    
    for name, data in students.items():
        student_list.append([name, str(data["late_days"]), str(data["minutes"])])
        
    student_list = sort_students_by_late_days(student_list)
    
    for i in range(0, len(student_list)):
        output += str(i) + ". " + student_list[i][0] + ", " + student_list[i][1] + " atrasos, " + student_list[i][2] + " minutos<br>"
    print("Total minutes: " + str(minutes_total))
    return render_template('index.html', output=output)
   
@app.route('/minutes_rank', methods=['POST'])
def minutes_rank():
    output = ""
    late_days = open("late_days.txt", "r").readlines()
    
    students = {}
    
    for line in late_days:
        data = line.split(";")
        name = data[0]
            
        new_student = {
        "late_days": 0,
        "minutes": 0
        }
        students[name] = new_student
    
    for line in late_days:
        data = line.split(";")
        name = data[0]
        grade = data[1]
        date = data[2]
        minutes = data[3]
        late_days_ = data[4]
        students[name]["late_days"] += int(late_days_)
        students[name]["minutes"] += int(minutes)
            
    student_list = []
    
    for name, data in students.items():
        student_list.append([name, str(data["late_days"]), str(data["minutes"])])
        
    student_list = sort_students_by_minutes(student_list)
    
    for i in range(0, len(student_list)):
        output += str(i) + ". " + student_list[i][0] + ", " + student_list[i][1] + " atrasos, " + student_list[i][2] + " minutos<br>"

    return render_template('index.html', output=output)

def load_neurons(neurons_file):
    neurons = []
    neurons_aux = neurons_file.replace("[", "").replace("]", "").replace(" ", "").split(",")
    for i in range(0, len(neurons_aux)):
        neurons.append(float(neurons_aux[i]))
    return neurons

def load_weights(weights_file, weights):
    weight_matrix_lines = weights_file.replace(" ", "").replace("[", "").replace("]]", "]").split("]")
            
    for i in range(0, len(weight_matrix_lines)):
        current_weight_line = weight_matrix_lines[i]
        matrix_aux = current_weight_line.split(",")
        matrix_line = []
        print("\n\nMatrix lines of size " + str(len(weight_matrix_lines)))
        print("\n\nMatrix aux of size " + str(len(matrix_aux)))
        for i in range(0, len(matrix_aux)):
            if matrix_aux[i] != "":
                matrix_line.append(float(matrix_aux[i]))
        weights.append(matrix_line)
    weights.pop() # there's an empty one at the end lol
    print(len(weights))
    print(len(weights[0]))
    return weights

def save_state(weights, neurons):
    file1 = open("weights.txt", "w")
    file1.write(str(weights))
    file2 = open("neurons.txt", "w")
    file2.write(str(neurons))
    file1.close()
    file2.close()

def sigmoid(number):
    result = number/(math.sqrt(1 + number**2))
    return result
            
def unsigmoid(x):
                print("Getting value for: " + str(abs(x)))
                result = abs(math.sqrt((0-x**2)/(x**2 - 1)))
                return result

#def feed_forward():


@app.route('/train', methods=['POST'])
def train_ai():
    # 84 layers, with the last one being the output of 3 neurons
    # 3738 neurons, last 3 being the output
    output = ""
    iterations = request.form['iterations']

    first_time = False

    neuron_layers = [[], [], [], []]
    neurons_ever = 0

    weights = []
    neurons = []

    weights_file = 0
    neurons_file = 0
    
    print("Making neuron indexes...")
    counter = 0
    for i in range(0, 86):
        neuron_layers[0].append(counter)
        counter += 1
    for i in range(0, 2000):
        if i < 1000:
            neuron_layers[1].append(counter)
        else:
            neuron_layers[2].append(counter)
        counter += 1
    for i in range(0, 3):
        neuron_layers[3].append(counter)
        counter += 1
        
    if exists("neurons.txt") == False:
        first_time = True
    
    if first_time:
        print("Creating neurons and weights...")
        for i in range(0, 2090): # Load neurons and weight lists
            neurons.append(0.1)
            weights.append([])
        for i in range(0, 2090):
            for j in range(0, 2090):
                weights[i].append((random.randint(0, 99)/100)) # Fill weight lists
    else:
        print("Loading neurons and weights")
        neurons_file = str(open("neurons.txt", "r").read())
        weights_file = str(open("weights.txt", "r").read())
        neurons = load_neurons(neurons_file)
        weights = load_weights(weights_file, weights)

    def get_neuron_layer(neuron):
        for i in range(0, len(neuron_layers)):
            if neuron in neuron_layers[i]:
                return i
            
    def is_connected(self, neuron1, neuron2):
            if get_neuron_layer(neuron1) == get_neuron_layer(neuron2):
                return False
            if get_neuron_layer(neuron1) > get_neuron_layer(neuron2): # If it's ahead, then it needs to know if the other one is right behind it
                if neuron2 in self.neuron_layers[get_neuron_layer(neuron1)-1]:
                    return True
            if get_neuron_layer(neuron1) < get_neuron_layer(neuron2): # If it's beind, then the other one needs to check if it's right in front of it
                if neuron1 in self.neuron_layers[get_neuron_layer(neuron2)-1]:
                    return True

    print("\n\nMatrix of size " + str(len(weights)))

    for i in range(0, int(iterations)):
        data = open("late_days.txt", "r").readlines()
        for line in data:
            late_day = str(line).split(";")
            name = late_day[0]
            grade = late_day[1]
            date = late_day[2]
            minutes = late_day[3]
            index = late_day[4]
            print(late_day)
            print("name = " + name)
            print("grade = " + grade)
            print("date = " + date)
            print("minutes = " + minutes)
            print("index = " + index)

            grade_data = sigmoid(int(grade))
            day_data = sigmoid(int(date.split("/")[0]))
            month_data = sigmoid(int(date.split("/")[1]))
            year_data = sigmoid(int(date.split("/")[2]))
            minutes_data = sigmoid(int(minutes))
            index_data = sigmoid(int(index))

            name_counter = 0
            for i in range(0, 80):
                neurons[i] = sigmoid(ord(name[name_counter]))
                name_counter += 1
                if name_counter == len(name):
                    name_counter = 0

            neurons[80] = grade_data
            neurons[81] = day_data
            neurons[82] = month_data
            neurons[83] = year_data
            neurons[84] = index_data

            for layer in range(1, len(neuron_layers)): # feed forward
                print("layer: " + str(layer))
                for neuron_index in neuron_layers[layer]:
                    neuron_value = 0
                    for neuron_index_2 in range(0, len(neuron_layers[layer-1])):
                        neuron_value += neurons[neuron_index_2] * weights[neuron_index][neuron_index_2]
                    neurons[neuron_index] = sigmoid(neuron_value)

            neural_output = [neurons[-2], neurons[-3], neurons[-4]] # last neuron is niggrlicious anyways
            real_output = [day_data, month_data, minutes_data]

            # Calculate error for each output
            errors = [((neural_output[i] - sigmoid(real_output[i])) ** 2) / 2 for i in range(3)]
            print("Errors:", errors)

            learning_rate = 0.0001

            # Update weights
            for i in range(len(weights)):
                for j in range(len(weights[i])):
                    if weights[i][j] == 0:
                        weights[i][j] = 0.1
        
            # Calculate weight update for each output separately
            for k in range(3):
                weights[i][j] -= learning_rate * (errors[k] / weights[i][j])

            print(len(weights))
            print(len(weights[0]))
            try:
                save_state(weights, neurons)
            except Exception as e:
                print("idiot error: " + str(e))
            print("saved")


    return render_template('index.html', output=output)

@app.route('/predict_days', methods=['POST'])
def predict_days():
    name = unidecode(request.form['student_name']).lower()
    grade = request.form['grade']

    neuron_layers = [[], [], [], []]
    neurons_ever = 0

    weights = []
    neurons = []

    weights_file = 0
    neurons_file = 0
    
    print("Making neuron indexes...")
    counter = 0
    for i in range(0, 86):
        neuron_layers[0].append(counter)
        counter += 1
    for i in range(0, 2000):
        if i < 1000:
            neuron_layers[1].append(counter)
        else:
            neuron_layers[2].append(counter)
        counter += 1
    for i in range(0, 3):
        neuron_layers[3].append(counter)
        counter += 1

    neurons_file = str(open("neurons.txt", "r").read())
    weights_file = str(open("weights.txt", "r").read())
    print("loading neurons")
    neurons = load_neurons(neurons_file)
    print("loading weights")
    weights = load_weights(weights_file, weights)
    predictions = []

    # load school days
    days = []
    day = 19
    month = 2
    while(day != 22 or month != 7):
        days.append([day, month])
        day += 1
        if(day == 32):
            day = 1
            month += 1
    day = 3
    month = 8
    while(day != 21 or month != 12):
        days.append([day, month])
        day += 1
        if(day == 32):
            day = 1
            month += 1
    
    counter = 1
    for day in days:
        grade_data = sigmoid(int(grade))
        day_data = sigmoid(int(day[0]))
        month_data = sigmoid(int(day[1]))
        year_data = sigmoid(2024)
        index_data = sigmoid(int(counter))
        counter += 1

        # feed forward

        name_counter = 0
        for i in range(0, 80):
            neurons[i] = sigmoid(ord(name[name_counter]))
            name_counter += 1
            if name_counter == len(name):
                name_counter = 0

        neurons[80] = grade_data
        neurons[81] = day_data
        neurons[82] = month_data
        neurons[83] = year_data
        neurons[84] = index_data

        for layer in range(1, len(neuron_layers)): # feed forward
            for neuron_index in neuron_layers[layer]:
                neuron_value = 0
                for neuron_index_2 in range(0, len(neuron_layers[layer-1])):
                    neuron_value += neurons[neuron_index_2] * weights[neuron_index][neuron_index_2]
                neurons[neuron_index] = sigmoid(neuron_value)

        neural_output = [neurons[-2], neurons[-3], neurons[-4]] # last neuron is niggrlicious anyways
        predictions.append(neural_output)
        print(neural_output)
    print("Final results: " + str(predictions))
    output = ""
    print("Generating output: ")
    # treating predictions first

    for i in range(0, len(predictions)):
        prediction = predictions[i]
        day_ = float("0." + str(prediction[0])[13] + str(prediction[0])[14])
        month_ = float("0." + str(prediction[1])[13] + str(prediction[1])[14])
        minutes_ = float("0." + str(prediction[2])[13] + str(prediction[2])[14])
        predictions[i][0] = day_
        predictions[i][1] = month_
        predictions[i][2] = minutes_
        print("fixed prediction: " + str(predictions[i]))

    for prediction in predictions:
        if int(sigmoid(prediction[2])*60) == 0 or int(sigmoid(prediction[0])*31) == 0 or int(sigmoid(prediction[1])*12) == 0:
            continue
        output += name + " se atrasou " + str(int(sigmoid(prediction[2])*60)) + " minutos " + "no dia " + str(int(sigmoid(prediction[0])*31)) + "/" + str(int(sigmoid(prediction[1])*12)) + "<br>"
    return render_template('index.html', output=output)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
