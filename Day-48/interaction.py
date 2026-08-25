from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()
driver.get("https://en.wikipedia.org/wiki/Main_Page")

try:
    search = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#searchform input[name='search']"))
    )
    search.send_keys("Python",Keys.ENTER)
except Exception as e:
    driver.save_screenshot("debug.png")
    print("Failed:", e)