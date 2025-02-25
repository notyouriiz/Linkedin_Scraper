from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://www.linkedin.com/in/faizadhytia")

# Test if elements exist
try:
    name = driver.find_element(By.CLASS_NAME, "text-heading-xlarge").text
    print("Name:", name)
except:
    print("Name not found. LinkedIn structure may have changed.")

driver.quit()
