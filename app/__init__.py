from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import config


app = Flask(__name__)
app.config.from_object(config.DefaultConfig)
success = app.config.from_json("cfg/config.json", silent=True)
if not success:
    raise RuntimeError("no config.json file in app/cfg/ directory")
db = SQLAlchemy(app)
migrate = Migrate(app, db, compare_type=True)

from app import routes, models
