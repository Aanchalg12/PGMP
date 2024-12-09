import selenium
from selenium.webdriver.support.ui import Select
from django.test import TestCase
import time
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException

class test1(LiveServerTestCase):

#     def testlogin(self):
#         driver = webdriver.Chrome()
#         driver.get("http://127.0.0.1:8000/login/")
#         time.sleep(5)
#         username= driver.find_element(By.NAME, 'username')
#         password= driver.find_element(By.NAME, 'password')

#         submit = driver.find_element(By.XPATH, '/html/body/section/div/div/div/div/div/form/button')

#         # username.send_keys('admin')
#         # password.send_keys('Test@123')
#         # username.send_keys('admin') #incorrect password
#         # password.send_keys('Test@12')
#         # username.send_keys('Admin') #incorrect username
#         # password.send_keys('Test@123')
#         # username.send_keys('admi') #incorrect username n password
#         # password.send_keys('Test@12')
#         # username.send_keys('') #empty username n password
#         # password.send_keys('')
#         # username.send_keys('') #empty username n correct password
#         # password.send_keys('Test@123')
#         # username.send_keys('ad') #empty username n correct password
#         # password.send_keys('')
#         submit.click()
#         time.sleep(7)
        
#         actualUrl="http://127.0.0.1:8000/admin_dashboard/"   #admin dashboard
#         expectedUrl= driver.current_url 
      
