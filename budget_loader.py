from app import db
from app.models import *
import app.Budget as Budget

Budget.load_mysql_all_budget()
