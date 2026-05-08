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
    prec = "{:." + str(precision) + "f}"
    timer = float(prec.format(random.uniform(min, max)))
    time.sleep(timer)
        
class WINDTRE(Trader):
    NAME = 'WINDTRE'
    ID = 29
    URL = 'https://www.windtre.it/offerte-windtre-luce-gas/'
    DOCTYPES = ['SCHEDA', 'CTE', 'CG']
    

    def get_products(self):
        b = get_browser()
        b.get(self.URL)
        rand_sleep(2, 3, 4)
        link = 'https://www.windtre.it/offerte-windtre-luce-gas/'
        products = []

        try:
            b.find_element(By.XPATH, "//button[@id='btn-cb btn-cb-primary rounded-pill text-uppercase accettatutti']").click()
            print('Cookie accettati.')
        except:
            print('Cookie window not found.')
        rand_sleep(3, 1, 2)

        i = 1
        b.find_element(By.XPATH, f"//div[@id='text-3e165586d3']//ul[3]")

        while True:
            try:
                b.find_element(By.XPATH, f"(//div[@id='text-3e165586d3'])//ul[3]//li[{i}]//a[contains(text(), 'Condizioni Economiche')]")
                i += 1
            except:
                break
        tries = 0
        i-=1
        for n in range(i):
            
            title = None
            print(n+1)
            try:
                title = b.find_element(By.XPATH, f"(//div[@id='text-3e165586d3'])//ul[3]//li[{n+1}]//a[contains(text(), 'Condizioni Economiche')]").get_attribute('textContent')
            except:
                tries += 1
                if tries > 3:
                    print(f'{n+1} Something wrong with title of offer: line 20')
                continue
            title = title.replace('Condizioni Economiche ', '')
            title = title.replace('documento', '')
            titolo = title.replace('&', ' ')
            titolo = titolo.replace('WINDTRE LUCE GAS', '')
            titolo = titolo.strip()
            title= title.strip()
            print(title)
            if 'Placet' not in title and title !='' and 'PRO' not in title:
                products.append([1, titolo+' Luce', link])
                products.append([2, titolo+' Gas', link])
        
        documento = ' - documento scaricabile'
        for p in products:
            b.get(p[2])
            documento = ' - documento scaricabile'
            rand_sleep(3, 3, 5)
            WebDriverWait(b, 10)
            rand_sleep(2, 1, 2)
                
            if p[0] == 1:
                title = title.replace(' Luce', '')
                p.append(b.find_element(By.XPATH, f"(//div[@id='text-3e165586d3'])//ul[3]//a[@title= 'Scheda sintetica Luce offerta {title}{documento}']").get_attribute('href'))
                p.append(b.find_element(By.XPATH, f"(//div[@id='text-3e165586d3'])//ul[3]//a[@title= 'Condizioni Economiche {title}{documento}']").get_attribute('href'))
                p.append(b.find_element(By.XPATH, f"(//div[@id='text-3e165586d3'])//ul[4]//a[@title= 'Condizioni Generale Contratto- documento scaricabile']").get_attribute('href'))
            else:
                title = title.replace(' Gas', '')
                p.append(b.find_element(By.XPATH, f"(//div[@id='text-3e165586d3'])//ul[3]//a[@title= 'Scheda sintetica Gas offerta {title}{documento}']").get_attribute('href'))
                p.append(b.find_element(By.XPATH, f"(//div[@id='text-3e165586d3'])//ul[3]//a[@title= 'Condizioni Economiche {title}{documento}']").get_attribute('href'))
                p.append(b.find_element(By.XPATH, f"(//div[@id='text-3e165586d3'])//ul[4]//a[@title= 'Condizioni Generale Contratto- documento scaricabile']").get_attribute('href'))
    
        products = self.products = self._get_pdf_links(products, b)
        print(products)
        #b.close()
        return products


    def _get_pdf_links(self, products, browser):
        b = browser
        products = self.products = self._get_pdfV2(products, b)    
        return products
    
    def _get_pdfV2(self, products, b):
        #import certifi
        #from urllib.request import Request, urlopen
        import shutil
        #import ssl
        #ssl._create_default_https_context = ssl._create_unverified_context
        desc_url = []
        now = dt.datetime.now().strftime("%Y-%m-%d")
        
        directory = ""
        
        for prds in products:
            url = prds[3]
            print(url)
            #req = Request(prds[3], headers={'User-Agent': 'Mozilla/5.0'})
            #webpage = urlopen(req, timeout=10).read()
            for x in range(3,6):
                b.get(prds[x])
                rand_sleep(3, 4, 6)
                #print(webpage)
                
                if prds[0]==1: 
                    pr = 'LUCE' 
                else: 
                    pr = 'GAS'
                
                directory = ((prds[1].upper()).replace(pr,'')).replace('  ',' ')
                #print(directory)
                directory = directory.strip()
                directory = directory.replace(' ','_')
                
                path = f"/fin_ser/UTILITIES_files/{self.NAME}/FILES/{pr}/{directory}"
                
                if "SCHEDA" in prds[x]:
                    new_file_name = f"SCD_{self.NAME}_{pr}_{directory}_RES_SC_{now}.pdf"
                elif "CONDIZIONI-ECONOMICHE" in prds[x]:
                    new_file_name = f"SCD_{self.NAME}_{pr}_{directory}_RES_{now}.pdf"
                elif "CONDIZIONI_GENERALI" in prds[x]:
                    new_file_name = f"SCD_{self.NAME}_{pr}_{directory}_RES_CG_{now}.pdf"
                
                desc_url = str(prds[x]).split('/')
                for dx in desc_url:
                    if ".pdf" in dx:
                        name_file = dx
                #with open('file.pdf', "wb") as f:
                #    f.write(webpage)
                
                if not os.path.exists(path):
                    os.makedirs(path)  
                
                rand_sleep(3, 4, 5)
                
                try:
                    shutil.move(f'{os.getcwd()}/{name_file}', f'{path}/{new_file_name}')
                except FileExistsError:
                    os.remove(f'{path}/{new_file_name}')
                    shutil.move(f'{os.getcwd()}/{name_file}', f'{path}/{new_file_name}')
                os.chown(f'{path}/{new_file_name}', 1003, 1004)
            
                rand_sleep(3, 2, 4)
        return products
