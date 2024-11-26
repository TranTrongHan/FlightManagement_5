from flask import Flask
from urllib.parse import quote
from flask_sqlalchemy import SQLAlchemy
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/flight_db?charset=utf8mb4" % quote('Admin@123')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True


# Configuration
cloudinary.config(
    cloud_name = "dfi68mgij",
    api_key = "894594157357848",
    api_secret = "<your_api_secret>", # Click 'View API Keys' above to copy your API secret
    secure=True
)



db = SQLAlchemy(app=app)
