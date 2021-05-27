from app import db
from app.models import *
from app.Bills import Bills

Bills.load_bills_into_mysql(last_mod_flag=False)
