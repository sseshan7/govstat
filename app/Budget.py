import os
import pandas as pd

import app
from app import db
from app.models import DeficitSurplus, ReceiptBreakdown, OutlayBreakdown

# globals
EXCEL_DIR = os.path.join(app.CONGRESS_PATH, 'data', 'hist_fy21')
BUDGET_1 = 'hist01z1.xlsx'
BUDGET_2 = 'hist02z1.xlsx'
BUDGET_3 = 'hist03z1.xlsx'
EXCEL_FILES = sorted(os.listdir(EXCEL_DIR))
BUDGET_ROW_THRESH = 6

key_index_dict = {}
key_index_dict['nat_def'] = [2, 'National Defense']
key_index_dict['nat_def_perc_outlays'] = [37, 'National Defense Percentage of Outlays']
key_index_dict['nat_def_perc_gdp'] = [47, 'National Defense Percentage of GDP']

key_index_dict['hum_res'] = [3, 'Human Resources']
key_index_dict['hum_res_perc_outlays'] = [38, 'Human Resources Percentage of Outlays']
key_index_dict['hum_res_perc_gdp'] = [48, 'Human Resources Percentage of GDP']
key_index_dict['edu'] = [4, 'Education']
key_index_dict['health'] = [5, 'Health']
key_index_dict['medicare'] = [6, 'Medicare']
key_index_dict['income_secur'] = [7, 'Income Security']
key_index_dict['social_secur'] = [8, 'Social Security']
key_index_dict['vet_benef'] = [11, 'Veterans Benefits']

key_index_dict['phys_res'] = [12, 'Physical Resources']
key_index_dict['phys_res_perc_outlays'] = [39, 'Physical Resources Percentage of Outlays']
key_index_dict['phys_res_perc_gdp'] = [49, 'Physical Resources Percentage of GDP']
key_index_dict['energy'] = [13, 'Energy']
key_index_dict['nat_res_env'] = [14, 'Natural Resources and Environment']
key_index_dict['commerce_house'] = [15, 'Commerce and Housing Credit']
key_index_dict['transport'] = [18, 'Transportation']
key_index_dict['comm_reg_dev'] = [19, 'Community and Regional Development']

key_index_dict['net_interest'] = [20, 'Net Interest']
key_index_dict['net_interest_perc_outlays'] = [40, 'Net Interest Percentage of Outlays']
key_index_dict['net_interest_perc_gdp'] = [50, 'Net Interest Percentage of GDP']

key_index_dict['other_funcs'] = [23, 'Other Functions']
key_index_dict['other_funcs_perc_outlays'] = [41, 'Other Functions Percentage of Outlays']
key_index_dict['other_funcs_perc_gdp'] = [51, 'Other Functions Percentage of GDP']
key_index_dict['intl_aff'] = [24, 'International Affairs']
key_index_dict['sci_spa_tech'] = [25, 'General Science, Space, and Technology']
key_index_dict['agriculture'] = [26, 'Agriculture']
key_index_dict['admin_justice'] = [27, 'Administration of Justice']
key_index_dict['gen_gov'] = [28, 'General Government']

def load_mysql_deficit_surplus():
    dataxls = pd.read_excel(os.path.join(EXCEL_DIR, BUDGET_1), index_col=None)
    for row_num, row in dataxls.iterrows():
        if row_num > BUDGET_ROW_THRESH:
            d = DeficitSurplus()
            try:
                d.year = int(row[0])
            except ValueError:
                print("Problem with Year")
                print(row)
                print()
                continue
            d.total_receipt = int(row[1])
            d.total_outlay = int(row[2])
            d.total_net = int(row[3])
            d.onbud_receipt = int(row[4])
            d.onbud_outlay = int(row[5])
            d.onbud_net = int(row[6])
            try:
                d.offbud_receipt = int(row[7])
                d.offbud_outlay = int(row[8])
                d.offbud_net = int(row[9])
            except ValueError:
                pass
            db.session.add(d)
            db.session.commit()


