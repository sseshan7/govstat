import os
import json
import requests
import datetime
from flask import render_template, jsonify, request

from app import CONGRESS_PATH
from app.Votes import Votes
from app.Bills import Bills
import app.Budget as Budget
from app import app

# globals
BILLS_PATH = os.path.join(CONGRESS_PATH, 'data', '116', 'bills')
JSON_NAME = 'data.json'

# BILLS SCRAPER
d = {}
bill_types = ['hconres', 'hjres', 'hr', 'hres', 's', 'sres', 'sconres', 'sjres']
d['hconres'] = 'House Concurrent Resolution'
d['hjres'] = 'House Joint Resolution'
d['hr'] = 'House of Representatives'
d['hres'] = 'House Simple Resolution'
d['s'] = 'Senate'
d['sres'] = 'Senate Simple Resolution'
d['sconres'] = 'Senate Concurrent Resolution'
d['sjres'] = 'Senate Joint Resolution'


@app.route('/budget_data')
def transmit_data():
    if request.args['id'] == '1':
        return jsonify(Budget.read_mysql_deficit_surplus())
    elif request.args['id'] == '2':
        return jsonify(Budget.read_mysql_receipt_breakdown())
    elif request.args['id'] == '3':
        return jsonify(Budget.read_mysql_outlay_breakdown())


@app.route('/budget')
def budget():
    return render_template('data.html')

@app.route('/')
@app.route('/index')
def index():
    latest_votes = Votes.return_sql_json_by_date(datetime.datetime.now() - datetime.timedelta(4, 0, 0))
    latest_bills = Bills.return_sql_json_by_date(datetime.datetime.now() - datetime.timedelta(4, 0, 0))

    return render_template('index_votes.html', vote_types=Votes.vote_types, dv=Votes.dv,
        latest_votes=latest_votes, bill_types=bill_types, d=d,
        latest_bills=latest_bills)
