from selenium import webdriver
from selenium.webdriver.common.by import By

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)


driver = webdriver.Chrome(options=chrome_options)
# driver.get("https://www.amazon.com/dp/B075CYMYK6?psc=1&ref_=cm_sw_r_cp_ud_ct_FM9M699VKHTT47YD50Q6")

# price_dollar = driver.find_elements(By.CLASS_NAME,value="a-price-whole")
# price_cents = driver.find_elements(By.CLASS_NAME,value="a-price-fraction")
#
# print(f"The price is {price_dollar.text}.{price_cents.text}")

driver.get("https://www.python.org/")
event_time =driver.find_elements(By.CSS_SELECTOR,value=".event-widget time")
event_name =driver.find_elements(By.CSS_SELECTOR,value=".event-widget li a")
events = {}

for n in range(len(event_time)):
    events[n] = {
        "time" : event_time[n].text,
        "name" : event_name[n].text,

    }
print(events)




driver.quit()