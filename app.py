from flask import render_template
from flask import Flask
from flask import request, jsonify, redirect, url_for
import populartimes as places

app = Flask(__name__)

@app.route('/')
def splash():
    return render_template('splash.html')

@app.route('/go', methods = ['POST', 'GET'])
def go():
    if request.method == 'POST':
        print(request.form['query'])
        return redirect((url_for('results', query=request.form['query'])))
    return render_template('splash.html')

@app.route('/results/')
@app.route('/results/<query>')
def results(query=None):
    # the query will be sauced and handled here
    # make a template with if statement
    return render_template('results.html', query=query)