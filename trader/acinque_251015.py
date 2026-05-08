from pickle import FALSE
from numpy import append, in1d
from trader import *
from bs4 import BeautifulSoup as BS
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


def rand_sleep(precision, min, max):
    '''
    rand_sleep takes (precision, min, max) where:\n
    precision ->   number of decimals after the .\n
    min-max ->     range of min-max values to generate a random number
    '''
    prec = "{:." + str(precision) + "f}"
    random_float = float(prec.format(random.uniform(min, max)))
    time.sleep(random_float)
    
def parse_txt(text):
    if 'PLACET' in text or 'placet' in text or 'Placet' in text:
        return None
    if len(text) > 22:
        return None
    if text:
        parsed_txt = ''
        parsed_txt = text.strip()
        if '+' in text:
            parsed_txt = text.replace('+', ' plus')
        return parsed_txt
    return None

class ACINQUE(Trader):
    NAME = 'ACINQUE'
    ID = 32
    URL = 'https://acinque.it/'
    DOCTYPES = ['SCHEDA+CTE']
    IMAGES=False

    
    def get_products(self):
        b = get_browser()
        b.get('https://acinque.it/luce-gas-e-servizi/casa/offerte.html')
        try:
            b.find_elements(By.XPATH,"//*[contains(text(), 'Accetta tutti')]")[-1].click()
        except:
            pass

        rand_sleep(3, 10, 15)
        soup = BS(b.page_source,'html.parser')
        all = soup.find_all('div',{'class':'title-box'})
        final = []
        for _ in all:
            if _.parent.find('a',string="Scopri l'offerta") != None:
                link_0 = 'https://acinque.it'+ _.parent.find('a',string="Scopri l'offerta")['href']
                title = _.text.strip()
                title = title.replace("  "," ")
                if 'LUCE' in title:
                    final.append([1,title, link_0])
                if 'GAS' in title:
                    final.append([2,title, link_0])
        
        # final.append([1,'miaConvenienza LUCE', 'https://acinque.it/miaconvenienza/'])
        # final.append([2,'miaConvenienza GAS', 'https://acinque.it/miaconvenienza/'])
        
        #print("VEDENDO FINAL")            
        print(final)
        #print("\n\n")
        prdts = []
        products = []
        for data in final:
            b.get(data[2])
            rand_sleep(3, 13, 17)
            soup = BS(b.page_source,'html.parser')
            links = [_ for _ in soup.find_all('li') if 'Condizioni Economiche' in _.text]
            for _ in links:
                print(data[1])
                if "miaSerena GAS" in data[1]:
                    prdts.append([data[0],data[1],data[2],_.a['href']])
                elif data[0]==1:
                    if "mia-convenienza" in data[2]:
                        prdts.append([data[0],'miaConvenienza LUCE',data[2],_.a['href']])
                    elif "mia-occasione" in data[2]:
                        prdts.append([data[0],'miaOccasione LUCE',data[2],_.a['href']])
                    elif "mia-certezza" in data[2]:
                        prdts.append([data[0],'miaCertezza LUCE',data[2],_.a['href']])
                    else:
                        # if 'luce' in _.text.lower():
                        #     prdts.append([data[0],_.text.split(' -' )[-1].strip().replace("+", " PLUS").replace('Monoraria','MONO').replace('Multioraria','BIO'),data[2], data[2]+_.a['href']])
                        prdts.append([data[0],_.text.split(' -' )[-1].strip().replace("+", " PLUS").replace('Monoraria','MONO').replace('Multioraria','BIO'),data[2],_.a['href']])
                else:
                    if "mia-convenienza" in data[2]:
                        prdts.append([data[0],'miaConvenienza GAS',data[2],_.a['href']])
                    elif "mia-occasione" in data[2]:
                        prdts.append([data[0],'miaOccasione GAS',data[2],_.a['href']])
                    elif "mia-certezza" in data[2]:
                        prdts.append([data[0],'miaCertezza GAS',data[2],_.a['href']])
                    else:
                        # if 'gas' in _.text.lower():
                        #     prdts.append([data[0],_.text.split(' -' )[-1].strip().replace("+", " PLUS"),data[2], data[2]+_.a['href']])
                        prdts.append([data[0],_.text.split(' -' )[-1].strip().replace("+", " PLUS"),data[2],_.a['href']])
        
        



        print("VEDENDO PRDTS:")            
        print(prdts)
        print("\n\n")
        # unique_data = []    
        # for row in prdts:
        #     if row not in unique_data:
        #         unique_data.append(row)
                
         
        products = prdts
        # print(products)
        products = self.products = self._get_pdf_links(products, b)
        print("\n\n")
        print(products)
        
        return products
                

    def _get_pdf_links(self, products, browser):
        b = browser
        products = self.products = self._get_pdfV2(products, b)    
        return products
    
    '''
    def _get_pdfV2(self, products, b):
        import certifi
        from urllib.request import Request, urlopen, ProxyHandler, build_opener, install_opener
        import shutil
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
        
        now = dt.datetime.now().strftime("%Y-%m-%d")

        directory = ""
        
        for prds in products:
            url = prds[3]
            # if "miaconvenienza" in str(prds[1]).lower():
            #     print(f"\n\nPRODOTTO: {prds[2]}\n")
            #     print(f"LINK: {prds[3]} \n")
            #     prds[3] = str(prds[3]).replace(prds[2],"")
            #     print(f"LINK MODIFICATO: {prds[3]} \n")
                
            # else: 
            PORTS = [*range(20001, 30000)]  
            port = np.random.choice(PORTS) 

            proxy_url = f"http://svilupp01:Sv1luPp02045@it-pr.oxylabs.io:{port}"  # inserisci credenziali reali

            proxies = {
                "http": proxy_url,
                "https": proxy_url
            }

            proxy_handler = ProxyHandler(proxies)
            opener = build_opener(proxy_handler)
            install_opener(opener)

            print(f"\n\nPRODOTTO: {prds[2]}\n")
            print(f"LINK: {prds[3]}\n")
            USER_AGENTS = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/112.0",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.5563.146 Safari/537.36'
            ]

            U_AGENT = random.choice(USER_AGENTS)

            req = Request(prds[3], headers={'User-Agent': U_AGENT})
            randpause(4.5, 2)
            webpage = urlopen(req, timeout=60).read()

            print("WEBPAGE ")
            # print(webpage)
            if prds[0]==1: 
                pr = 'LUCE' 
            else: 
                pr = 'GAS'
            
            directory = ((prds[1].upper()).replace(pr,'')).replace('  ',' ')
            #print(directory)
            directory = directory.strip()
            directory = directory.replace(' ','_')
            
            path = f"/fin_ser/UTILITIES_files/{self.NAME}/FILES/{pr}/{directory}"
            new_file_name = f"SCD_{self.NAME}_{pr}_{directory}_RES_CTE-SC_{now}.pdf"
            with open('file.pdf', "wb") as f:
                f.write(webpage)
            
            if not os.path.exists(path):
                os.makedirs(path)  
            
            try:
                shutil.move(f'{os.getcwd()}/file.pdf', f'{path}/{new_file_name}')
            except FileExistsError:
                os.remove(f'{path}/{new_file_name}')
                shutil.move(f'{os.getcwd()}/file.pdf', f'{path}/{new_file_name}')
            os.chown(f'{path}/{new_file_name}', 1003, 1004)
                
        return products
    '''

    def _get_pdfV2(self, products, b):
        import os
        import shutil
        import datetime as dt
        import requests
        import random

        now = dt.datetime.now().strftime("%Y-%m-%d")

        USER_AGENTS = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/112.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.5563.146 Safari/537.36"
        ]

        OXYLABS_USER = 'svilupp01'  # <-- Inserisci qui le credenziali vere
        OXYLABS_PASS = 'Sv1luPp02045'

        for prds in products:
            url = prds[3]
            U_AGENT = random.choice(USER_AGENTS)
            headers = {'User-Agent': U_AGENT}

            # Proxy Oxylabs con porta casuale
            PORTS = list(range(20001, 30000))
            port = np.random.choice(PORTS)

            proxy_url = f"http://{OXYLABS_USER}:{OXYLABS_PASS}@it-pr.oxylabs.io:{port}"
            proxies = {
                "http": proxy_url,
                "https": proxy_url
            }

            print(f"\n\nPRODOTTO: {prds[2]}")
            print(f"LINK: {url}")

            # Ritardo anti-ban
            rand_sleep(3,3.5,7.5)

            try:
                response = requests.get(url, headers=headers, proxies=proxies, timeout=60, verify=False)

                if response.status_code != 200:
                    print(f"[ERRORE] Status code {response.status_code} per {url}")
                    continue

                # Determina tipo prodotto
                pr = 'LUCE' if prds[0] == 1 else 'GAS'

                # Prepara directory
                directory = ((prds[1].upper()).replace(pr, '')).replace('  ', ' ').strip().replace(' ', '_')
                path = f"/fin_ser/UTILITIES_files/{self.NAME}/FILES/{pr}/{directory}"
                new_file_name = f"SCD_{self.NAME}_{pr}_{directory}_RES_CTE-SC_{now}.pdf"

                if not os.path.exists(path):
                    os.makedirs(path)

                # Scrive il PDF
                with open('file.pdf', 'wb') as f:
                    f.write(response.content)

                # Sposta il file
                dest_path = os.path.join(path, new_file_name)
                if os.path.exists(dest_path):
                    os.remove(dest_path)
                shutil.move('file.pdf', dest_path)

                # Imposta permessi (facoltativo: dipende dal sistema)
                os.chown(dest_path, 1003, 1004)

            except requests.exceptions.RequestException as e:
                print(f"[EXCEPTION] Errore durante il download da {url}:\n{e}")
                continue

        return products

    

