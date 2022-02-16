import os
import json
from datetime import datetime
import xml.etree.cElementTree as ET
from sqlalchemy import func

import app
from app import db
from app.models import Vote, Bill, BillType, Representative, LegislativeSubjects, BillStatus


BILLS_PATH = os.path.join(app.CONGRESS_PATH, "data")
latest_session = sorted([x for x in os.listdir(BILLS_PATH) if x.isdigit()])[-1]
BILLS_PATH = os.path.join(BILLS_PATH, latest_session, 'bills')
XML_FILE = 'fdsys_billstatus.xml'
JSON_FILE = 'data.json'
LAST_MOD_FILE1 = 'data-fromfdsys-lastmod.txt'
LAST_MOD_FILE2 = 'fdsys_billstatus-lastmod.txt'

class Bills:
    @classmethod
    def load_bills_into_mysql(cls, last_mod_flag=False):
        """Read all json bill data, and push it into mysql db.
           Link table with other tables (Votes, Reps, Status, Subjects, etc.)"""
        # Today's Date
        today = datetime.now().date()

        for bill_type in BillType.types:
            db_bill_type = getattr(BillType, bill_type.upper()) # db_bill_types starts counting at 1
            type_path = os.path.join(BILLS_PATH, bill_type)

            for dir_name in os.listdir(type_path):
                # iterating over bills (one bill per directory inside type_path)
                try:
                    with open(os.path.join(type_path, dir_name, JSON_FILE), 'r') as f:
                        jsondata = json.load(f)
                except IOError:
                    print("{}: {}".format(latest_session, dir_name))
                    continue

                cong = jsondata['congress']
                num = jsondata['number']
                intro_date = jsondata['introduced_at']
                intro_date = datetime.strptime(intro_date, '%Y-%m-%d').date()

                # data variable reassigned FROM json TO XML tree
                xmldata = ET.parse(os.path.join(type_path, dir_name, XML_FILE)).getroot()

                if last_mod_flag:
                    # check from one of the two last-modified files
                    try:
                        with open(os.path.join(type_path, dir_name, LAST_MOD_FILE1), 'r') as f:
                            last_mod = f.read()
                    except IOError:
                        with open(os.path.join(type_path, dir_name, LAST_MOD_FILE2), 'r') as f:
                            last_mod = f.read()
                    last_mod = last_mod[:10]
                    last_mod = datetime.strptime(last_mod, '%Y-%m-%d').date()
                    if (today - last_mod).days > 1:
                        # if last modified is greater than 1 day,
                        # then ignore that file, and continue
                        continue
                    else:
                        # if last modified occurred on this day,
                        # then perform an "update" of the existing record.
                        # Precondition: the bill has been fully loaded.
                        # Postcondition: the following params have been updated:
                        # active, awaiting_sig, enacted, vetoed, status objects
                        bill_q = Bill.query.filter(Bill.bill_type == db_bill_type) \
                            .filter(Bill.bill_num == num) \
                            .filter(Bill.congress == cong)
                        bills = bill_q.all()
                        if len(bills) == 0:
                            # bill does not exist, call the fully_populate function
                            Bills.fully_populate_bill(jsondata, xmldata, num, db_bill_type)
                        else:
                            # bill does exist, and we just want to update
                            # update actions, 4 status variables, and cosponsors
                            Bills.update_bill(jsondata, xmldata, bills[0])
                        continue
                Bills.fully_populate_bill(jsondata, xmldata, num, db_bill_type)
                # end of dir_name iteration
            # end of bill_type iteration
        # end of function


    @classmethod
    def return_sql_json_by_date(cls, date):
        current_date = date.date()
        date_to_query = current_date
        d = {}

        # store the most recent bill introduced OF EACH TYPE
        recent_date_by_type = {}
        for bill_type_abbr in BillType.types:
            bill_type = getattr(BillType, bill_type_abbr.upper()) # bill_types starts counting at 1
            introduced_ordered_q = Bill.query.filter(Bill.bill_type == bill_type).order_by(Bill.introduced_date.desc())
            max_intro_date = introduced_ordered_q.first().introduced_date.date()
            if current_date > max_intro_date:
                date_to_query = max_intro_date
            else:
                date_to_query = current_date
            type_bills_inrange = introduced_ordered_q.filter(Bill.introduced_date == date_to_query).all()
            d[bill_type_abbr] = type_bills_inrange
        return d


    @classmethod
    def fully_populate_bill(cls, jsondata, xmldata, bill_num, bill_type):
        # idempotent function, will not corrupt if called even if bill is fully populated
        if jsondata['short_title'] == None:
            if jsondata['popular_title'] == None:
                title = jsondata['official_title']
            else:
                title = jsondata['popular_title']
        else:
            title = jsondata['short_title']
        title = title if len(title) <= 256 else title[:256]

        cong = jsondata['congress']
        num = jsondata['number']
        active = jsondata['history']['active']
        sig = jsondata['history']['awaiting_signature']
        enact = jsondata['history']['enacted']
        veto = jsondata['history']['vetoed']
        try:
            comm = jsondata['committees'][0]['committee']
        except IndexError:
            comm = None

        intro_date = jsondata['introduced_at']
        intro_date = datetime.strptime(intro_date, '%Y-%m-%d').date()

        bill_q = Bill.query.filter(Bill.bill_type == bill_type) \
            .filter(Bill.bill_num == num) \
            .filter(Bill.congress == cong)
        bills = bill_q.all()

        if len(bills) > 0:
            # if the bill has been instantiated,
            # check if bill has been fully populated
            bill = bills[0]
            populated = bool(bill.title)
            if not populated:
                # if not populated, instantiate key identifying info (title, origin date)
                bill.congress = cong
                bill.title = title
                bill.introduced_date = intro_date
            # overwrite with most recent status info
            bill.active = active
            bill.awaiting_sig = sig
            bill.enacted = enact
            bill.vetoed = veto
            bill.committee = comm
        else:
            # if bill has NOT been instantiated,
            # create instantiation and add to db
            populated = False
            bill = Bill(title=title, congress=cong,
                bill_type=bill_type,
                bill_num=num,
                introduced_date=intro_date,
                committee=comm,
                active=active,
                awaiting_sig=sig,
                enacted=enact,
                vetoed=veto)
            db.session.add(bill)

        # delete old statuses
        bill.statuses = [] # clears all actions attached to this bill
        statuses = BillStatus.query.filter(BillStatus.bill_id == bill.id).all()
        for bs in statuses:
            db.session.delete(bs)
        # bill statuses and actions
        actions = jsondata['actions']
        for act in actions:
            stat = BillStatus()
            d = act['acted_at'][:10]
            d = datetime.strptime(d, '%Y-%m-%d').date()
            text = act['text']
            text = text if len(text) < 128 else text[:128]
            act_type = act['type']
            stat.date = d
            stat.text = text
            stat.action_type = act_type
            bill.statuses.append(stat)

        if not populated:
            # set and link legislative subjects
            subjects = jsondata['subjects']
            for subj in subjects:
                subj_q = LegislativeSubjects.query.filter(func.lower(LegislativeSubjects.subject) == subj.lower())
                loaded_subjects = subj_q.all()
                if loaded_subjects:
                    for sub in loaded_subjects:
                        bill.leg_subjects.append(sub)
                else:
                    new_sub = LegislativeSubjects()
                    new_sub.subject = subj
                    bill.leg_subjects.append(new_sub)

            # sponsors
            spon = xmldata[0].findall('sponsors')
            spon = spon[0]
            bio_id = spon[0].find('bioguideId').text
            lname = spon[0].find('lastName').text
            fname = spon[0].find('firstName').text
            state = spon[0].find('state').text
            party = spon[0].find('party').text

            if bill_type < 5:
                # Bill originated in the House of Representatives
                # Search for reps using bioguide_id
                rep_q = Representative.query.filter(Representative.bioguide_id == bio_id)
            else:
                # Bill originated in the Senate
                # Search for reps using state + party lastname
                rep_q = Representative.query.filter(Representative.state == state) \
                    .filter(Representative.party == party) \
                    .filter(func.lower(Representative.lname) == lname.lower())
            reps = rep_q.all()

            if len(reps) > 0:
                # representative exists in the database
                # add them as a sponsor to this bill.
                rep = reps[0]
            else:
                rep = Representative()
            rep.bioguide_id = bio_id
            rep.fname = fname.title()
            rep.lname = lname.title()
            mname = spon[0].find('middleName').text
            if mname is not None:
                rep.mname = mname.title()
            rep.state = state
            rep.party = party
            rep.active = True
            bill.sponsor = rep
            # end of not-populated clause

        # cosponsors
        bill.cosponsors = [] # clears all actions attached to this bill
        cospon = xmldata[0].findall('cosponsors')
        cospon = cospon[0]
        for c in cospon:
            bio_id = c.find('bioguideId').text
            lname = c.find('lastName').text
            fname = c.find('firstName').text
            state = c.find('state').text
            party = c.find('party').text

            if bill_type < 5:
                # Bill originated in the House of Representatives
                # Search for reps using bioguide_id
                rep_q = Representative.query.filter(Representative.bioguide_id == bio_id)
            else:
                # Bill originated in the Senate
                # Search for reps using state + party lastname
                rep_q = Representative.query.filter(Representative.state == state) \
                    .filter(Representative.party == party) \
                    .filter(func.lower(Representative.lname) == lname.lower())
            reps = rep_q.all()
            if len(reps) > 0:
                # representative exists in the database
                # add them as a cosponsor to this bill.
                rep = reps[0]
            else:
                rep = Representative()
            rep.bioguide_id = bio_id
            rep.fname = fname.title()
            rep.lname = lname.title()
            mname = c.find('middleName').text
            if mname is not None:
                rep.mname = mname.title()
            rep.state = state
            rep.party = party
            rep.active = True
            bill.cosponsors.append(rep)
            # end of cosponsor iteration
        db.session.commit()


    @classmethod
    def update_bill(cls, jsondata, xmldata, bill):
        # precondition: requires bill to be fully populated beforehand
	# overwrites actions, 4 status variables, and cosponsors
        bill.active = jsondata['history']['active']
        bill.awaiting_sig = jsondata['history']['awaiting_signature']
        bill.enacted = jsondata['history']['enacted']
        bill.vetoed = jsondata['history']['vetoed']

        # delete old statuses
        bill.statuses = []
        statuses = BillStatus.query.filter(BillStatus.bill_id == bill.id).all()
        for bs in statuses:
            db.session.delete(bs)
        # append all current statuses
        actions = jsondata['actions']
        for act in actions:
            stat = BillStatus()
            d = act['acted_at'][:10]
            d = datetime.strptime(d, '%Y-%m-%d').date()
            text = act['text']
            text = text if len(text) < 128 else text[:128]
            act_type = act['type']
            stat.date = d
            stat.text = text
            stat.action_type = act_type
            bill.statuses.append(stat)

        # unlink old cosponsors
        bill.cosponsors = []
        #link new cosponsors
        cospon = xmldata[0].findall('cosponsors')
        cospon = cospon[0]
        for c in cospon:
            bio_id = c.find('bioguideId').text
            lname = c.find('lastName').text
            fname = c.find('firstName').text
            state = c.find('state').text
            party = c.find('party').text

            if bill.bill_type < 5:
                # Bill originated in the House of Representatives
                # Search for reps using bioguide_id
                rep_q = Representative.query.filter(Representative.bioguide_id == bio_id)
            else:
                # Bill originated in the Senate
                # Search for reps using state + party lastname
                rep_q = Representative.query.filter(Representative.state == state) \
                    .filter(Representative.party == party) \
                    .filter(func.lower(Representative.lname) == lname.lower())
            reps = rep_q.all()
            if len(reps) > 0:
                # representative exists in the database
                # add them as a cosponsor to this bill.
                rep = reps[0]
            else:
                rep = Representative()
            rep.bioguide_id = bio_id
            rep.fname = fname.title()
            rep.lname = lname.title()
            mname = c.find('middleName').text
            if mname is not None:
                rep.mname = mname.title()
            rep.state = state
            rep.party = party
            rep.active = True
            bill.cosponsors.append(rep)
            # end of cosponsor iteration
        db.session.commit()
