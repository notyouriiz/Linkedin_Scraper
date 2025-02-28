import os
import time
import random
import pandas as pd
from dotenv import load_dotenv
from selenium import webdriver
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
options.add_argument("--disable-blink-features=AutomationControlled")  
options.add_argument("--disable-gpu")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

# Initialize WebDriver
chromedriver_path = "driver/chromedriver.exe"
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=options)

# Load city names from CSV
city_file_path = "Data/Person Locations/indonesia_cities.csv"
cities_df = pd.read_csv(city_file_path)
cities = cities_df["City"].tolist()

# CSV file path
csv_file = "Data/LinkedIn_SCU_Alumni.csv"

# Load existing data
if os.path.exists(csv_file):
    existing_df = pd.read_csv(csv_file)
    scraped_urls = set(existing_df["Linkedin Link"].dropna())  # Set for fast lookup
else:
    existing_df = pd.DataFrame()
    scraped_urls = set()

# Global flag to stop scraping
stop_scraping = False  

def manual_login():
    """Prompts the user to log in manually."""
    driver.get("https://www.linkedin.com/login")
    print("🔹 Please log in manually and press Enter here once done.")
    input("🔹 Press Enter after logging in...")
    print("✅ Logged in manually!")

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

def search_alumni(city, max_profiles=50):
    """Scrapes alumni data from LinkedIn for a given city."""
    global stop_scraping  # Allow modification of the global flag

    search_url = f"https://www.linkedin.com/school/unika-soegijapranata-semarang/people/?keywords={city}"
    driver.get(search_url)
    time.sleep(random.uniform(5, 7))

    alumni_list = []
    profiles_scraped = 0

    while profiles_scraped < max_profiles:
        if stop_scraping:
            print("❌ Stopping scraping immediately...")
            return alumni_list  

        scroll_page()
        try:
            profiles = WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "org-people-profile-card__profile-info")]'))
            )
            print(f"🔍 Found {len(profiles)} profiles in {city}")

            for profile in profiles:
                if stop_scraping:
                    print("❌ Stopping scraping immediately...")
                    return alumni_list  

                if profiles_scraped >= max_profiles:
                    print(f"✅ Reached {max_profiles} profiles for {city}. Moving to the next city...")
                    return alumni_list  

                user_input = input("🔹 Press Enter to continue, type 'next' to skip city, or 'exit' to stop: ").strip().lower()
                if user_input == "exit":
                    stop_scraping = True
                    print("❌ Stopping scraping immediately...")
                    return alumni_list
                elif user_input == "next":
                    print(f"➡️ Skipping city: {city}")
                    return alumni_list  

                try:
                    name_element = profile.find_element(By.XPATH, './/div[contains(@class, "artdeco-entity-lockup__title")]')
                    name = name_element.text.strip() if name_element else "Unknown"

                    job_element = profile.find_element(By.XPATH, './/div[contains(@class, "artdeco-entity-lockup__subtitle")]')
                    job_title = job_element.text.strip() if job_element else "N/A"

                    image_element = profile.find_element(By.TAG_NAME, "img")
                    image_url = image_element.get_attribute("src") if image_element else "No image"

                    profile_url_element = profile.find_element(By.XPATH, './/div[contains(@class, "artdeco-entity-lockup__title")]//a[contains(@href, "/in/")]')
                    profile_url = profile_url_element.get_attribute("href") if profile_url_element else ""

                    if profile_url in scraped_urls:
                        print(f"🔹 Profile already scraped: {profile_url}")
                        continue  

                    if profile_url:
                        scraped_urls.add(profile_url)  # Mark as scraped
                        profiles_scraped += 1

                        driver.execute_script("window.open(arguments[0]);", profile_url)
                        driver.switch_to.window(driver.window_handles[1])

                        profile_data = extract_profile_data(profile_url)

                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])

                        alumni_list.append({
                            "City": city,
                            "Name": name,
                            "Headlines": job_title,
                            "Linkedin Link": profile_url,
                            "Profile Picture": image_url,
                            "Experience": profile_data["Experience"],
                            "Education": profile_data["Education"],
                            "Licenses & Certifications": profile_data["Licenses & Certifications"]
                        })

                except Exception as e:
                    print(f"⚠️ Error extracting profile: {e}")
                    continue

        except Exception as e:
            print(f"❌ No more profiles found for {city}: {e}")
            break  

    print(f"✅ Scraped {len(alumni_list)} profiles from {city}")
    return alumni_list

def save_to_csv(new_data):
    """Appends new data to the existing CSV file without overwriting."""
    new_df = pd.DataFrame(new_data)
    new_df.to_csv(csv_file, mode='a', header=not os.path.exists(csv_file), index=False)
    print(f"✅ New data appended to {csv_file}")

def main():
    """Main function to execute the scraper for multiple cities."""
    global stop_scraping

    manual_login()
    all_alumni_data = []

    for city in cities:
        if stop_scraping:
            break  
        print(f"🔍 Searching alumni from: {city}...")
        alumni_data = search_alumni(city)
        all_alumni_data.extend(alumni_data)

    if all_alumni_data:
        save_to_csv(all_alumni_data)
    
    driver.quit()

if __name__ == "__main__":
    main()
