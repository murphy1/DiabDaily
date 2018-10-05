# Diabetes application. Tracks sugar levels and food intake. Can also search foods to check nutritional values
import requests
import json
import firebase_admin
import matplotlib.pyplot as plt
from firebase_admin import db
from firebase_admin import credentials
from datetime import datetime

# Database information (Firebase)
path_to_db = "/"
db_url = ""


class DiabDaily(object):

    # init method initializes the Nutritionix API
    def __init__(self, app_id, app_key):
        self.headers = {"x-app-id": app_id, "x-app-key": app_key, "x-remote-user-id": "0"}  # 0 for Development

        cred = credentials.Certificate(path_to_db)
        firebase_admin.initialize_app(cred, {'databaseURL': db_url})
        self.root = db.reference()

    def nutritionix(self, food_input):
        item_id = ""
        url = "https://trackapi.nutritionix.com/v2/search/instant?query=%s" % food_input

        food_input_request = requests.get(url, headers=self.headers)
        food_input_request.raise_for_status()
        search_food_input_request = json.loads(food_input_request.text)
        food_input_request.close()

        for k1, v1 in search_food_input_request.items():
            if k1 == "branded":
                for k2, v2 in v1[0].items():
                    if k2 == "nix_item_id":
                        item_id += v2

        item_url = "https://trackapi.nutritionix.com/v2/search/item?nix_item_id=%s" % item_id
        item_info_request = requests.get(item_url, headers=self.headers)
        item_info_request.raise_for_status()
        query_nutrients = json.loads(item_info_request.text)
        item_info_request.close()
        return query_nutrients

    # This method will use the food id from init method to return the nutritional values
    def get_nutrients(self, food_input):
        query_nutrients = DiabDaily.nutritionix(self, food_input=food_input)
        print_list = []
        for k3, v3 in query_nutrients.items():
            print_list.append("Similar Brand: "+v3[0]['brand_name'])
            print_list.append("Serving Size: "+str(v3[0]['serving_qty'])+" "+str(v3[0]['serving_unit']))
            print_list.append("Calories: "+str(v3[0]['nf_calories']))
            print_list.append("Sugars: "+str(v3[0]['nf_sugars'])+"g")
            print_list.append("Carbohydrates: "+str(v3[0]['nf_total_carbohydrate']))
            print_list.append("Protein: "+str(v3[0]['nf_protein'])+"g")
        return print_list


    # Sugar Log


    # this method allows the user to enter their blood sugar levels
    def enter_sugar(self, reading, name):
        # will add a new attribute to the db
        push_sugar = self.root.child("%s's Sugar Levels" % name).push({
            'level': '%s' % reading,  #mmol/L
            'name': '%s' % name,
            'date': str(datetime.now())
        })
        print("%s's reading added!" % name)

    # this method allows the user to read their levels from the database
    def read_sugar_all_readings(self, name):
        result_list = list()
        ref = db.reference("%s's Sugar Levels" % name)
        for keys, values in ref.get().items():
            result_list.append('Date: '+values['date']+' - Reading: '+values['level']+'mmol/L')
        print(result_list)

    # This method will allow the user to read their sugar readings by inputted date
    def read_sugar_by_date(self, name, date):
        result_list = list()
        ref = db.reference("%s's Sugar Levels" % name)
        for keys, values in ref.get().items():
            if date == str(values['date']).split(" ")[0]:
                result_list.append("Date: "+str(values['date']).split(" ")[0]+" - Reading: "+values['level']+"mmol/L")
        print(result_list)


    # Medication Log


    # user enters their medication here along with the dosage per day
    def enter_medication(self, user_name, med_name, dosage):
        push_medication = self.root.child("%s's Medication" % user_name).push({
            'dosage': '%d' % dosage,
            'medication': '%s' % med_name,
            'name': '%s' % user_name,
            'date entered': str(datetime.now())
        })
        print("%s's medication added!" % user_name)

    # users can read their medication and dosages
    def read_medication(self, name):
        result_list = list()
        ref = db.reference("%s's Medication" % name)
        for keys, values in ref.get().items():
            result_list.append('Medication: '+values['medication']+' - Dosage: '+values['dosage']+' times daily')
        print(result_list)


    # Graphing with Matplotlib


    # set up the y-axis numbers for plotting
    def y_axis_sugar_levels(self):
        plot_numbers_for_levels = []
        for i in range(0, 10):
            plot_numbers_for_levels.append(float(i))
        return plot_numbers_for_levels

    # method to get the values from the database to be plotted (for sugar levels)
    def sugar_plot_setup(self, name):
        date_list = list()
        time_list = list()
        level_list = list()
        daily_list = list()
        ref = db.reference("%s's Sugar Levels" % name)
        for keys, values in ref.get().items():
            # get the date, time and the value
            date_list.append((values['date']).split(" ")[0])
            time_list.append(((values['date']).split(" ")[1])[0:5])
            level_list.append(float(values['level']))
            daily_list.append((values['date']).split(" ")[0]+' '+values['level'])

        return date_list, time_list, level_list, daily_list

    # this method will plot sugar levels with the information from the above 'sugar_plot_setup'
    def sugar_plot(self, name, type):
        proceed = False
        if type == "hourly":
            plt.plot(DiabDaily.sugar_plot_setup(self, name)[1], DiabDaily.sugar_plot_setup(self, name)[2], 'ro')
            proceed = True
        # the user can enter a day to see their average sugar reading
        elif type == "daily":
            average = 0
            num_of_records = 0
            date = input("Please enter a date:")
            for record in DiabDaily.sugar_plot_setup(self, name)[3]:
                if date == record.split(" ")[0]:
                    average += float(record.split(" ")[1])
                    num_of_records += 1
            average = str(round(average / num_of_records, 2))
            plt.plot(date, float(average), 'ro')
            proceed = True
        else:
            print("Please enter a type!")
        if proceed is True:
            plt.title("%s's Sugar Levels" % name)
            plt.xlabel("Time")
            plt.ylabel("mmol/L")
            plt.yticks(DiabDaily.y_axis_sugar_levels(self))
            plt.grid(True)
            plt.show()
