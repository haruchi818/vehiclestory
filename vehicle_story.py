import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import os

# 
# vreg - vehicle registration number
# vreg_date - vehicle 1st registration date
# vvin - vehicle vin
# 
#

class VehicleStory:
    def __init__(self,vreg,vreg_date,vvin,page_url):
        self.url=page_url
        self.vreg=vreg
        self.vreg_date=vreg_date
        self.vvin=vvin
    def init_browser(self):
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
        chromeOptions = webdriver.ChromeOptions()
        chrome_binary_path = "/chrome-linux/chrome"
        chromeOptions.binary_location = chrome_binary_path
        chromeOptions.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2}) 
        chromeOptions.add_argument("--no-sandbox") 
        chromeOptions.add_argument("--window-size=1920,1080")
        chromeOptions.add_argument("--disable-setuid-sandbox") 
        chromeOptions.add_argument("--remote-debugging-port=9222")  # this
        chromeOptions.add_argument("--disable-dev-shm-using") 
        chromeOptions.add_argument("--disable-extensions") 
        chromeOptions.add_argument("--disable-gpu") 
        chromeOptions.add_argument('--disable-dev-shm-usage')
        chromeOptions.add_argument("start-maximized") 
        chromeOptions.add_argument("disable-infobars")
        chromeOptions.add_argument(f"user-data-dir=.//")
        chromeOptions.add_argument(f'--user-agent={user_agent}')
        chromeOptions.add_argument(r"user-data-dir=.\cookies\\test") 
        chromeOptions.add_argument('ignore-certificate-errors')
        self.browser=webdriver.Chrome(chrome_options=chromeOptions)
    def get_vehicle_story(self):
        self.browser.get(self.url)
        self.browser.find_element(By.CLASS_NAME, 'rej').send_keys(self.vreg)
        self.browser.find_element(By.CLASS_NAME, 'vin').send_keys(self.vvin)
        vreg_data_element=self.browser.find_element(By.ID, '_historiapojazduportlet_WAR_historiapojazduportlet_:data')
        self.browser.execute_script(f'document.getElementById("_historiapojazduportlet_WAR_historiapojazduportlet_:data").value="{self.vreg_date}"',vreg_data_element)
        self.browser.find_element(By.ID, '_historiapojazduportlet_WAR_historiapojazduportlet_:btnSprawdz').click()
        self.get_vehicle_basic_data()
        self.get_table("timeline")
        self.get_vehicle_information()
        self.get_vehicle_foreign_data()      
    def get_table(self,table_id):
        soup = BeautifulSoup(self.browser.page_source, 'html.parser')
        table = soup.find('table', attrs={'id': table_id})
        headers = [th.text for th in table.find_all('th')]
        rows = table.find_all('tr')
        data = [[td.text for td in row.find_all('td')] for row in rows[1:]]
        self.vtimeline_df = pd.DataFrame(data, columns=headers)
        self.vtimeline = self.vtimeline_df.to_dict(orient='records')
    def get_vehicle_basic_data(self):
        self.basic_data=self.browser.find_element(By.ID, 'dane-podstawowe').text
    def get_vehicle_foreign_data(self):
        self.foreign_data=self.browser.find_element(By.CLASS_NAME, 'box-dane-zagraniczne').text        
    def get_vehicle_information(self):
        self.information=self.browser.find_element(By.CLASS_NAME, 'box-information').text

def main(rej,rej_date,vin):
    page_url = os.environ["PAGE_URL"]
    vstory=VehicleStory(rej,rej_date,vin,page_url)
    vstory.init_browser()
    vstory.get_vehicle_story()
    return {
        "basic_data":vstory.basic_data,
        "foreign_data": vstory.foreign_data,
        "information": vstory.information,
        "timeline": vstory.vtimeline
    }






from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route('/', methods=['POST'])
def vehicle_story():
    try:
        data = request.get_json()
        result = main(data["rej"], data["rej_data"], data["vin"])
        return jsonify(result), 201
    except ValueError:
        return jsonify({"error": "Invalid JSON"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

