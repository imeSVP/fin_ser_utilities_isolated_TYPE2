import cgitb
from trader import *
from bs4 import BeautifulSoup as BS
from time import sleep

def rand_sleep(precision, min, max):
    '''
    rand_sleep takes (precision, min, max) where:\n
    precision ->   number of decimals after the .\n
    min-max ->     range of min-max values to generate a random number
    '''
    prec = "{:." + str(precision) + "f}"
    random_float = float(prec.format(random.uniform(min, max)))
    time.sleep(random_float)

class WEKIWI(Trader):
    NAME = 'WEKIWI'
    ID = 20
    URL = 'https://www.wekiwi.it/documenti-e-moduli/'
    DOCTYPES = ['SCHEDA+CTE', 'CG']
    #PDF_BROWSER = True


    def get_products(self):
        b = get_browser()
        b.maximize_window()
        b.get(self.URL)
        WebDriverWait(b, 10)
        rand_sleep(3, 2, 3)
        try:
            e = WebDriverWait(b, 10).until(EC.element_to_be_clickable(
                (By.XPATH, "//div[@class='cmplz-buttons']//button[contains(text(), 'Accetta')]")))
            e.click()
            print('Cookie accettato')
        except TimeoutException:
            print('Accetta i Cookie non trovato')
            pass
        URL = 'https://www.wekiwi.it/documenti-e-moduli/'

        # Variables
        products = []

        cg = b.find_element(By.XPATH, "//div[@class='elementor-widget-container']//a[contains(@href, 'Condizioni-generali')]").get_attribute('href')

        link_1 = b.find_element(By.XPATH, "//div[@class='elementor-widget-container']//a[contains(@href, 'DOM-CR')]").get_attribute('href')
        prod_1 = [1, "Energia Alla Fonte", URL, link_1, cg ]
        

        link_2 = b.find_element(By.XPATH, "//div[@class='elementor-widget-container']//a[contains(@href, 'GAS-VAR-12-DOM-CR')]").get_attribute('href')
        prod_2 = [2, "Energia Alla Fonte", URL, link_2, cg ]
        
        products = [prod_1, prod_2]
        print(products)
        #self.products= products
        
        products = self.products = self._get_pdfV2(products, b)

        return products
    
    
    def _get_pdfV2(self, products, b):
        from urllib.request import Request, urlopen
        import shutil
        now = dt.datetime.now().strftime("%Y-%m-%d")
        for prds in products:
            url = prds[3]
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            webpage = urlopen(req, timeout=10).read()

            #print(webpage)
            if prds[0]==1: 
                pr = 'LUCE' 
            else: 
                pr = 'GAS'
            
            path = f"/fin_ser/UTILITIES_files/WEKIWI/FILES/{pr}/{(prds[1].replace(' ','_')).upper()}/"
            new_file_name = f"SCD_WEKIWI_{pr}_{(prds[1].replace(' ','_')).upper()}_RES_CTE-SC_{now}.pdf"
            with open('file_wekiwi.pdf', "wb") as f:
                f.write(webpage)

            time.sleep(3)                
            try:
                shutil.copy(f'{os.getcwd()}/file_wekiwi.pdf', f'{path}/{new_file_name}')
            except FileExistsError:
                os.remove(f'{path}/{new_file_name}')
                shutil.copy(f'{os.getcwd()}/file_wekiwi.pdf', f'{path}/{new_file_name}')
            os.chown(f'{path}/{new_file_name}', 1003, 1004)
            time.sleep(4)
        
        os.remove(f'{os.getcwd()}/file_wekiwi.pdf')        
        return products
         
