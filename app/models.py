from app import db

###########################
# Many-Many Helper Tables #
###########################

yea_votes = db.Table(
    'yea_votes',
    db.Column('vote_id', db.Integer, db.ForeignKey('vote.id')),
    db.Column('rep_id', db.Integer, db.ForeignKey('representative.id'))
)

nay_votes = db.Table(
    'nay_votes',
    db.Column('vote_id', db.Integer, db.ForeignKey('vote.id')),
    db.Column('rep_id', db.Integer, db.ForeignKey('representative.id'))
)

not_votes = db.Table(
    'not_votes',
    db.Column('vote_id', db.Integer, db.ForeignKey('vote.id')),
    db.Column('rep_id', db.Integer, db.ForeignKey('representative.id'))
)

cosponsor_bills = db.Table(
    'cosponsor_bills',
    db.Column('bill_id', db.Integer, db.ForeignKey('bill.id')),
    db.Column('rep_id', db.Integer, db.ForeignKey('representative.id'))
)

bill_subjects = db.Table(
    'bill_subjects',
    db.Column('bill_id', db.Integer, db.ForeignKey('bill.id')),
    db.Column('subject_id', db.Integer, db.ForeignKey('legislative_subjects.id'))
)

bill_to_bills = db.Table(
    'bill_to_bills',
    db.Column('parent_bill_id', db.Integer, db.ForeignKey('bill.id')),
    db.Column('related_bill_id', db.Integer, db.ForeignKey('bill.id'))
)


class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chamber = db.Column(db.String(1))
    vote_num = db.Column(db.Integer, index=True)
    date = db.Column(db.DateTime)
    vote_result = db.Column(db.String(64))
    num_yeas = db.Column(db.Integer)
    num_nays = db.Column(db.Integer)
    num_abstains = db.Column(db.Integer)
    required = db.Column(db.String(10))
    vote_type = db.Column(db.String(32))
    question = db.Column(db.String(512))

    # 1-Many Single Entity
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'))

    # Many-Many Relationship
    yea_voters = db.relationship('Representative', secondary=yea_votes, backref='yea_votes')
    nay_voters = db.relationship('Representative', secondary=nay_votes, backref='nay_votes')
    not_voters = db.relationship('Representative', secondary=not_votes, backref='not_votes')

    def __repr__(self):
        return '<Vote:{}-{}>'.format(self.chamber, self.vote_num)


class BillType:
    HCONRES = 1
    HJRES = 2
    HR = 3
    HRES = 4
    S = 5
    SCONRES = 6
    SJRES = 7
    SRES = 8

    types = ['hconres', 'hjres', 'hr', 'hres', 's', 'sconres', 'sjres', 'sres']

    d = {}
    d[HCONRES] = 'House Concurrent Resolution'
    d[HJRES] = 'House Joint Resolution'
    d[HR] = 'House of Representatives'
    d[HRES] = 'House Simple Resolution'
    d[S] = 'Senate'
    d[SCONRES] = 'Senate Concurrent Resolution'
    d[SJRES] = 'Senate Joint Resolution'
    d[SRES] = 'Senate Simple Resolution'


class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256))
    congress = db.Column(db.Integer)
    bill_type = db.Column(db.Integer)
    bill_num = db.Column(db.Integer)
    introduced_date = db.Column(db.DateTime)
    committee = db.Column(db.String(128))
    cbo_link = db.Column(db.String(128))
    active = db.Column(db.Boolean)
    awaiting_sig = db.Column(db.Boolean)
    enacted = db.Column(db.Boolean)
    vetoed = db.Column(db.Boolean)

    # 1-Many Single Entity
    sponsor_id = db.Column(db.Integer, db.ForeignKey('representative.id'))

    # 1-Many Multiple Entity
    statuses = db.relationship('BillStatus', backref='bill', cascade='all, delete-orphan, delete')
    votes = db.relationship('Vote', backref='bill')

    # Many-Many Relationships
    cosponsors = db.relationship(
        'Representative',
        secondary=cosponsor_bills,
        backref='bills_cosponsored'
    )
    related_bills = db.relationship(
        'Bill',
        secondary=bill_to_bills,
        primaryjoin='Bill.id==bill_to_bills.c.related_bill_id',
        secondaryjoin='Bill.id==bill_to_bills.c.parent_bill_id',
        backref='parent_bills'
    )
    leg_subjects = db.relationship('LegislativeSubjects', secondary=bill_subjects, backref='bills')

    def __repr__(self):
        return '<Bill:{}-{}>'.format(BillType.types[self.bill_type-1], self.bill_num)


