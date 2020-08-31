from flask import Flask, render_template, redirect, jsonify
from flask_pymongo import PyMongo
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import item_id_scrape

# Create an instance of Flask
app = Flask(__name__)

#connect postgres server
connection_string = 'postgres:nwyfre@localhost:5432/osrs_ge_tracker_db'
engine = create_engine(f'postgresql://{connection_string}')
Base = automap_base()
Base.prepare(engine, reflect=True)



# Route to render index.html template using data from Mongo
@app.route("/")
def test():
    # Return template and data
    
    return render_template("index.html")


@app.route("/scrape")
def scraper():
    #run scrape script
    item_gen = item_id_scrape.scrape1()
    item_daily = item_id_scrape.scrape2()


    return item_gen


if __name__ == "__main__":
    app.run(debug=True)



    