import os
import time
import random
import re
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
import csv
from flask import send_file
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from Formatter.data_cleaner import clean_scraped_data

stop_scraping = False
driver = None
scraped_urls = set()
city_file_path = "Data/Person Locations/Indonesia_names.csv"
csv_file = "Data/Linkedin_SCU_Alumni_2025.csv"
load_dotenv("credentials.env")

def start_driver():
    """Driver setup for web scraping using Bright Data Web Unlocker direct API."""
    global driver
    
    API_KEY = os.getenv("UNLOCKER_API_KEY")
    UNLOCKER_URL = f"https://brd.superproxy.io:33335?api_key={API_KEY}"
    seleniumwire_options = {
        'proxy': {
            'http': UNLOCKER_URL,
            'https': UNLOCKER_URL,
            'no_proxy': 'localhost,127.0.0.1'
        }
    }
    # Chrome options for stealth
    options = uc.ChromeOptions()
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--start-maximized")
    options.add_argument("--lang=en-US,en")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/119.0.0.0 Safari/537.36"
    )
    driver_path = ChromeDriverManager().install()
    driver = uc.Chrome(driver_executable_path=driver_path, options=options, seleniumwire_options=seleniumwire_options)
    return driver

def manual_login():
    driver.get("https://www.linkedin.com/login")
    print("🔹 Please log in manually in the browser window.")

def scroll_page(driver, max_clicks=10):
    """Scrolls down dynamically and clicks 'Load more' if present."""
    clicks = 0
    total_scrolls = random.randint(10, 20)
    scroll_pause = [random.uniform(1.5, 4) for _ in range(total_scrolls)]

    body = driver.find_element("tag name", "body")

    for i in range(total_scrolls):
        # Scroll a bit
        scroll_height = random.randint(300, 700)
        driver.execute_script(f"window.scrollBy(0, {scroll_height});")
        time.sleep(scroll_pause[i])

        # Occasionally scroll up
        if random.random() < 0.2:
            driver.execute_script(f"window.scrollBy(0, {-random.randint(100, 300)});")
            time.sleep(random.uniform(1, 2))

        # Try clicking "Load more" if it's there
        try:
            load_more = driver.find_element(By.XPATH, '//*[@class="artdeco-button artdeco-button--muted artdeco-button--1 artdeco-button--full artdeco-button--secondary ember-view scaffold-finite-scroll__load-button"]')
            if load_more.is_displayed():
                print("🔄 Clicking 'Load more'...")
                driver.execute_script("arguments[0].click();", load_more)
                time.sleep(random.uniform(2, 4))
                clicks += 1
                if clicks >= max_clicks:
                    print("🛑 Max load-more clicks reached.")
                    break
        except NoSuchElementException:
            pass
    # Final scroll to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

