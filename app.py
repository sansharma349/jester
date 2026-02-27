import requests
from flask import Flask, render_template
#Import from SQLAlchemy
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)

#Configure the SQLite database file location
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jokes.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Initialize the SQLAlchemy object with the Flask app
db = SQLAlchemy(app)

#Create your Database Model (This creates a 'joke' table)
class JokeDb(db.Model):
    # SQLAlchemy uses capitalized Column and type names
    id = db.Column(db.Integer, primary_key=True)  # auto‑incrementing primary key
    setup = db.Column(db.String(300), nullable=False)  # joke setup text
    punchline = db.Column(db.String(300), nullable=False)  # joke punchline text

# Tell Python to actually create the file and tables before the first request
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return "<h1>Welcome to the Terminal Jester Web Server!</h1><p><a href='/joke'>Click to see a new joke</a></p>"

@app.route("/joke")
def get_joke():
    # 1. Define the URL
    joke_url = "https://official-joke-api.appspot.com/random_joke"
    
    try:
        # 2. Fixed the typos (= and requests)
        response = requests.get(joke_url)
        response.raise_for_status()
        joke_data = response.json()

        # ==========================================
        # NEW DATABASE LOGIC:
        # 1. Create a new Joke object using the data from the API
        new_joke = JokeDb(setup=joke_data['setup'], punchline=joke_data['punchline'])
        
        # 2. Add it to the database's waiting room (session)
        db.session.add(new_joke)
        
        # 3. Commit the changes to permanently save it to jokes.db!
        db.session.commit()
        # ==========================================


        # Added an HTML <br> tag so the punchline appears on a new line in the browser!
        return render_template("joke.html", setup=joke_data['setup'], punchline=joke_data['punchline'])
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching joke: {e}")
        # 3. Return a string instead of None
        return "Sorry, the joke machine is currently down."


@app.route("/history")
def history():
    # 1. Fetch ALL jokes from the database as a list of Python objects
    saved_jokes = JokeDb.query.all()
    
    # 2. Render a new template, passing the list of jokes into it
    return render_template("history.html", all_jokes=saved_jokes)

if __name__ == "__main__":
    # Back to the clean, standard local server setup!
    app.run(debug=True)