#         self.assertEqual(actualUrl, expectedUrl)
#         driver.close()
#         return driver

    # def testSignUp(self):
    #     driver = webdriver.Chrome()
    #     driver.get("http://127.0.0.1:8000/signup/")
    #     time.sleep(5)
    #     username= driver.find_element(By.NAME, 'username')
    #     email= driver.find_element(By.NAME, 'email')
    #     password1= driver.find_element(By.NAME, 'password1')
    #     password2= driver.find_element(By.NAME, 'password2')
    #     submit = driver.find_element(By.XPATH, '/html/body/section/div/div/div/div/div/form/button')

    #     username.send_keys('arpit')
    #     email.send_keys('arpit@gmail.com')
    #     password1.send_keys('Test@123')
    #     password2.send_keys('Test@123')
    #     submit.click()
    #     time.sleep(5)
        
    #     actualUrl="http://127.0.0.1:8000/login/"
    #     expectedUrl= driver.current_url 
      
    #     self.assertEqual(actualUrl, expectedUrl)
    #     driver.close()

    # def testCustomerDashboard(self):
    #     driver = webdriver.Chrome()
    #     driver.maximize_window()
    #     driver.get("http://127.0.0.1:8000/login/")
    #     # time.sleep(3)
    #     username= driver.find_element(By.NAME, 'username')
    #     password= driver.find_element(By.NAME, 'password')
    #     submit = driver.find_element(By.XPATH, '/html/body/section/div/div/div/div/div/form/button')
    #     username.send_keys('arpit')
    #     password.send_keys('Test@123')
    #     submit.click()
    #     actualUrl="http://127.0.0.1:8000/dashboard/customer/"
    #     expectedUrl= driver.current_url 
    #     self.assertEqual(actualUrl, expectedUrl)
    #     # estimator= driver.find_element(By.XPATH, '/html/body/div[1]/nav/a[4]')
    #     # estimator.click()
    #     # postcode= driver.find_element(By.ID, 'postcode')
    #     # bill= driver.find_element(By.ID, 'electricity_bill')
    #     # x = driver.find_element(By.ID, 'house_type')
    #     # drop = Select(x) 
    #     # button= driver.find_element(By.XPATH, '//*[@id="solar-estimation-form"]/div[4]/button')
    #     # postcode.send_keys('CB58HL')
    #     # bill.send_keys('80')
    #     # drop.select_by_value("semi-detached")
    #     # button.click()
    #     # time.sleep(5)
    #     # actualUrl= "http://127.0.0.1:8000/estimation_result/"
    #     # expectedUrl= driver.current_url 
    #     # self.assertEqual(actualUrl, expectedUrl)
    #     dashboard= driver.find_element(By.XPATH, '/html/body/div[1]/nav/a[1]/span[2]')
    #     dashboard.click()
    #     time.sleep(3)
    #     add_button = WebDriverWait(driver, 10).until(
    #         EC.presence_of_element_located((By.XPATH, '/html/body/main/section[2]/div/div/div/div/div[3]/a'))
    #     )
    #     button_location = add_button.location
    #     driver.execute_script(f"window.scrollTo(0, {button_location['y'] - 100});")
    #     add_button = WebDriverWait(driver, 10).until(
    #         EC.element_to_be_clickable((By.XPATH, '/html/body/main/section[2]/div/div/div/div/div[3]/a'))
    #     )
    #     try:
    #         add_button.click()
    #     except selenium.common.exceptions.ElementClickInterceptedException:
    #         print("Click intercepted. Attempting JavaScript click.")
    #         driver.execute_script("arguments[0].click();", add_button)
    #     except selenium.common.exceptions.StaleElementReferenceException:
    #         print("Stale element detected. Re-locating and re-clicking.")
    #         add_button = WebDriverWait(driver, 10).until(
    #             EC.element_to_be_clickable((By.XPATH, '/html/body/main/section[2]/div/div/div/div/div[3]/a'))
    #         )
    #         add_button.click()
        
    #     shopping_cart= driver.find_element(By.XPATH, '/html/body/main/div[2]/div[2]/div/div/div/div/a[1]')
    #     cart = shopping_cart.location
    #     driver.execute_script(f"window.scrollTo(0, {cart['y'] - 100});")
    #     shopping_cart = WebDriverWait(driver, 10).until(
    #         EC.element_to_be_clickable((By.XPATH, '/html/body/main/div[2]/div[2]/div/div/div/div/a[1]'))
    #     )
    #     try:
    #         shopping_cart.click()
    #     except selenium.common.exceptions.ElementClickInterceptedException:
    #         print("Click intercepted. Attempting JavaScript click.")
    #         driver.execute_script("arguments[0].click();", shopping_cart)
    #     except selenium.common.exceptions.StaleElementReferenceException:
    #         print("Stale element detected. Re-locating and re-clicking.")
    #         shopping_cart = WebDriverWait(driver, 10).until(
    #             EC.element_to_be_clickable((By.XPATH, '/html/body/main/div[2]/div[2]/div/div/div/div/a[1]'))
    #         )
    #         shopping_cart.click()
    #     edit_cart= driver.find_element(By.XPATH, '//*[@id="id_quantity"]')
    #     edit_cart.clear()
    #     edit_cart.send_keys('1')
    #     save = driver.find_element(By.XPATH, '/html/body/main/form/button')
    #     save.click()
    
    #     # checkout= driver.find_element(By.CSS_SELECTOR, 'btn btn-primary')
    #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    #     # Wait for the checkout button to become clickable and then click
    #     checkout = WebDriverWait(driver, 10).until(
    #         EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn.btn-primary'))
    #     )
    #     try:
    #         checkout.click()
    #     except ElementClickInterceptedException:
    #         driver.execute_script("arguments[0].click();", checkout)
    #     order= driver.find_element(By.XPATH, '/html/body/main/div[2]/form/button')
    #     order.click()
    #     time.sleep(2)
    #     driver.close()

    def testAdminDashboard(self):
        driver = webdriver.Chrome()
        driver.maximize_window()
        driver.get("http://127.0.0.1:8000/login/")
        # time.sleep(3)
        username= driver.find_element(By.NAME, 'username')
        password= driver.find_element(By.NAME, 'password')
        submit = driver.find_element(By.XPATH, '/html/body/section/div/div/div/div/div/form/button')
        username.send_keys('admin')
        password.send_keys('Test@123')
        submit.click()
        actualUrl="http://127.0.0.1:8000/admin_dashboard/"
        expectedUrl= driver.current_url 
        self.assertEqual(actualUrl, expectedUrl)
        user_management= driver.find_element(By.XPATH, '/html/body/div/nav/a[2]')
        user_management.click()
        # read= driver.find_element(By.XPATH, '/html/body/main/table/tbody/tr[1]/td[4]/a[1]')
        # read.click()
        # actualUrl="http://127.0.0.1:8000/user_detail/6/"
        # expectedUrl= driver.current_url 
        # self.assertEqual(actualUrl, expectedUrl)
        add_user= driver.find_element(By.PARTIAL_LINK_TEXT, 'Add New User')
        add_user.click()
        user=driver.find_element(By.ID, 'id_username').send_keys('tim')
        email=driver.find_element(By.ID, 'id_email').send_keys('tim@gmail.com')
        address=driver.find_element(By.ID, 'id_address').send_keys('Cambridge, UK')
        mobile=driver.find_element(By.ID, 'id_mobile').send_keys('7539590520')
        password1=driver.find_element(By.ID, 'id_password').send_keys('Test@123')
        select = Select(driver.find_element(By.ID,'id_user_role'))
        select.select_by_visible_text('Vendor')
        company_name=driver.find_element(By.NAME, 'company_name').send_keys('Tim Solar Panel Company')
        save= driver.find_element(By.XPATH, '/html/body/main/div/form/button').click()
        time.sleep(4)
        driver.close()