class Representative(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(24))
    mname = db.Column(db.String(24))
    lname = db.Column(db.String(24))
    bioguide_id = db.Column(db.String(12))
    lis_id = db.Column(db.String(12))
    state = db.Column(db.String(5))
    district = db.Column(db.Integer)
    party = db.Column(db.String(6))
    chamber = db.Column(db.String(1))
    active = db.Column(db.Boolean)

    # 1-Many Multiple Entity
    bills_sponsored = db.relationship('Bill', backref='sponsor')

    # Many-Many Relationships covered by Backref
    # bills_cosponsored <-> Bill
    # yea_votes <-> Vote
    # nay_votes <-> Vote
    # not_votes <-> Vote

    def __repr__(self):
        return '<{}:{}-{}>'.format(self.chamber, self.fname, self.lname)


class BillStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(128))
    action_type = db.Column(db.String(32))
    date = db.Column(db.DateTime)

    # 1-Many Single Entity
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'))


class LegislativeSubjects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(128))


#######################
# Budget Models Below #
#######################

class DeficitSurplus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, index=True)
    total_receipt = db.Column(db.Integer)
    total_outlay = db.Column(db.Integer)
    total_net = db.Column(db.Integer)
    onbud_receipt = db.Column(db.Integer)
    onbud_outlay = db.Column(db.Integer)
    onbud_net = db.Column(db.Integer)
    offbud_receipt = db.Column(db.Integer)
    offbud_outlay = db.Column(db.Integer)
    offbud_net = db.Column(db.Integer)

    def __repr__(self):
        return '<DefSur:{}-{}>'.format(self.year, self.total_net)


class ReceiptBreakdown(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, index=True)
    indiv_income_tax = db.Column(db.Integer)
    corp_income_tax = db.Column(db.Integer)
    soc_ins_retire_total = db.Column(db.Integer)
    excise_tax = db.Column(db.Integer)
    other = db.Column(db.Integer)

    def __repr__(self):
        return '<Receipt:{}-{}>'.format(self.year, self.indiv_income_tax)


class OutlayBreakdown(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, index=True)
    nat_def = db.Column(db.Integer)
    nat_def_perc_outlays = db.Column(db.Float)
    nat_def_perc_gdp = db.Column(db.Float)

    hum_res = db.Column(db.Integer)
    hum_res_perc_outlays = db.Column(db.Float)
    hum_res_perc_gdp = db.Column(db.Float)
    edu = db.Column(db.Integer)
    health = db.Column(db.Integer)
    medicare = db.Column(db.Integer)
    income_secur = db.Column(db.Integer)
    social_secur = db.Column(db.Integer)
    vet_benef = db.Column(db.Integer)

    phys_res = db.Column(db.Integer)
    phys_res_perc_outlays = db.Column(db.Float)
    phys_res_perc_gdp = db.Column(db.Float)
    energy = db.Column(db.Integer)
    nat_res_env = db.Column(db.Integer)
    commerce_house = db.Column(db.Integer)
    transport = db.Column(db.Integer)
    comm_reg_dev = db.Column(db.Integer)

    net_interest = db.Column(db.Integer)
    net_interest_perc_outlays = db.Column(db.Float)
    net_interest_perc_gdp = db.Column(db.Float)

    other_funcs = db.Column(db.Integer)
    other_funcs_perc_outlays = db.Column(db.Float)
    other_funcs_perc_gdp = db.Column(db.Float)
    intl_aff = db.Column(db.Integer)
    sci_spa_tech = db.Column(db.Integer)
    agriculture = db.Column(db.Integer)
    admin_justice = db.Column(db.Integer)
    gen_gov = db.Column(db.Integer)