def read_mysql_deficit_surplus():
    data_dict = {}
    tot_data_query = db.session.query(DeficitSurplus.year).order_by(DeficitSurplus.year)
    data_dict['years'] = [x[0] for x in tot_data_query.all()]
    tot_data_query = db.session.query(DeficitSurplus.total_receipt).order_by(DeficitSurplus.year)
    data_dict['total_receipts'] = [x[0] for x in tot_data_query.all()]
    tot_data_query = db.session.query(DeficitSurplus.total_outlay).order_by(DeficitSurplus.year)
    data_dict['total_outlays'] = [x[0] for x in tot_data_query.all()]
    tot_data_query = db.session.query(DeficitSurplus.total_net).order_by(DeficitSurplus.year)
    data_dict['total_net'] = [x[0] for x in tot_data_query.all()]

    d = {}
    d['total_receipts'] = "Total Receipts (Money Collected)"
    d['total_outlays'] = "Total Outlays (Money Spent)"
    d['total_net'] = "Net Deficit or Surplus"
    data_dict['full_names'] = d
    return data_dict


def load_mysql_receipt_breakdown():
    dataxls = pd.read_excel(os.path.join(EXCEL_DIR, BUDGET_2), index_col=None)
    for row_num, row in dataxls.iterrows():
        if row_num > 3:
            d = ReceiptBreakdown()
            try:
                d.year = int(row[0])
            except ValueError:
                print("Problem with Year")
                print(row)
                print()
                continue
            d.indiv_income_tax = int(row[1])
            d.corp_income_tax = int(row[2])
            d.soc_ins_retire_total = int(row[3])
            d.excise_tax = int(row[6])
            d.other = int(row[7])
            db.session.add(d)
            db.session.commit()


def read_mysql_receipt_breakdown():
    data_dict = {}
    data_query = db.session.query(ReceiptBreakdown.year).order_by(ReceiptBreakdown.year)
    data_dict['years'] = [x[0] for x in data_query.all()]
    data_query = db.session.query(ReceiptBreakdown.indiv_income_tax).order_by(ReceiptBreakdown.year)
    data_dict['indiv_income_tax'] = [x[0] for x in data_query.all()]
    data_query = db.session.query(ReceiptBreakdown.corp_income_tax).order_by(ReceiptBreakdown.year)
    data_dict['corp_income_tax'] = [x[0] for x in data_query.all()]
    data_query = db.session.query(ReceiptBreakdown.soc_ins_retire_total).order_by(ReceiptBreakdown.year)
    data_dict['insurance_retirement'] = [x[0] for x in data_query.all()]
    data_query = db.session.query(ReceiptBreakdown.excise_tax).order_by(ReceiptBreakdown.year)
    data_dict['excise_tax'] = [x[0] for x in data_query.all()]
    data_query = db.session.query(ReceiptBreakdown.other).order_by(ReceiptBreakdown.year)
    data_dict['other'] = [x[0] for x in data_query.all()]

    d = {}
    d['indiv_income_tax'] = "Individual Income Taxes"
    d['corp_income_tax'] = "Corporate Income Taxes"
    d['insurance_retirement'] = "Social Insurance and Retirement Receipts"
    d['excise_tax'] = "Excise Taxes"
    d['other'] = "Other"
    data_dict['full_names'] = d
    return data_dict


def load_mysql_outlay_breakdown():
    dataxls = pd.read_excel(os.path.join(EXCEL_DIR, BUDGET_3), index_col=None)
    num_cols = len(dataxls.iloc[0, :])

    for n in range(1, num_cols):
        d = OutlayBreakdown()
        col = dataxls.iloc[:, n]
        try:
            d.year = int(col[0])
        except ValueError:
            print('Problem with year')
            print(col)
            print()
            continue
        for k in key_index_dict:
            # iterate over keys, get value in dataframe, insert into model object
            try:
                setattr(d, k, int(col[key_index_dict[k][0]]))
            except ValueError:
                try:
                    setattr(d, k, float(col[key_index_dict[k][0]]))
                except ValueError:
                    setattr(d, k, 0)

        db.session.add(d)
        db.session.commit()


def read_mysql_outlay_breakdown():
    data_dict = {}
    data_query = db.session.query(OutlayBreakdown.year).order_by(OutlayBreakdown.year)
    data_dict['years'] = [x[0] for x in data_query.all()]

    for k in key_index_dict:
        data_query = db.session.query(getattr(OutlayBreakdown, k)).order_by(OutlayBreakdown.year)
        data_dict[k] = [x[0] for x in data_query.all()]

    data_dict['full_names'] = {}
    for k in key_index_dict:
        data_dict['full_names'][k] = key_index_dict[k][1]
    return data_dict


def load_mysql_all_budget():
    load_mysql_deficit_surplus()
    load_mysql_receipt_breakdown()
    load_mysql_outlay_breakdown()
