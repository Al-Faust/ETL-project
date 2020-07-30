from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import item_id_scrape

# Create an instance of Flask
app = Flask(__name__)

# Use PyMongo to establish Mongo connection
#mongo = PyMongo(app, uri="mongodb://localhost:27017/weather_app")


# Route to render index.html template using data from Mongo
@app.route("/")
def test_override():

    # Find one record of data from the mongo database
    item_id = item_id_scrape.scrape_ids()

    # Return template and data
    return render_template("index.html", item_id=item_id)


if __name__ == "__main__":
    app.run(debug=True)

