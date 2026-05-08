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

        rand_sleep(3, 5, 7)
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
            rand_sleep(3, 10, 14)
            soup = BS(b.page_source,'html.parser')
            links = [_ for _ in soup.find_all('li') if 'Condizioni Economiche' in _.text]
            for _ in links:
                print(data[1])
                if "miaSerena GAS" in data[1]:
                    prdts.append([data[0],data[1],data[2],_.a['href']])
                elif data[0]==1:
                    if "miaConvenienza" not in data[1]:
                        prdts.append([data[0],_.text.split(' -' )[-1].strip().replace("+", " PLUS").replace('Monoraria','MONO').replace('Multioraria','BIO'),data[2],_.a['href']])
                    else:
                        if 'luce' in _.text.lower():
                            prdts.append([data[0],_.text.split(' -' )[-1].strip().replace("+", " PLUS").replace('Monoraria','MONO').replace('Multioraria','BIO'),data[2], data[2]+_.a['href']])
                else:
                    if "miaConvenienza" not in data[1]:
                        prdts.append([data[0],_.text.split(' -' )[-1].strip().replace("+", " PLUS"),data[2],_.a['href']])
                    else:
                        if 'gas' in _.text.lower():
                            prdts.append([data[0],_.text.split(' -' )[-1].strip().replace("+", " PLUS"),data[2], data[2]+_.a['href']])
        
        



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
    
    def _get_pdfV2(self, products, b):
        import certifi
        from urllib.request import Request, urlopen
        import shutil
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
        
        now = dt.datetime.now().strftime("%Y-%m-%d")
        
        directory = ""
        
        for prds in products:
            url = prds[3]
            print(f"PRODOTTO: {prds[2]}\n")
            print(f"LINK: {prds[3]}\n")
            req = Request(prds[3], headers={'User-Agent': 'Mozilla/5.0'})
            webpage = urlopen(req, timeout=15).read()

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

    

