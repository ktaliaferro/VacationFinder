"""This is the 'main' part of my app.  Flask uses it generate the
HTML on my website."""

# packages
from flask import render_template, request
from flask import Flask
import time

# files in this directory
import get_rankings
import get_rankings_dummy

app = Flask(__name__)

@app.route('/')
@app.route('/index')    
@app.route('/input')
def cities_input():
    return render_template("input.html")

@app.route('/output')
def cities_output():
    interests = request.args.get('ID') # pull interests from the input page
    start = time.time()
    # If the user inputs the string 'cached_results', then the app will return 
    # cached results for boats, surfing, kayaking, and swimming.  This is for 
    # testing and demonstration purposes only.
    if interests == 'cached_results':
        interests = 'boats, surfing, kayaking, swimming'
        rankings = get_rankings_dummy.get_rankings_dummy()
    else:
        rankings = get_rankings.get_rankings(interests)
    end = time.time()
    print 'runtime', end-start, 'seconds'
    length = min(20,len(rankings))
    return render_template("output.html", rankings = rankings, interests=interests, length=length, runtime=end-start)
  
@app.route('/slides')
def slides():
    return render_template("slides.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
