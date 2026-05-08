import re
from selenium import webdriver
from selenium.common.exceptions import (WebDriverException,
                                        NoSuchElementException,
                                        TimeoutException,
                                        ElementClickInterceptedException,
                                        InvalidElementStateException,
                                        ElementNotInteractableException,
                                        StaleElementReferenceException)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.proxy import Proxy, ProxyType
import paramiko
import pdfplumber
import requests
import pandas as pd
import time
import os
import numpy as np
from pathlib import Path
import random
import datetime as dt
from io import BytesIO
import MySQLdb as mysql
from MySQLdb._exceptions import OperationalError, DataError
import pdf2image
import pytesseract



print("punto 1")
WEBDRIVER_LOC = str(Path(__file__).parent.resolve()/'chromedriver')
# TESSERACT_LOC = str(Path(__file__).parent.resolve()/'Tesseract-OCR/tesseract')
TESSERACT_LOC = Path('/usr/bin/tesseract')
pytesseract.pytesseract.tesseract_cmd = TESSERACT_LOC

'''
MYSQL = {'host': '193.70.114.235', 'user': 'finser', 'passwd': 'finser1905?',
         'db': 'finser_utilities_db', 'use_unicode': True,
         'charset': 'utf8mb4'}
'''
MYSQL = {'host': '146.59.233.56', 'user': 'finser', 'passwd': 'finser0914?',
         'db': 'finser_utilities_db', 'use_unicode': True,
         'charset': 'utf8mb4'}

DEBIAN = {'hostname': '146.59.233.56', 'username': 'servern',
          'password': 'Chi1456?'}
USERNAME = "svilupp01"
PASSWORD = "Sv1luPp02045"
ENDPOINT = "pr.oxylabs.io"
PORTS = [*range(20001, 30000)]
COUNTRY = 'IT'

def connect():
    while True:
        try:
            conn = mysql.connect(**MYSQL)
            return conn
        except OperationalError:
            continue


def load(tbl):
    conn = connect()
    SQL = f"SELECT * FROM {tbl}"
    df = pd.read_sql_query(SQL, conn)
    conn.close()
    return df


def execute(sql):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()


def write(tbl, entries, fields):
    conn = connect()
    cursor = conn.cursor()
    new = []
    #print(fields)
    #print(entries)
    for e in entries:
        new.append({f: v for f, v in zip(fields, e)})
    sql = 'INSERT INTO ' + '`' + tbl + '`'
    fields_str = ", ".join([f'`{f}`' for f in fields])
    sql += " (" + fields_str + ")"
    val_str = ' VALUES ' + ", ".join(
        '(' + ", ".join(["'"+str(v).replace("'", "''")+"'" for v in e]) + ')'
        for e in entries)
    sql += val_str
    sql = sql.replace("'None'", 'NULL')
    print(sql)
    cursor.execute(sql)
    conn.commit()
    conn.close()

# Open the browser without connection to the proxy
'''
def get_browser():
    options = Options()
    options.add_argument('--disable-notifications')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--headless')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    prefs = {'download.default_directory': os.getcwd()}
    options.add_experimental_option('prefs', prefs)
    capabilities = DesiredCapabilities().CHROME
    capabilities.update(options.to_capabilities())
    i = 0
    while True:
        print(f'Launching ChromeDriver. Attempt {i}...')
        i += 1
        try:
            browser = webdriver.Chrome(WEBDRIVER_LOC, options=options)
        except WebDriverException as e:
            print(e)
            continue
        return browser
'''

def get_proxy(country, endpoint):
    port = np.random.choice(PORTS)
    PORTS.remove(port)
    address = f'http://{country.lower()}-{endpoint}:{port}'
    # return address#####
    proxy = Proxy()
    proxy.proxy_type = ProxyType.MANUAL
    proxy.http_proxy = address
    proxy.ssl_proxy = address
    return proxy

# Open the browser with connection to the proxy

