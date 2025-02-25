import os
import time
import random
import pandas as pd
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Load credentials
load_dotenv("credentials.env")
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

# Set up Chrome options
options = Options()
options.add_argument("--headless=new")  # Run in headless mode (remove if debugging)
options.add_argument("--disable-gpu")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--disable-blink-features=AutomationControlled")  # Bypass bot detection
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

# Initialize WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def login_linkedin():
    """Logs into LinkedIn securely."""
    driver.get("https://www.linkedin.com/login")
    
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(LINKEDIN_EMAIL)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password"))).send_keys(LINKEDIN_PASSWORD + Keys.RETURN)
        time.sleep(random.uniform(5, 7))  # Allow login process
        print("✅ Logged in successfully!")
    except Exception as e:
        print(f"❌ Login failed: {e}")
        driver.quit()
        exit()


def scroll_page():
    """Scrolls down dynamically to load more profiles."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(2, 4))
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def search_alumni():
    """Scrapes Soegijapranata Catholic University alumni from LinkedIn."""
    search_url = "https://www.linkedin.com/school/unika-soegijapranata-semarang/people/"
    driver.get(search_url)
    time.sleep(random.uniform(5, 7))  # Allow page to load

    alumni_list = []
    scroll_page()  # Scroll to load more profiles dynamically

    try:
        profiles = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "org-people-profile-card__profile-info")]'))
        )
        print(f"🔍 Found {len(profiles)} profiles")

        for profile in profiles:
            try:
                # Extract Name
                try:
                    name_element = profile.find_element(By.XPATH, './/div[contains(@class, "artdeco-entity-lockup__title")]')
                    name = name_element.text.strip() if name_element else "Unknown"
                except:
                    name = "Unknown"

                # Extract Job Title
                try:
                    job_element = profile.find_element(By.XPATH, './/div[contains(@class, "artdeco-entity-lockup__subtitle")]')
                    job_title = job_element.text.strip() if job_element else "N/A"
                except:
                    job_title = "N/A"

                # Extract Profile Description
                try:
                    description_element = profile.find_element(By.XPATH, './/div[contains(@class, "lt-line-clamp--multi-line")]')
                    description = description_element.text.strip() if description_element else "No description"
                except:
                    description = "No description"

                # Extract Profile Image
                try:
                    image_element = profile.find_element(By.TAG_NAME, "img")
                    image_url = image_element.get_attribute("src") if image_element else "No image"
                except:
                    image_url = "No image"

                # Extract Location
                try:
                    location_element = profile.find_element(By.XPATH, './/span[contains(@class, "text-align-center")]')
                    location = location_element.text.strip() if location_element else "Unknown"
                except:
                    location = "Unknown"

                # Extract Graduation Year (if available)
                try:
                    grad_year_element = profile.find_element(By.XPATH, './/span[contains(text(), "Class of")]')
                    grad_year = grad_year_element.text.strip().replace("Class of ", "") if grad_year_element else "N/A"
                except:
                    grad_year = "N/A"

                print(f"👤 {name} | 💼 {job_title} | 📜 {description} | 🖼️ {image_url} | 📍 {location} | 🎓 {grad_year}")  # Debugging Output

                alumni_list.append({
                    "Name": name,
                    "Job Title": job_title,
                    "Profile Description": description,
                    "Profile Image": image_url,
                    "Location": location,
                    "Graduation Year": grad_year
                })
            except Exception as e:
                print(f"⚠️ Error extracting profile: {e}")
                continue

    except Exception as e:
        print(f"❌ No profiles found: {e}")

    print(f"✅ Scraped {len(alumni_list)} profiles")
    return alumni_list


def save_to_csv(data):
    """Saves the scraped data to a CSV file with separate columns."""
    df = pd.DataFrame(data, columns=["Name", "Job Title", "Profile Description", "Profile Image", "Location", "Graduation Year"])
    filename = "LinkedIn_SCU_Alumni.csv"
    df.to_csv(filename, index=False)
    print(f"✅ Data saved to {filename}")


def main():
    """Main function to execute the scraper."""
    login_linkedin()
    alumni_data = search_alumni()
    save_to_csv(alumni_data)
    driver.quit()


if __name__ == "__main__":
    main()