def extract_profile_data(profile_url, location_class, section_class):
    """Extracts Experience, Education, and Licenses from an individual LinkedIn profile with dynamic class input."""
    driver.get(profile_url)
    time.sleep(random.uniform(5, 7))
    scroll_page(driver)

    soup = BeautifulSoup(driver.page_source, 'lxml')

    profile_data = {
        "Location": "N/A",
        "Experience": [],
        "Education": [],
        "Licenses & Certifications": []
    }

    # Extract Location using user-defined class
    if location_class:
        location_div = soup.find('div', {'class': location_class})
        if location_div:
            location_span = location_div.find('span')
            if location_span:
                text = location_span.get_text(strip=True)
                if text:
                    profile_data["Location"] = text

    # Common logic to find section by ID
    def find_section_by_id(section_id):
        return soup.find('section', {'id': section_id}) or \
               next((sec for sec in soup.find_all('section') if sec.find('div', {'id': section_id})), None)

    # Extract Experience
    experience = find_section_by_id('experience')
    if experience and section_class:
        experiences = experience.find_all('div', {'class': section_class})
        for exp in experiences:
            job_title = exp.find('span', {'class': 'visually-hidden'})
            company = exp.find('span', {'class': 't-14 t-normal'})
            duration = exp.find('span', {'class': 't-14 t-normal t-black--light'})

            profile_data["Experience"].append({
                "Job Title": job_title.get_text(strip=True) if job_title else "N/A",
                "Company": company.get_text(strip=True) if company else "N/A",
                "Duration": duration.get_text(strip=True) if duration else "N/A"
            })

    # Extract Education
    education = find_section_by_id('education')
    if education and section_class:
        educations = education.find_all('div', {'class': section_class})
        for edu in educations:
            spans = edu.find_all('span', {'class': 'visually-hidden'})
            school = spans[0].get_text(strip=True) if len(spans) > 0 else "N/A"
            degree = spans[1].get_text(strip=True) if len(spans) > 1 else "N/A"
            duration = spans[2].get_text(strip=True) if len(spans) > 2 else "N/A"
            project = spans[3].get_text(strip=True) if len(spans) > 3 else "N/A"

            profile_data["Education"].append({
                "School": school,
                "Degree": degree,
                "Duration": duration,
                "Project": project
            })

    # Extract Licenses & Certifications
    licenses = find_section_by_id('licenses_and_certifications')
    if licenses and section_class:
        license_list = licenses.find_all('div', {'class': section_class})
        for lic in license_list:
            cert_name = lic.find('span', {'class': 'visually-hidden'})
            issued_by = lic.find('span', {'class': 't-14 t-normal'})

            profile_data["Licenses & Certifications"].append({
                "Certification": cert_name.get_text(strip=True) if cert_name else "N/A",
                "Issued By": issued_by.get_text(strip=True) if issued_by else "N/A"
            })

    return profile_data



