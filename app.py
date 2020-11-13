from flask import render_template
from flask import Flask
from flask import request, jsonify, redirect, url_for
import populartimes as places
import requests

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
def find_places(keyword):
    params = {"input":keyword, 
            "inputtype":"textquery", 
            "fields":"formatted_address,name,rating,opening_hours,place_id,types,business_status",
            "key":google_api_key}
    data = requests.get(url=google_places_endpoint, params=params) 
    return data.json()

# nearby places, more sophisticated, requirres location information
def find_places_advanced(keyword, latitude, longitude, radius=1000):
    params = {"keyword":keyword, 
            "location": [latitude, longitude], 
            "radius":radius,
            "key":google_api_key}
    print(params)
    data = requests.get(url=google_places_endpoint, params=params) 
    return data.json()

# home page
@app.route('/')
def splash():
    print(format(request.remote_addr))
    location_data = get_user_location()
    print(location_data)
    print()
    print(find_places('bar'))
    print()
    print(find_places_advanced('park', location_data["latitude"], location_data["longitude"]))
    return render_template('splash.html')






# POST route for search bar
@app.route('/go', methods = ['POST', 'GET'])
def go():
    if request.method == 'POST':
        print(request.form['query'])
        return redirect((url_for('results', query=request.form['query'])))
    return render_template('splash.html')






# presenting the ranking / results / sauce
@app.route('/results/')
@app.route('/results/<query>')
def results(query=None):
    # the query will be sauced and handled here
    # the ranking thing will prolly be used here
    # need to pass multiple params to template
    # make a template with if statement
    return render_template('results.html', query=query)