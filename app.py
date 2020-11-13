from flask import render_template
from flask import Flask
from flask import request, jsonify, redirect, url_for
import populartimes
import requests
import datetime
import math
from random import random

default_ip = '40.78.55.113' # some san jose microsoft ip lol

google_api_key = 'AIzaSyD7vPDsCi7bnYdbiFGRD5FDq8nor5EB4D0'
google_places_endpoint = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
google_places_advanced_endpoint = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

ipstack_api_key = 'b2cfd213fc3f26ea12b0f109bcb9d956'
ipstack_endpoint = "http://api.ipstack.com/"

app = Flask(__name__)

# get clean location information
def get_user_location(user_ip_addr=default_ip):
    data = requests.get(ipstack_endpoint+user_ip_addr+"?access_key="+ipstack_api_key)
    cleaned = {"latitude":data.json()["latitude"], 
                "longitude":data.json()["longitude"], 
                "city":data.json()["city"], 
                "zip":data.json()["zip"], 
                "region_name":data.json()["region_name"]}
    return cleaned

# basic find places by keywords
def find_places_basic(keyword):
    params = {"input":keyword, 
            "inputtype":"textquery", 
            "fields":"formatted_address,name,rating,opening_hours,place_id,types,business_status",
            "key":google_api_key}
    data = requests.get(url=google_places_endpoint, params=params) 
    return data.json()

# nearby places, more sophisticated, requirres location information
def find_places_advanced(keyword, latitude, longitude, radius=1000):
    url = google_places_advanced_endpoint
    url += "?location="+str(latitude)+", "+str(longitude)+"&radius="+str(radius)+"&keyword="+keyword+"&key="+google_api_key
    data = requests.get(url=url) 
    return data.json()

# home page
@app.route('/')
def splash():
    # location_data = get_user_location() # THIS IS NO PARAM BY DEFAULT (testing purposes)
    # print(location_data)
    # print()
    # print(find_places_basic('bar'))
    # print()
    # print(find_places_advanced('park', location_data["latitude"], location_data["longitude"]))
    return render_template('splash.html')






# POST route for search bar
@app.route('/go', methods = ['POST', 'GET'])
def go():
    if request.method == 'POST':
        print(request.form['query'])
        return redirect((url_for('results', query=request.form['query'])))
    return render_template('splash.html')


def clean_candidates(candidates):
    clean_candidates = []
    for candidate in candidates:
        popularity_data = populartimes.get_id(google_api_key, candidate["place_id"])
        # print(popularity_data)
        # candidate is a JSON element
        clean_candidate = {"name": candidate["name"], 
                            "types": candidate["types"], 
                            "business_status": candidate["business_status"],
                            "address": popularity_data["address"],
                          }

        if "populartimes" in popularity_data:
            clean_candidate["populartimes"] = popularity_data["populartimes"]
        if "current_popularity" in popularity_data:
            clean_candidate["current_popularity"] = popularity_data["current_popularity"]
        if "time_spent" in popularity_data:
            clean_candidate["time_spent"] = popularity_data["time_spent"]
        if "rating_n" in popularity_data:
            clean_candidate["rating_n"] = popularity_data["rating_n"]
        if "rating" in popularity_data:
            clean_candidate["rating"] = popularity_data["rating"]

        clean_candidates.append(clean_candidate)

    return clean_candidates


# presenting the ranking / results / sauce
@app.route('/results/')
@app.route('/results/<query>')
def results(query=None, advanced=True):
    if query is not None:
        # query = ... ?
        location_data = get_user_location() # random SJ warehouse lol, in real pass request.remote_addr
        if advanced:
            candidates = find_places_advanced(query, location_data["latitude"], location_data["longitude"])["results"]
        else:
            candidates = find_places_basic(query)["candidates"]
        
        if len(cleaned_data) < 1:
            candidates = find_places_basic(query)["candidates"]
            
        cleaned_data = clean_candidates(candidates)
        
        hour = datetime.datetime.now().hour
        day_num = datetime.datetime.now().weekday()
        scores = []

        noise = []
        
        for c in cleaned_data:
            if 'current_popularity' in c and 'populartimes' in c:
                exp_score = math.e ** (- c['populartimes'][day_num]['data'][hour] / c['current_popularity'])
                c['exp_score'] = round(exp_score, 3)
            else:
                exp_score = 0
                c['exp_score'] = exp_score

            if 'rating' in c:
                r = c['rating']
            else:
                r = 3.6
                c['rating'] = r
            
            if 'rating_n' in c:
                n_score = math.atan(c['rating_n']/3)/3
                c['n_score'] = round(n_score, 3)
            else:
                n_score = 0
                c['n_score'] = 0
            
            if 'time_wait' in c:
                waiting_score = c['time_wait'][day_num]['data'][hour]
                c['waiting_score'] = round(waiting_score, 3)
            else:
                waiting_score = 0
                c['waiting_score'] = 0

            composite_score = exp_score + r + n_score - waiting_score
            c['comp_score'] = round(composite_score, 3)

            scores.append(composite_score)
            noise = [random() for _ in range(len(scores))]

        cleaned_data = [x for _, __, x in sorted(zip(scores, noise, cleaned_data), reverse=True)]

        return render_template('results.html', results=cleaned_data, og_query=query, best=cleaned_data[0]['name'], best_addy=cleaned_data[0]['address'])

    return render_template('splash.html')