def get_browser():
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-notifications')
    options.add_argument('--window-size=1920,1080')
    options.headless = True
    options.add_argument('--headless')
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    # options.add_argument('--remote-debugging-port=9222')
    options.add_argument('disable-infobars')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)

    prefs = {'download.default_directory': os.getcwd()}
    options.add_experimental_option('prefs', prefs)

    # proxies = chrome_proxy(USERNAME, PASSWORD, COUNTRY, ENDPOINT)
    # options.add_argument(get_proxy(COUNTRY, ENDPOINT))

    capabilities = webdriver.DesiredCapabilities.CHROME
    proxy = get_proxy(COUNTRY, ENDPOINT)
    proxy.add_to_capabilities(capabilities)
    # webdriver.DesiredCapabilities.CHROME['proxy']= {
    #     "httpProxy": proxy,
    #     "ftpProxy": proxy,
    #     "sslProxy": proxy,
    #     "noProxy": None,
    #     "proxyType": "MANUAL",
    #     "autodetect": False}
    # capabilities['proxy'] = {'proxyType': 'MANUAL', 'httpProxy': proxy, 'ftpProxy': proxy, 'sslProxy': proxy, 'class': 'org.openqa.selenium.Proxy', 'autodetect': False}
    # capabilities.update(options.to_capabilities())

    i = 0
    while True:
        print(f'Launching ChromeDriver. Attempt {i}...')
        i += 1
        try:
            # browser = webdriver.Chrome(WEBDRIVER_LOC, options=options, seleniumwire_options=proxies)
            # browser = webdriver.Chrome(ChromeDriverManager().install(), options=options, seleniumwire_options=proxies)
            # browser = webdriver.Chrome(WEBDRIVER_LOC, options=options)
            browser = webdriver.Chrome(WEBDRIVER_LOC, options=options, desired_capabilities=capabilities)
        except WebDriverException as e:
            print(e)
            continue
        return browser

print("punto 2")
def randpause(seconds=4, minimum=1):
    delay = max(minimum+random.random(), seconds*random.random())
    time.sleep(delay)


