# Diabetes application. Tracks sugar levels and food intake. Can also search foods to check nutritional values
import requests
import json


class DiabDaily(object):

    # init method uses the Nutritionix API to search for the user inputted food
    def __init__(self, app_id, app_key, food_input):
        item_id = ""
        url = "https://trackapi.nutritionix.com/v2/search/instant?query=%s" % food_input
        headers = {"x-app-id": app_id, "x-app-key": app_key, "x-remote-user-id": "0"}  # 0 for Development

        food_input_request = requests.get(url, headers=headers)
        food_input_request.raise_for_status()
        search_food_input_request = json.loads(food_input_request.text)
        food_input_request.close()

        for k1, v1 in search_food_input_request.items():
            if k1 == "branded":
                for k2, v2 in v1[0].items():
                    if k2 == "nix_item_id":
                        item_id += v2

        item_url = "https://trackapi.nutritionix.com/v2/search/item?nix_item_id=%s" % item_id
        item_info_request = requests.get(item_url, headers=headers)
        item_info_request.raise_for_status()
        self.query_nutrients = json.loads(item_info_request.text)
        item_info_request.close()

    # This method will use the food id from init method to return the nutritional values
    def get_nutrients(self):
        print_list = []
        for k3, v3 in self.query_nutrients.items():
            print_list.append("Similar Brand: "+v3[0]['brand_name'])
            print_list.append("Serving Size: "+str(v3[0]['serving_qty'])+" "+str(v3[0]['serving_unit']))
            print_list.append("Calories: "+str(v3[0]['nf_calories']))
            print_list.append("Sugars: "+str(v3[0]['nf_sugars'])+"g")
            print_list.append("Carbohydrates: "+str(v3[0]['nf_total_carbohydrate']))
            print_list.append("Protein: "+str(v3[0]['nf_protein'])+"g")
        return print_list

