# govstat

Source code for [GovStat.us](https://govstat.us) website.

![start\_page](https://user-images.githubusercontent.com/17132214/155255795-bf69314d-6f99-4750-af46-6c8b9693b3e0.png)
![budget](https://user-images.githubusercontent.com/17132214/155255799-56d17524-f30a-4681-82de-31f8369449b9.png)

Webserver is implemented using Flask on Python 3.10.

Install locally using `pip install .`

## Dependencies:

- [python](https://www.python.org/downloads/)
- [acxz/congress/python-packaging](https://github.com/acxz/congress/tree/python-package)
- [git-lfs](https://git-lfs.github.com/)
- A MySQL server
  - e.g. [MariaDB](https://mariadb.org/download)

Python dependencies will be pulled in automatically by `pip`.

## Data Sources
Some notes on where the data for this webapp comes from.
Congress data on bills and votes comes from scrapers in the
[unitedstates/congress](https://github.com/unitedstates/congress) repo.
Budget data comes from excel files published by the White House
[Office of Management and Budget (OMB)](https://www.whitehouse.gov/omb/historical-tables/).

To obtain congress data, do the following:

From the root of this repo, run:
```bash
usc-run votes --congress=XXX --session=YYYY --force=True
usc-run govinfo --bulkdata=BILLSTATUS --congress=XXX
usc-run bills
```
where `XXX` is the Congress number, and `YYYY` is the session number.

For example,
```bash
usc-run votes --congress=117 --session=2022 --force=True
usc-run govinfo --bulkdata=BILLSTATUS --congress=117
usc-run bills
```

Budget data is carried in this repo via `git-lfs`.

## Flask MySQL DB Creation

### Start a MySQL Server.
Simple start for MariaDB:
```bash
sudo mariadb-install-db --user=mysql --basedir=/usr --datadir=/var/lib/mysql
sudo systemctl start mariadb.service
```

### Add Configuration Information:
```bash
cp app/cfg/config.sample.json app/cfg/config.json
```
and edit in the appropriate values to `app/cfg/config.json`.

### Initialize and Start `flask`.
```bash
flask db init
flask db migrate -m "initial migration"
flask db upgrade
```

### Populate DB
After creating the flask MySQL DB run the following commands to populate it:
```bash
python vote_loader.py
python bill_loader.py
python budget_loader.py
```

## Webapp Entrypoint

To launch the webapp:
```bash
gunicorn -b localhost:5000 -w 4 govstat:app
```

- Host Name (`localhost`)
- Port Number (`5000`)
- Number of Threads/Handlers (`4`)
- Flask app and entrypoint (`govstat:app`)

## Gunicorn, NGINX, and Supervisor Configuration

See above to run gunicorn.\
Specify NGINX port permissions, and forwarding for HTTP and HTTPS requests at `/etc/nginx/sites-enabled/`\
Configure supervisor to run gunicorn app at `/etc/supervisor/conf.d/`\
Create SSL certificates

## Directory Structure

```
congress/
+--	govstat/
    +-- app/
        +--	Bills.py
        +-- Budget.py
        +-- config.py
        +-- __init__.py		[App instantiation, database instantiation, import functions for data loading and retrieval.]
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
