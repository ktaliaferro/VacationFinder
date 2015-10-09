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
  #pull 'ID' from input field and store it
  interests = request.args.get('ID')
  use_dummy = False
  if interests == 'cached_results':
    use_dummy = True
    interests = 'golf, hiking, horseback, skiing, gardening, karate, basketball, cooking, zoo, chess, boats, soccer, coffee, frisbee, shopping, football, baseball, surfing, volunteering, kayaking, museums, biking, scuba, swimming'
  start = time.time()
  if use_dummy:
    rankings = get_rankings_dummy.get_rankings(interests)
  else:
    rankings = get_rankings.get_rankings(interests)
  end = time.time()
  print 'runtime', end-start, 'seconds'
  length = len(rankings)
  return render_template("output.html", rankings = rankings, interests=interests, length=length, runtime=end-start)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
