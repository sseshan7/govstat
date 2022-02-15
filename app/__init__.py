from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from . import config


app = Flask(__name__)
app.config.from_object(config.DefaultConfig)
success = app.config.from_json("cfg/config.json", silent=True)
if not success:
    raise RuntimeError("no config.json file in app/cfg/ directory")
db = SQLAlchemy(app)
migrate = Migrate(app, db, compare_type=True)
CONGRESS_PATH = app.config.get("CONGRESS_PATH")
if CONGRESS_PATH is None:
    raise RuntimeError("CONGRESS_PATH not set in cfg/config.json")
GOVSTAT_PATH = app.config.get("GOVSTAT_PATH")
if GOVSTAT_PATH is None:
    raise RuntimeError("GOVSTAT_PATH not set in cfg/config.json")

from app import routes, models