class Trader():
    NAME = None
    ID = None
    URL = None
    DOCTYPES = []
    IMAGES = False
    PDF_BROWSER = False
    SLICES = [.5]

    def __init__(self):
        self.date = None
        defs = load('traders')
        self.defs = defs[defs['id'] == self.ID].iloc[0].to_dict()
        self.errors = []

        client = self.client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def run(self, download_cg=False, date=None):
        '''
        Parameters
        ----------
        download_cg : bool
            If set to True, the CG file will also be downloaded

        date : optional datetime
            If you would like files to save with a different date than today,
            you can enter it here
        '''
        
        self.date = date
        self.get_products()
        #self.compare_products()
        #self.scrape_pdfs(download_cg)

    def get_products(self):
        '''
        This is a custom method for each trader that will scrape the website
        for available products and links.
        '''
        print('Getting Products From Website...')
        products = []
        return products


    print("punto 3.2")

    def _get_pdf_links(self, products, browser):
        '''
        This is a custom method for each trader that is called by get_products
        to get the PDF links.
        '''
        return products
    '''
    def compare_products(self):
        print("punto3.7")
        This method will be common to all traders.  It will compare products
        and links.
        print("punto3.6")
        print('Comparing Products...')
        print("punto3.7")
        products = self.products
        products_db = load('products')
        products_db = products_db[(products_db['id_trader'] == self.ID)]

        print("punto3.5")
        new = []
        for p in products:
            c1 = 'LUCE' if p[0] == 1 else 'GAS'
            c2 = self._format_title(p[1])
            row = products_db[
                products_db['nome_intern_product'].str.contains(c1) &
                (products_db['nome_intern_product'].str.replace('GAS', '').str
                 .replace('LUCE', '').str.replace(' ', '').str.lower() == c2)]
            if len(row) == 0:
                typ = 5 if c1 == 'LUCE' else 6
                new.append([self.ID, c2.upper()+' '+c1, typ, 1])
        print("punto 3.3")
        titles = [self._format_title(x[1]).upper() for x in products]
        titles = [t[:-1] if t[-1] == '_' else t for t in titles]
        titles = [t + (' GAS' if products[i][0] == 2 else ' LUCE')
                  for i, t in enumerate(titles)]
        off = []
        for p in products_db.values:
            if p[2] not in titles:
                off.append(p[0])

        if (len(new) > 0) or (len(off) > 0):
            self._update_products(new, off, products_db)
        self._compare_links()
    '''

    def _format_title(self, name):
        c2 = (name.lower().replace('luce e gas ', '')
              .replace(self.NAME.lower()+' ', '').replace('+ ', '')
              .replace('gas e luce ', '').replace('gas ', '')
              .replace('luce ', '').replace('gas', '')
              .replace('luce', '').replace('e.on ', '').replace(' ', '_'))
        c2 = c2[:-1] if c2[-1] == '_' else c2
        return c2

    def _update_products(self, new, off, products_db):
        print('Updating Products...')
        off = [str(o) for o in off]
        ids = '(' + ','.join(off) + ')'


        print("punto 3.1")
        if len(off) > 0:
            SQL = f"UPDATE products SET on_off = 0 WHERE `id` IN {ids}"
            execute(SQL)

            SQL = (f"UPDATE products SET on_off = 1 WHERE `id` NOT IN {ids} "
                   f"AND id_trader = {self.ID}")
            execute(SQL)

            SQL = (f"UPDATE links SET on_off = 0 WHERE `id_product` "
                   f"IN {ids} AND id_trader = {self.ID}")
            execute(SQL)

        else:
            SQL = f"UPDATE products SET on_off = 1 WHERE id_trader = {self.ID}"
            execute(SQL)

        if len(new) > 0:
            write('products', new, products_db.columns[1:])

        self._products_new = new
        self._products_off = off

    '''
    def _compare_links(self):
        print('Comparing Links...')
        products_db = load('products')
        products_db = products_db[products_db['id_trader'] == self.ID]
        links_db = load('links')
        links_db = links_db[(links_db['id_trader'] == self.ID) &
                            (links_db['on_off'] == 1)]

        doc_to = {'SCHEDA+CTE': ['_CTE-SC',
                                 'Condizioni economiche e scheda sintetica'],
                  'SCHEDA': ['_SC', 'Scheda di confrontabilità'],
                  'CTE': ['', 'Condizioni economiche'],
                  'CG': ['_CG', 'Condizioni generali di contratto'],
                  'SCHEDA+CTE+CG': ['_CTE-SC-CG', (
                      'Condizioni economiche e scheda sintetica e condizioni '
                      'generali di contratto')]}

        new = []
        off = []
        for p in self.products:
            c1 = 'LUCE' if p[0] == 1 else 'GAS'
            c2 = self._format_title(p[1])
            row = products_db[
                products_db['nome_intern_product'].str.contains(c1) &
                (products_db['nome_intern_product'].str.replace('GAS', '').str
                 .replace('LUCE', '').str.replace(' ', '').str.lower() == c2)]
            if len(row) < 1:
                continue
            _id = row.iloc[0]['id']

            # Main Link
            r = links_db[(links_db['id_product'] == _id) &
                         (links_db['id_tipo_link'] == 1)]
            if len(r) == 0:
                new.append([self.ID, 1, p[2], None, None, None, _id, 1])
            else:
                r = r.iloc[0]
                if r['description_link'] != p[2]:
                    off.append(r['id'])
                    new.append([self.ID, 1, p[2], None, None, None, _id, 1])

            # PDF Links
            r = links_db[(links_db['id_product'] == _id) &
                         (links_db['id_tipo_link'] == 2) &
                         (links_db['on_off'] == 1)]
            address = f'_{self.NAME}_{c1}_{c2.upper()}_RES'
            #print(c2)
            address = address.replace('&', 'AND')
            if len(r) == 0:
                for i, doc in enumerate(self.DOCTYPES):
                    new.append(
                        [self.ID, 2, p[3+i], address+doc_to[doc][0], doc,
                         doc_to[doc][1], _id, 1])
            else:
                for i, doc in enumerate(self.DOCTYPES):
                    line = r[r['tipo_info'] == doc]
                    if len(line) == 0:
                        new.append(
                            [self.ID, 2, p[3+i], address+doc_to[doc][0], doc,
                             doc_to[doc][1], _id, 1])
                    elif line.iloc[0]['description_link'] != p[3+i]:
                        off.append(line.iloc[0]['id'])
                        new.append(
                            [self.ID, 2, p[3+i], address+doc_to[doc][0], doc,
                             doc_to[doc][1], _id, 1])

        on = [p['id'] for _, p in products_db.iterrows() if p['on_off'] == 1]
        off += [r['id'] for _, r in links_db.iterrows() if
                (r['id_product'] not in on)]

        self._update_links(new, off, links_db)
    '''
    def _update_links(self, new, off, links_db):
        print('Updating Links...')
        ids = '(' + ','.join([str(x) for x in off]) + ')'

        print("punto 3")
        # Set on/off to off for old links
        if len(off) > 0:
            SQL = f"UPDATE links SET on_off = 0 WHERE `id` IN {ids}"
            execute(SQL)

        # Write new links
        if len(new) > 0:
            write('links', new, links_db.columns[1:])

            # Update search tags, homog for changed links
            if len(off) > 0:
                links_db = load('links')
                links_db = links_db[(links_db['id_trader'] == self.ID)]
                links_db = links_db.where(~links_db.isna(), '')
                for _id in off:
                    match = links_db[links_db['id'] == _id
                                     ].iloc[0][['id_product', 'tipo_info']]
                    r = links_db[
                        (links_db[match.index] == match.values).all(axis=1) &
                        (links_db['on_off'] == 1)].iloc[0]
                    SQL = (f'UPDATE search_tags_utl SET id_link = {r["id"]} '
                           f'WHERE id_link = {_id}')
                    execute(SQL)
                    SQL = (f'UPDATE homologation_tags SET id_link = {r["id"]} '
                           f'WHERE id_link = {_id}')
                    execute(SQL)

        self._links_new = new
        self._links_off = off

    def scrape_pdfs(self, download_cg=False):
        print('Scraping PDFs...')
        client = self.client
        client.connect(**DEBIAN)
        links_db = load('links')
        links_db = links_db[(links_db['id_trader'] == self.ID) &
                            (links_db['id_tipo_link'] == 2) &
                            (links_db['on_off'] == 1)]
        tags_db = load('search_tags_utl')
        tags_db = tags_db[(tags_db['id_trader'] == self.ID) &
                          (tags_db['on_off'] == 1) &
                          (tags_db['id_tipo_tag'] == 4)]
        homog_db = load('homologation_tags')
        homog_db = homog_db[homog_db['id_trader'] == self.ID]
        products_db = load('products')
        products_db = products_db[products_db['id_trader'] == self.ID]
        info_luce_db = load('util_luce_info')
        info_gas_db = load('util_gas_info')

        if download_cg is False:  # Set download_cg to True to download CG
            links_db = links_db[links_db['tipo_info'] != 'CG']

        if self.PDF_BROWSER:
            b = get_browser()
            b.save_screenshot("document.png")

        # Download / Scrape
        new_dl = []
        idprod_to_ftv = {}
        idprod_to_ttc = {}
        idprod_to_tags = {}
        now = dt.datetime.now() if self.date is None else self.date
        for _, r in links_db.iterrows():
            print('Scraping '+str(r['id']))
            defs = products_db[products_db['id'] == r['id_product']].iloc[0]
            homog = homog_db[homog_db['id_link'] == r['id']]
            url = r['description_link']
            if url == '' or url == ' ':
                continue
            title = (r['part_title_file'].replace(f'_{self.NAME}_LUCE_', '')
                     .replace(f'_{self.NAME}_GAS_', '')
                     .replace('_LUCE_RES', '').replace('_GAS_RES', '')
                     .replace('_CTE-SC-CG','').replace('_CTE-SC', '').replace('_CG', '')
                     .replace('_SC', '').replace('_CTE', '')
                     .replace('_RES', '').replace(f'_{self.NAME}_', ''))
            address = (f'{self.defs["path_files"]}/FILES/'
                       f'{"LUCE" if "LUCE" in r["part_title_file"] else "GAS"}'
                       f'/{title}/').replace('_&', '')
            file = f'SCD{r["part_title_file"]}_{now.strftime("%Y-%m-%d")}.pdf'
            fp = address + file
            new_dl.append(
                [self.ID, r['id'], self.URL.replace('http://', '')[:-1],
                 now.year, now.month, now.day, address, file])

            # Makes directories if they don't exist
            path = '/'
            for folder in address.split('/'):
                if folder == '':
                    continue
                path += folder + '/'
                stdin, stdout, stderr = client.exec_command(
                    f'if test -d {path}; then echo 1; else echo 0; fi')
                if int(stdout.readline()[0]) == 0:
                    stdin, stdout, stderr = client.exec_command(
                        f'mkdir {path}')


            # Download PDF
            if self.PDF_BROWSER:
                pdf, fn = self._get_pdf(b, url)
                
                if pdf is None:
                    print("PDF Download Failed. Skipping.")
                    continue
                _pdf = pdf
            else:
                pdf = self._get_pdf(url)

            if pdf is not None:
                ftp = client.open_sftp()
                ftp.putfo(pdf, fp)
                pdf.seek(0)

            
            if len(homog) == 0:  # Stop here if no tag mappings
                continue
            

            # Extract text from PDF
            if self.IMAGES:
                print("estrazione")
                images = pdf2image.convert_from_bytes(pdf.read())
            try:
                pdf = pdfplumber.open(pdf)
            except:
                continue
            textR = ''
            textC = ''
            textI = None
            for pg in pdf.pages:
                pag = pg
                txt = pg.extract_text(x_tolerance=1)
                if txt:
                    textR += txt
                w = float(pg.width)
                h = float(pg.height)
                #print(f"Num. Pages: {pg}")
                rest = 0
                for split in self.SLICES:
                    #print(f"ANCHO: {w} --> {w-12.019}")
                    #print(f"ALTO: {h}")
                    
                    #if str(pag).find('4')>0:
                        #print("ESTOY EN 1")
                        #txt = pg.crop((12.019, 13.000, w*split, h*split)).extract_text()
                    #else:
                        #print("ESTOY EN 2")
                    txt = pg.crop((0, 0, w*split, h)).extract_text()
                    
                    rest += split
                    if txt:
                        textC += txt
                # txt = pg.crop((0, 0, w*.5, h)).extract_text()
                # if txt:
                #     textC += txt
                txt = pg.crop((w*rest, 0, w, h)).extract_text()
                if txt:
                    textC += txt
            if self.PDF_BROWSER:
                pdf.close()
                os.remove(pdf)
            pdf.close()

            if self.IMAGES:
                textI = ''
                for img in images:
                    textI += pytesseract.image_to_string(img)

            # Extract values from text + search tags
            typ = defs['type_product']
            F = 'C' if typ == 5 else 'D'
            name = defs['nome_intern_product'].replace('_', ' ').title()
            ftv = {'fetching_date': now.strftime("%Y-%m-%d"),
                   'id_product': r['id_product'],
                   'TP': str(typ),
                   f'{F}1': self.defs['name_trader'],
                   f'{F}2': name}
            ttc = pd.Series(homog['codice_xls'].values,
                            index=homog['id_search_tag'].values)
            tags = tags_db[tags_db['id_link'] == r['id']]
            for _, tag in tags.iterrows():
                try:
                    val = self._pdf_extract(
                        tag['description_tag'], textR, textC, textI)
                    for x in ttc[ttc.index == tag['id']].values:
                        ftv[x] = val
                except ValueError as err:
                    for x in ttc[ttc.index == tag['id']].values:
                        ftv[x] = None
                        self.errors.append({'id_link': r['id'],
                                            'id_tag': tag['id'],
                                            'error': str(err)})
            matches = len([x for x in ftv.values() if
                           x != '' and x is not None]) - 5
            print(f'Matched {matches} Tags')

            if defs['id'] in idprod_to_ftv:
                idprod_to_ftv[defs['id']].update(
                    {k: v for k, v in ftv.items() if v is not None})
                idprod_to_ttc[defs['id']] = (
                    idprod_to_ttc[defs['id']].append(ttc))
                idprod_to_tags[defs['id']] = (
                    idprod_to_tags[defs['id']].append(tags, ignore_index=True))
            else:
                idprod_to_ftv[defs['id']] = ftv
                idprod_to_ttc[defs['id']] = ttc
                idprod_to_tags[defs['id']] = tags
            
            #print(idprod_to_ftv)
            #print(idprod_to_ttc)
            #print(idprod_to_tags)


        # DB Interactions
        diff_entries = []
        diff_types = []
        
        for idprod, ftv in idprod_to_ftv.items():
            print(f'Writing Product {idprod}...', end='')
            defs = products_db[products_db['id'] == idprod].iloc[0]
            ttc = idprod_to_ttc[idprod]
            ctt = {v: k for k, v in ttc.items()}

            # Write Values
            tbl = ('util_luce_info' if defs['type_product'] == 5 else
                   'util_gas_info')
            while True:
                try:
                    write(tbl, [[*ftv.values()]], [*ftv])
                    break
                except DataError as err:
                    s = err.args[1].find('column ') + 8
                    e = err.args[1].find(' at row') - 1
                    col = err.args[1][s:e]
                    id_tag = (ctt[col] if col in ctt else
                              ttc[ttc == 'C14'].index[0])
                    self.errors.append({'id_link': idprod,
                                        'id_tag': id_tag,
                                        'error': str(err.args[1])})
                    ftv.pop(col)
            print(f' {len(ftv)} Values')

            # Compare
            if defs['type_product'] == 6:
                prior = info_gas_db[info_gas_db['id_product'] == idprod
                                    ].sort_values('fetching_date')
            else:
                prior = info_luce_db[info_luce_db['id_product'] == idprod
                                     ].sort_values('fetching_date')
            if len(prior) > 1:
                both = prior.iloc[-1:]
                both = both.append(ftv, ignore_index=True)
                prior = both.iloc[0]
                new = both.iloc[1]
                mask = (~new.isnull() & ~prior.isnull() & (prior != new))
                prior = prior[mask]
                new = new[mask]
                tags = idprod_to_tags[idprod]
                for c, v in new.items():
                    if c in ('fetching_date', 'C1', 'C2', 'D1', 'D2'):
                        continue
                    t = tags.set_index('id').loc[ctt[c]]
                    e = [self.ID, self.URL, ftv['fetching_date'], ctt[c],
                         t['description_tag'], prior[c], None,
                         file.replace(
                             new['fetching_date'],
                             prior['fetching_date'].strftime('%Y-%m-%d')),
                         v, None, file, 1]
                    diff_entries.append(e)
                    diff_types.append(typ)

        if self.PDF_BROWSER:
            b.close()

        if len(new_dl) > 0:
            write('downloaded_files', new_dl,
                  load('downloaded_files').columns[1:])
        if len(diff_entries) > 0:
            self._update_diffs(diff_entries, diff_types)

    '''
    def _get_pdf(self, url):
        response = requests.get(url)
        pdf = BytesIO(response.content)
        return pdf
    '''
    def _get_pdf(self, url):
        if url==" ":
            pdf = None
        else:
            response = requests.get(url)
            pdf = BytesIO(response.content)
        return pdf

    def _update_diffs(self, diff_entries, diff_types):
        dl_db = load('downloaded_files')
        dl_db = dl_db[dl_db['id_trader'] == self.ID]
        fti = pd.Series(dl_db['id'].values, index=dl_db['file_name'].values
                        ).to_dict()
        fields = load('trader_productGas_diff_file').columns[1:]
        luce = []
        gas = []
        for e, t in zip(diff_entries, diff_types):
            if e[7] in fti:
                e[6] = fti[e[7]]
            else:
                e[6] = 0
            e[9] = fti[e[10]]
            if t == 5:
                luce.append(e)
            else:
                gas.append(e)
        if len(luce) > 0:
            write('trader_productLuce_diff_file', luce, fields)
        if len(gas) > 0:
            write('trader_productGas_diff_file', gas, fields)

    def _pdf_extract(self, search_tag, textR, textC, textI=None):
        '''
        Rules for search_tag string:

            1. Place {p} where the VALUE is relative to the search tag. Keep
               blank spaces and case in mind!  IF {p} is not provided, scraper
               will assume tag is BEFORE the VALUE with a space in between.

                Ex1) 'componente Energia valido per {p}' will return the word
                     that comes AFTER 'componente Energia valido per '.
                Ex2) '{p} la polizza casa' will return the word that comes
                     BEFORE ' la polizza casa'.
                Ex3) 'Opzione {p}aria' will return the word that comes AFTER
                     'Opzione ' AND BEFORE 'aria'.
                Ex4) 'componente Energia valido per' will return the word
                     that comes AFTER 'componente Energia valido per '.


            2. Place the number of words (terms separated by blank spaces)
               before {p}, e.g. {2p}.  IF a number is not provided, scraper
               will assume VALUE is 1 word.

                Ex1) "l'offerta {2p} elettrica" will return TWO WORDS between
                     "l'offerta" and "elettrica".
                Ex2) 'offre in {4p}' will return FOUR WORDS after 'offre in'

            3. If there is more than one result, you can include an occurrence
               number at the end of the search tag in the form {#n}, where n
               is the occurrence number you are looking for.

                Ex1) The PDF includes two occurrences of 'Opzione {p}aria':
                     'Opzione Monoraria' and 'Opzione Bioraria'. You want the
                     2nd, so you use the tag 'Opzione {p}aria{#2}'.

            4. If the page has two columns AND the search tag exists in
               the one of the columns, include {C} at the end of the tag.

            5. If the desired value only includes certain words extracted from
               the tag, you can specify them with the index feature, {@S:E}.
               Replace 'S' with the index of the 1st word you want to return,
               and replace 'E' with the index of the last word.

               Ex 1) If you search for 'Bob says hello to {4p}{@3:4}', and the
                     PDF includes the text:
                         'Bob says hello to James and Peter Smith'
                     the value will be returned as "Peter Smith".

        '''

        if '{C}' in search_tag:
            text = str(textC)
            search_tag = search_tag.replace('{C}', '')
        else:
            text = str(textR)

        text = text.replace('’', "'")  # replaces different apostrophe char
        search_tag = search_tag.replace('’', "'")
        text = text.replace('\n', " ")  # replaces \n with space
        text = re.sub(' +', ' ', text)

        if textI:
            textI = textI.replace('’', "'")
            search_tag = search_tag.replace('’', "'")
            textI = textI.replace('\n', " ")
            textI = re.sub(' +', ' ', textI)

        if 'p}' not in search_tag:
            search_tag += ' {p}'
        if search_tag[search_tag.index('p}')-1] == '{':
            search_tag = search_tag.replace('{p}', '{1p}')
        if '{#' not in search_tag:
            occurrence = 1
        else:
            s = search_tag.index('{#')+2
            e = search_tag.index('}', s)
            occurrence = int(search_tag[s:e])
            search_tag = search_tag.replace('{#' + str(occurrence) + '}', '')
        if '{@' not in search_tag:
            index = None
        else:
            s = search_tag.index('{@')+2
            e = search_tag.index('}', s)
            replace = search_tag[s:e]
            index = [int(x) for x in replace.split(':')]
            search_tag = search_tag.replace('{@' + replace + '}', '')

        s = search_tag[::-1].index('}p')
        e = search_tag[::-1].index('{', s)
        ct_words = int(search_tag[::-1][s+2:e][::-1])
        split = search_tag.split('{' + str(ct_words) + 'p}')
        tagB = split[0]
        tagA = split[1]

        try:
            s = text.index(tagB) + len(tagB) if tagB != '' else None
            e = text.index(tagA, s) if tagA != '' else None
            occ = 1
            if all([s, e]):
                while True:
                    if (len(text[s:e].split(' ')) == ct_words and
                            occ == occurrence):
                        break
                    else:
                        _s = text.index(tagB, s+1) + len(tagB)
                        if _s < e:
                            s = _s
                            continue
                        s = text.index(tagB, e) + len(tagB)
                        e = text.index(tagA, s)
                        occ += 1
                value = ' '.join(text[s:e].split(' ')[:ct_words])
            elif s:
                while occ != occurrence:
                    s = text.index(tagB, s) + len(tagB)
                    occ += 1
                value = ' '.join(text[s:].split(' ')[:ct_words])
            else:
                while occ != occurrence:
                    e = text.index(tagA, e+1)
                    occ += 1
                value = ' '.join(text[:e].split(' ')[-ct_words:])
        except ValueError as err:
            if textI:
                s = textI.index(tagB) + len(tagB) if tagB != '' else None
                e = textI.index(tagA, s) if tagA != '' else None
                occ = 1
                if all([s, e]):
                    while True:
                        if (len(textI[s:e].split(' ')) == ct_words and
                                occ == occurrence):
                            break
                        else:
                            _s = textI.index(tagB, s+1) + len(tagB)
                            if _s < e:
                                s = _s
                                continue
                            s = textI.index(tagB, e) + len(tagB)
                            e = textI.index(tagA, s)
                            occ += 1
                    value = ' '.join(textI[s:e].split(' ')[:ct_words])
                elif s:
                    while occ != occurrence:
                        s = textI.index(tagB, s) + len(tagB)
                        occ += 1
                    value = ' '.join(textI[s:].split(' ')[:ct_words])
                else:
                    while occ != occurrence:
                        e = textI.index(tagA, e+1)
                        occ += 1
                    value = ' '.join(textI[:e].split(' ')[-ct_words:])
            else:
                raise err

        if index is not None:
            vals = value.split(' ')
            s = index[0] - 1
            e = None if index[1] == len(vals) else index[1]
            value = ' '.join(vals[s:e])

        # Remove ending punctuation
        if len(value) > 0 and value[-1] in ['.', ',', ';', '!', '?', '-']:
            value = value[:-1]

        return value
