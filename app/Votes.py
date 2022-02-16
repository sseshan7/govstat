import os
import json
from datetime import datetime

import app
from app import db
from app.models import Vote, Bill, BillType, Representative

VOTES_PATH = os.path.join(app.CONGRESS_PATH, "data")
LATEST_SESSION = sorted([x for x in os.listdir(VOTES_PATH) if x.isdigit()])[-1]
VOTES_PATH = os.path.join(VOTES_PATH, LATEST_SESSION, "votes")
LATEST_YEAR = sorted([x for x in os.listdir(VOTES_PATH) if x.isdigit()])[-1]
VOTES_PATH = os.path.join(VOTES_PATH, LATEST_YEAR)
JSON_FILE = 'data.json'


class Votes:
    vote_types = ['s', 'h']
    dv = {}
    dv['s'] = 'Senate'
    dv['h'] = 'House of Representatives'


    @classmethod
    def load_votes_into_mysql(cls):
        """Read all json data saved, and push it into mysql db"""
        for dir_name in os.listdir(VOTES_PATH):
            with open(os.path.join(VOTES_PATH, dir_name, JSON_FILE), 'r') as f:
                data = json.load(f)

            c = data['chamber']
            n = data['number']

            entries = Vote.query.filter(Vote.vote_num == n).filter(Vote.chamber == c).all()
            if entries:
                # If vote already exists in the database, skip adding it
                continue

            q = data['question']
            d = data['date']
            r = data['result']
            req = data['requires']
            t = data['type']
            try:
                nays = data['votes']['Nay']
            except KeyError:
                try:
                    nays = data['votes']['No']
                except KeyError:
                    nays = []
            try:
                yeas = data['votes']['Yea']
            except KeyError:
                try:
                    yeas = data['votes']['Aye']
                except KeyError:
                    yeas = []
            try:
                abstains = data['votes']['Not Voting']
            except KeyError:
                abstains = []

            d = d[:19] # strip off the timezone offset
            dt = datetime.strptime(d, '%Y-%m-%dT%H:%M:%S').date()

            num_nays = len(nays)
            num_yeas = len(yeas)
            num_abstains = len(abstains)

            v = Vote(chamber=c,
                     vote_num=n,
                     date=dt,
                     vote_result=r if len(r) <= 64 else r[:64],
                     num_yeas=num_yeas,
                     num_nays=num_nays,
                     num_abstains=num_abstains,
                     required=req,
                     vote_type=t if len(t) <= 32 else t[:32],
                     question=q if len(q) <= 512 else q[:512])

            for rep_data in yeas:
                # iterate over yea representatives.
                # link the appropriate rep with this yea vote.
                # create the rep if bioguide not in the database
                if c == 'h':
                    rep_q = Representative.query.filter(Representative.bioguide_id == rep_data['id'])
                else:
                    try:
                        rep_q = Representative.query.filter(Representative.lis_id == rep_data['id'])
                    except TypeError:
                        print("{}{}".format(c, n))
                        print(rep_data)
                        continue
                reps = rep_q.all()
                if reps:
                    # the rep exists in the database
                    # link that rep with this yea vote
                    r = reps[0]
                else:
                    # the rep doesn't exist
                    # create the rep and then link
                    if c == 'h':
                        r = Representative(bioguide_id=rep_data['id'])
                    else:
                        r = Representative(lis_id=rep_data['id'])
                        r.fname = rep_data['first_name'].title()
                        r.lname = rep_data['last_name'].title()
                    r.state = rep_data['state']
                    r.party = rep_data['party']
                    r.active = True
                    r.chamber = c
                v.yea_voters.append(r)

            for rep_data in nays:
                # iterate over nay representatives.
                # link the appropriate rep with this nay vote.
                # create the rep if bioguide not in the database
                if c == 'h':
                    rep_q = Representative.query.filter(Representative.bioguide_id == rep_data['id'])
                else:
                    rep_q = Representative.query.filter(Representative.lis_id == rep_data['id'])
                reps = rep_q.all()
                if reps:
                    # the rep exists in the database
                    # link that rep with this yea vote
                    r = reps[0]
                else:
                    # the rep doesn't exist
                    # create the rep and then link
                    if c == 'h':
                        r = Representative(bioguide_id=rep_data['id'])
                    else:
                        r = Representative(lis_id=rep_data['id'])
                        r.fname = rep_data['first_name'].title()
                        r.lname = rep_data['last_name'].title()
                    r.state = rep_data['state']
                    r.party = rep_data['party']
                    r.active = True
                    r.chamber = c
                v.nay_voters.append(r)

            for rep_data in abstains:
                # iterate over not voting representatives.
                # link the appropriate rep with this not vote.
                # create the rep if bioguide not in the database
                if c == 'h':
                    rep_q = Representative.query.filter(Representative.bioguide_id == rep_data['id'])
                else:
                    rep_q = Representative.query.filter(Representative.lis_id == rep_data['id'])
                reps = rep_q.all()
                if reps:
                    # the rep exists in the database
                    # link that rep with this yea vote
                    r = reps[0]
                else:
                    # the rep doesn't exist
                    # create the rep and then link
                    if c == 'h':
                        r = Representative(bioguide_id=rep_data['id'])
                    else:
                        r = Representative(lis_id=rep_data['id'])
                        r.fname = rep_data['first_name'].title()
                        r.lname = rep_data['last_name'].title()
                    r.state = rep_data['state']
                    r.party = rep_data['party']
                    r.active = True
                    r.chamber = c
                v.not_voters.append(r)

            try:
                bill = data['bill']
                bill_q = Bill.query \
                    .filter(Bill.bill_type == getattr(BillType, bill['type'].upper())) \
                    .filter(Bill.bill_num == bill['number']) \
                    .filter(Bill.congress == bill['congress'])
                bills = bill_q.all()
                if len(bills) == 1:
                    # if bill being voted on exists in the database (TYPE, NUM, CONGRESS),
                    # then link the bill to this vote
                    v.bill = bills[0]
                elif not bills:
                    # if there is no matching bill in database (TYPE, NUM, CONGRESS),
                    # then create the bill, and link to this vote
                    ad_hoc_bill = Bill(
                        congress=bill['congress'],
                        bill_type=getattr(BillType, bill['type'].upper()),
                        bill_num=bill['number'],
                    )
                    v.bill = ad_hoc_bill
            except KeyError:
                # The vote is not related to any bill
                pass

            db.session.add(v)
            db.session.commit()


    @classmethod
    def return_sql_json_by_date(cls, date):
        current_date = date.date()
        date_to_query = current_date
        d = {}

        ordered_dates = db.session.query(
            Vote.vote_num,
            Vote.question,
            Vote.vote_result,
            Vote.num_yeas,
            Vote.num_nays,
            Vote.num_abstains,
            Vote.date,
        ).order_by(Vote.date.desc())

        senate_ordered = ordered_dates.filter(Vote.chamber == 's')
        senate_max_date = senate_ordered.first()[-1].date()
        house_ordered = ordered_dates.filter(Vote.chamber == 'h')
        house_max_date = house_ordered.first()[-1].date()

        if current_date > senate_max_date:
            date_to_query = senate_max_date
        d['s'] = senate_ordered.filter(Vote.date >= date_to_query).all()

        if current_date > house_max_date:
            date_to_query = house_max_date
        d['h'] = house_ordered.filter(Vote.date >= date_to_query).all()

        return d
