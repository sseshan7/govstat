# govstat

Source code for [GovStat.us](https://govstat.us) website.

Webserver is implemented using Flask on Python 3.10.

Install locally using `pip install .`

### Dependencies required: ###
- gunicorn
- xlrd
- pandas
- numpy
- flask
- flask-sqlalchemy
- pymysql
- flask-migrate
- flask-wtf

### Webapp Entrypoint
``gunicorn -b localhost:5000 -w 4 govstat:app``\
Host Name (localhost)\
Port Number (5000)\
Number of Threads/Handlers (4)\
Flask app and entrypoint (govstat:app)

### Flask MySQL DB Creation and Migration
```
flask db init
flask db migrate -m "initial migration"
flask db upgrade
```

### Gunicorn, NGINX, and Supervisor configuration
See above to run gunicorn.\
Specify NGINX port permissions, and forwarding for HTTP and HTTPS requests at `/etc/nginx/sites-enabled/`\
Configure supervisor to run gunicorn app at `/etc/supervisor/conf.d/`
Create SSL certificates

### Directory Structure

```
congress/
+--	govstat/
    +-- app/
        +--	Bills.py
        +-- Budget.py
        +-- config.py
        +-- __init.py__		[App instantiation, database instantiation, import functions for data loading and retrieval.]
        +-- models.py
        +-- routes.py
        +--	Votes.py
        +-- static/
        +-- templates/
    +-- govstat.py
    +-- setup.py
    +-- bill_loader.py
    +--	vote_loader.py
+--	data/
    +-- 116/
        +-- amendments/
            +-- hamdt/ [House Amendments]
                +-- hamdtN/
                    +-- [JSON and XML files]
            +-- samdt/ [Senate Amendments]
                +-- samdtN/
                    +-- [JSON and XML files]
        +-- bills/
            +-- hconres/
                +-- hconresN/
                    +-- [XML files. After processing, JSON files]
            +-- hjres/
                +-- hjresN/
                    +-- [XML files. After processing, JSON files]
            +-- hr
                +-- hrN/
                    +-- [XML files. After processing, JSON files]
            +-- hres/
                +-- hresN/
                    +-- [XML files. After processing, JSON files]
            +-- s/
                +-- sN/
                    +-- [XML files. After processing, JSON files]
            +-- sconres/
                +-- sconresN/
                    +-- [XML files. After processing, JSON files]
            +-- sjres/
                +-- sjresN/
                    +-- [XML files. After processing, JSON files]
            +-- sres/
                +-- sresN/
                    +-- [XML files. After processing, JSON files]
        +-- votes/
            +-- 2020/
                +-- hN/
                    +-- [JSON and XML files]
                +-- sN/
                    +-- [JSON and XML files]
                +-- 2021/ [One directory per year]
    +-- 117/ ... [One directory per congress session number]
    +--	hist_fy21/ [Historical data through 2021 from Office of Management and Budget (OMB)]
        +-- [51 XLSX files containing data].
    +-- supplemental/
        +-- [XLSX files containing supplemental budget data]
    +--	upcoming_house_floor/
        +-- [JSON files per week containing bill activities that week]
+-- tasks/
    +-- [PY files for each type of data that can be scraped and delivered]
    +--	[amendments, bills, committees, govinfo, nominations, votes, upcoming, etc.]
+-- scripts/
    +-- [SH scripts to transform raw JSON and XML data into forms usable for govtrack and other utilities.]
+-- cache/
+-- test/
    +-- [Test scripts, not exhaustive]
+-- contrib/
```
