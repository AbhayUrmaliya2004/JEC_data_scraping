from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoAlertPresentException
import urllib
from pytesseract import image_to_string
import pytesseract
import time, csv
import os

# Specify the path to chromedriver.exe
chromedriver_path = 'D:\\BrowserDrivers\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe'
# Setup tesseract path 
tesseract_path = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = tesseract_path

# Setup driver
chrome_service = Service(executable_path=chromedriver_path)
chrome_options = Options()

chrome_options.add_argument('--ignore-ssl-errors=yes')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

driver = webdriver.Chrome(options=chrome_options, service=chrome_service)

class JecScrapingDemo:
    def scrap_details(self, id, password):
        driver.get('https://www.jecjabalpur.ac.in/')

        # Handle CAPTCHA and login
        for attempt in range(3):
            print(id, " ", attempt+1)
            time.sleep(0.5)
            # Cross the temporary info page 
            try:
               driver.find_element(By.XPATH, '//*[@id="alert-modal"]/div/div/div[1]/a').click()
            except:
               print("Couldn't cross")

            # Get the CAPTCHA code 
            try : 
                captcha_link = 'https://www.jecjabalpur.ac.in/' + driver.find_element(By.XPATH, '//*[@id="UserLogin1_pnlCaptcha"]/table/tbody/tr[1]/td/div/img').get_dom_attribute('src')
            except : 
                driver.refresh()
                continue 
            # send id and password
            try:
               driver.find_element(By.XPATH, '//*[@id="UserLogin1_txtUserName"]').send_keys(id)
               driver.find_element(By.XPATH, '//*[@id="UserLogin1_txtPassword"]').send_keys(password)
#           time.sleep(2)
            except:
               print("Couldn't send id or password")

            filename = id + '.png'
            response = urllib.request.urlopen(captcha_link)
            data = response.read()

            # Write the image data to a file
            with open(filename, 'wb') as f:
                f.write(data)

            text = image_to_string(filename)
            captcha_val = self.structure_captcha(text)
            os.remove(filename)
              
            # Cross the temporary info page 
            try:
                driver.find_element(By.XPATH, '//*[@id="alert-modal"]/div/div/div[1]/a').click()
            except:
                print("Couldn't cross")    
                  
            # Enter the CAPTCHA value
            try : 
               driver.find_element(By.XPATH, '//*[@id="UserLogin1_TextBox1"]').send_keys(captcha_val)
            except :
                print("could not find captcha value")
                driver.refresh()
                continue
            
            time.sleep(0.5)
            
            try:
                # Login into portal
                driver.find_element(By.XPATH, '//*[@id="UserLogin1_btnLogin"]').click()
#                time.sleep(2)
            except:
                print("Couldn't find captcha image or login button")
                # check again if couldn't login
                driver.refresh()
                continue 

            # Check if login was successful or CAPTCHA failed
            if self.is_alert_present(driver):
                print("Alert is present")
            # You can handle the alert here, e.g., accept it
                alert = driver.switch_to.alert
                alert_text = alert.text
                print("Alert Text : ", alert_text)
                alert.accept()
                
                # if captcha alert then try again
                if 'You have entered a wrong Captcha text' in alert_text:
                    driver.refresh()
                    continue

            else:
                break 

        else:
            print("Failed to login after 3 attempts")
            return
        
        time.sleep(0.5)
        # Get name
        name = '' 
        try:
            name = driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_InnerUserName1_lblUserName').text
        except: 
            print("Couldn't find name")

        # Student service
        try:
            driver.find_element(By.LINK_TEXT, 'STUDENT SERVICES').click()
        except:
            print("Couldn't find student service")

        # Enter into academic history 
        try:
            driver.find_element(By.LINK_TEXT, 'Academic History').click()
        except:
            print("Couldn't enter into academic history")

        session, gpa, semester = '', '', ''
        try:
            session = driver.find_element(By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_gvStudentHistory_GS"]/tbody/tr[2]/td[1]').text
            semester = driver.find_element(By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_gvStudentHistory_GS"]/tbody/tr[2]/td[2]').text
            gpa = driver.find_element(By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_gvStudentHistory_GS"]/tbody/tr[2]/td[3]').text
        except:
            print('Could not find GPA')

        if name != '' :
            with open('Selenium\data.csv', 'a', newline='') as f:
            # Assuming all variables are strings (add conversions if needed)
                csv_writer = csv.writer(f)
                csv_writer.writerow([id, name, session, semester, gpa])


        # Print the result 
        print('*' * 10, name, '*' * 10)
        print('Session:', session, '   Sem:', semester, '   GPA:', gpa)


    def is_alert_present(self, driver):
        try:
           alert = driver.switch_to.alert
           print("Alert Text : ", alert.text)
           return True
        except NoAlertPresentException:
             return False
        
    def structure_captcha(self, s):
        s = s[:-1].upper().replace(" ", '')
        s = s.replace("\n", "")
        return s[:5]
    
jec_page = JecScrapingDemo()

# Scraping student data 
enrolment_no = ['0201AI221003', '0201AI221030', '0201AI221023', '0201AI221003','0201AI221004']
password = ['220604', 'hggoswami_2004', '123456', '220604', '123456']

# Scraping
password = '123456'
for i in range(1,10):
    enrolment = '0201AI2210'
    if(i < 9):
        enrolment += '0'+str(i)
    else :
        enrolment += str(i)
    # check for all those have password 123456
    jec_page.scrap_details(enrolment, password)

driver.quit()