def search_alumni(keyword, profiles_scraped, max_profiles, location_class, section_class):
    """Search alumni profiles in two phases: collect URLs first, then extract profile data."""
    global stop_scraping
    driver.set_page_load_timeout(45)

    search_url = f"https://www.linkedin.com/school/unika-soegijapranata-semarang/people/?keywords={keyword}"
    driver.get(search_url)
    time.sleep(random.uniform(5, 7))

    collected_profiles = []

    # -------- Phase 1: Collect profile metadata (no navigation yet) --------
    while profiles_scraped + len(collected_profiles) < max_profiles:
        if stop_scraping:
            print("❌ Stopping scraping immediately...")
            return []

        scroll_page(driver)

        try:
            profiles = WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, '//div[contains(@class, "org-people-profile-card__profile-info")]')
                )
            )
            print(f"\n🔍 Found {len(profiles)} profiles in {keyword}\n")

            new_profile_found = False

            for profile in profiles:
                if stop_scraping or profiles_scraped + len(collected_profiles) >= max_profiles:
                    break

                try:
                    profile_url_element = profile.find_element(
                        By.XPATH,
                        './/div[contains(@class, "artdeco-entity-lockup__title")]//a[contains(@href, "/in/")]'
                    )
                    profile_url = profile_url_element.get_attribute("href") if profile_url_element else ""

                    # Skip duplicates or empty URLs
                    if not profile_url or profile_url in scraped_urls:
                        continue

                    name_element = profile.find_element(
                        By.XPATH, './/div[contains(@class, "artdeco-entity-lockup__title")]'
                    )
                    name = name_element.text.strip() if name_element else "Unknown"

                    job_element = profile.find_element(
                        By.XPATH, './/div[contains(@class, "artdeco-entity-lockup__subtitle")]'
                    )
                    job_title = job_element.text.strip() if job_element else "N/A"

                    image_element = profile.find_element(By.TAG_NAME, "img")
                    image_url = image_element.get_attribute("src") if image_element else "No image"

                    # Save metadata
                    collected_profiles.append({
                        "Name": name,
                        "Headlines": job_title,
                        "Linkedin Link": profile_url,
                        "Profile Picture": image_url
                    })
                    scraped_urls.add(profile_url)
                    new_profile_found = True

                except Exception as e:
                    print(f"⚠️ Error collecting profile metadata: {e}")
                    continue

            if not new_profile_found:
                print("🚫 No new profiles found on this scroll. Moving to next keyword...")
                break

        except Exception as e:
            print(f"❌ No profiles found for {keyword}: {e}")
            break

    # -------- Phase 2: Visit each profile and extract details --------
    alumni_list = []
    for profile in collected_profiles:
        if stop_scraping or profiles_scraped + len(alumni_list) >= max_profiles:
            break

        profile_url = profile["Linkedin Link"]

        try:
            profile_data = extract_profile_data(profile_url, location_class, section_class)

            alumni_list.append({
                "City": profile_data["Location"],
                "Name": profile["Name"],
                "Headlines": profile["Headlines"],
                "Linkedin Link": profile_url,
                "Profile Picture": profile["Profile Picture"],
                "Experience": profile_data["Experience"],
                "Education": profile_data["Education"],
                "Licenses & Certifications": profile_data["Licenses & Certifications"],
                "Scraped At": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

        except Exception as e:
            print(f"⚠️ Timeout or error extracting {profile_url}: {e}")
            continue

    print(f"✅ Scraped {len(alumni_list)} profiles from {keyword}")
    return alumni_list




def save_to_csv(all_alumni_data, filename=csv_file, overwrite=False):
    """Saving scraping result either overwriting or appending."""
    # Always load existing data if the file exists
    existing_data = load_existing_data(filename) if os.path.exists(filename) else []

    # Merge new data into the existing data (overwrite profiles with matching URLs)
    for new_profile in all_alumni_data:
        existing_profile = next((p for p in existing_data if p["Linkedin Link"] == new_profile["Linkedin Link"]), None)
        if existing_profile:
            existing_data[existing_data.index(existing_profile)] = new_profile
        else:
            existing_data.append(new_profile)

    # Save the merged data back to the CSV
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        fieldnames = ["City", "Name", "Headlines", "Linkedin Link", "Profile Picture", "Experience", "Education", "Licenses & Certifications", "Scraped At"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(existing_data)

    print(f"✅ Data successfully saved to {filename}")
    
    
def load_existing_data(filename):
    """Load existing data from the CSV file, return empty list if missing."""
    if not os.path.exists(filename):
        return []
    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)


def clean_class_input(class_input):
    """
    Cleans messy HTML class input:
    - Strips spaces, tabs, and newlines from ends
    - Removes quotes and unwanted characters
    - Keeps only valid CSS class characters
    """
    if not class_input:
        return ""
    cleaned = class_input.strip().strip('"').strip("'")
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = re.sub(r"[^a-zA-Z0-9_\- ]", "", cleaned)
    return cleaned


def run_scraper(location_class, section_class, max_profiles, overwrite=False):
    global scraped_urls

    location_class = clean_class_input(location_class)
    section_class = clean_class_input(section_class)
    
    start_driver()
    scraped_urls = set()

    # Load previously scraped URLs if appending
    if not overwrite:
        existing_data = load_existing_data(csv_file)
        scraped_urls = set(p["Linkedin Link"] for p in existing_data)

    keywords_df = pd.read_csv(city_file_path)
    keywords = keywords_df["Name"].tolist()

    all_data = []
    profiles_scraped = 0

    for keyword in keywords:
        if profiles_scraped >= max_profiles:
            break

        alumni = search_alumni(
            keyword, profiles_scraped, max_profiles,
            location_class, section_class
        )

        # update counters and results
        if alumni:
            profiles_scraped += len(alumni)
            all_data.extend(alumni)

    # Save results only if new data exists
    if all_data:
        save_to_csv(all_data, overwrite=overwrite)
        clean_scraped_data()

    driver.quit()
    print(f"✅ Done scraping! Total profiles scraped: {profiles_scraped}")
