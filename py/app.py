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
    itemID = item_id_scrape.scrape()
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    Gen = Base.classes.general_info
    VoT = Base.classes.price_over_time
    """Return a list of passenger data including the name, age, and sex of each passenger"""
    # Query all passengers
    Gen_results = session.query(Gen.name, Gen.current_price).all()
    VoT_results = session.query(VoT.Date, VoT.price).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    gen_data = []
    VoT_data = []
    gen_dict = {}
    gen_dict["name"] = Gen_results.name
    gen_dict["current price"] = Gen_results.current_price
    gen_data.append(gen_dict)

    for Date, price in VoT_results:
        VoT_dict = {}
        VoT_dict["Date"] = Date
        VoT_dict["price"] = price
        VoT_data.append(VoT_dict)

    return jsonify(VoT_data, gen_data)


if __name__ == "__main__":
    app.run(debug=True)



    