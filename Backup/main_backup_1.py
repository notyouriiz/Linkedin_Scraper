import os
import time
import re
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
options.add_argument("--disable-popup-blocking")
options.add_argument("--disable-blink-features=AutomationControlled")  # Bypass bot detection
options.add_argument("--disable-gpu")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

# Initialize WebDriver
chromedriver_path = "driver/chromedriver.exe"
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=options)

def manual_login():
    """Prompts the user to log in manually."""
    driver.get("https://www.linkedin.com/login")
    print("🔹 Please log in manually and press Enter here once done.")
    input("🔹 Press Enter after logging in...")
    print("✅ Logged in manually!")

# def login_linkedin():
#     """Logs into LinkedIn securely."""
#     driver.get("https://www.linkedin.com/login")
    
#     try:
#         WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(LINKEDIN_EMAIL)
#         WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password"))).send_keys(LINKEDIN_PASSWORD + Keys.RETURN)
#         time.sleep(random.uniform(5, 7))  # Allow login process
#         print("✅ Logged in successfully!")
#     except Exception as e:
#         print(f"❌ Login failed: {e}")
#         driver.quit()
#         exit()


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


def extract_profile_data(profile_url):
    """Extracts Experience, Education, and Licenses from an individual LinkedIn profile."""
    driver.get(profile_url)
    time.sleep(random.uniform(5, 7)) 

    profile_data = {
        "Experience": [],
        "Education": [],
        "Licenses & Certifications": []
    }

    # Extract Experience
    try:
        experiences = driver.find_elements(By.XPATH, "/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[5]/div[3]/ul/li")
        profile_data["Experience"] = [exp.text.strip() for exp in experiences]
    except:
        profile_data["Experience"] = []

    # Extract Education
    try:
        educations = driver.find_elements(By.XPATH, "/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[6]/div[3]/ul/li")
        profile_data["Education"] = [edu.text.strip() for edu in educations]
    except:
        profile_data["Education"] = []

    # Extract Licenses & Certifications
    try:
        licenses = driver.find_elements(By.XPATH, "/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[7]/div[3]/ul/li/div")
        profile_data["Licenses & Certifications"] = [lic.text.strip() for lic in licenses]
    except:
        profile_data["Licenses & Certifications"] = []

    return profile_data


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
                name_element = profile.find_element(By.XPATH, './/div[contains(@class, "artdeco-entity-lockup__title")]')
                name = name_element.text.strip() if name_element else "Unknown"

                # Extract Job Title
                job_element = profile.find_element(By.XPATH, './/div[contains(@class, "artdeco-entity-lockup__subtitle")]')
                job_title = job_element.text.strip() if job_element else "N/A"

                # Extract Profile Image
                image_element = profile.find_element(By.TAG_NAME, "img")
                image_url = image_element.get_attribute("src") if image_element else "No image"

                # Extract Profile URL (Anchor located inside div with the specific class)
                profile_url_element = profile.find_element(By.XPATH, './/div[contains(@class, "artdeco-entity-lockup__title")]//a[contains(@href, "/in/")]')
                profile_url = profile_url_element.get_attribute("href") if profile_url_element else ""

                # Visit profile page to extract more data
                if profile_url:
                    profile_data = extract_profile_data(profile_url)
                    alumni_list.append({
                        "Name": name,
                        "Job Title": job_title,
                        "Profile Image": image_url,
                        "Experience": profile_data["Experience"],
                        "Education": profile_data["Education"],
                        "Licenses & Certifications": profile_data["Licenses & Certifications"]
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
    df = pd.DataFrame(data, columns=["Name", "Job Title", "Profile Image", "Experience", "Education", "Licenses & Certifications"])
    filename = "Data/LinkedIn_SCU_Alumni_Backup_1.csv"
    df.to_csv(filename, index=False)
    print(f"✅ Data saved to {filename}")


def main():
    """Main function to execute the scraper."""
    manual_login()
    alumni_data = search_alumni()
    save_to_csv(alumni_data)
    driver.quit()


if __name__ == "__main__":
    main()