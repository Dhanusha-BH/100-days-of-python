from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys



chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)


driver = webdriver.Chrome(options=chrome_options)
driver.get("https://appbrewery.github.io/fake-newsletter-signup/")

first_name=driver.find_element(By.NAME,value="fName")
last_name=driver.find_element(By.NAME,value="lName")
email=driver.find_element(By.NAME,value="email")

first_name.send_keys("Dhanusha")
last_name.send_keys("BH")
email.send_keys("dhanusha@gmail.com")

submit = driver.find_element(By.CSS_SELECTOR,value="form button")
submit.click()