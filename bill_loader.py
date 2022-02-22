from app import db
from app.Bills import Bills
from app.models import *

Bills.load_bills_into_mysql(last_mod_flag=False)
