from app import db
from app.models import *
from app.Votes import Votes

Votes.load_votes_into_mysql()
