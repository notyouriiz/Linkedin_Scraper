# LinkedIn Alumni Scraper

This project is a web scraper that automates the process of extracting LinkedIn alumni data from a specific university. It collects information such as names, job titles, profile links, experience, education, and certifications.

## Features
- **Automated Login**: Supports auto login that able to bypass LinkedIn's bot detection.
- **Manual Login**: Safer option to bypass LinkedIn's bot detection.
- **Dynamic Scrolling**: Loads more profiles dynamically for comprehensive data extraction.
- **Profile Scraping**: Extracts detailed information such as work experience, education, and certifications.
- **Data Storage**: Saves extracted data into a CSV file for further analysis.
- **City-Based Search**: Scrapes alumni based on city names from a predefined list.

## Requirements
Before running the scraper, ensure you have the following dependencies installed:

```sh
pip install -r requirements.txt
```

### Dependencies
- `selenium`
- `webdriver-manager`
- `pandas`
- `python-dotenv`

## Setup
1. **Install Dependencies**
   ```sh
   pip install -r requirements.txt
   ```

2. **Set Up Credentials**
   Create a `.env` file in the project directory and add your LinkedIn credentials:
   ```env
   LINKEDIN_EMAIL=your-email@example.com
   LINKEDIN_PASSWORD=your-password
   ```

3. **Download ChromeDriver**
   Ensure you have the appropriate version of ChromeDriver installed. The script will attempt to download it automatically using `webdriver-manager`.

4. **Prepare City List**
   Ensure that the `Data/Person Locations/indonesia_cities.csv` file contains a list of cities in a column named `City`.

5. **Prepare Class Code**
   ```Python
   ('div', {
            'class': 'YqprdwMdlHkSDMqLRuVsNMDuqpfpOSlCY EUugwXMAWHNSsJUZCvVoLYGTUzCejokiBUPPY aDbiGyAraCVAtqkDKUGRiLuhDZgkXmYiMA' # Make sure this Code is UP TO DATE
        })
   ```
   <img align="center" src="Web Structure Image/Class Code.png" alt="Class Code Places" style="border-radius: 10px; margin-top: 10px;" height="30%" width="30%" /><br><br>
   Ensure that the `Class`, code from your Linkedin is Up To Date, the Class Code on the program might be different due to Linkedin Dynamic Section `Class` Code.

   <p align="center"><strong>💡Tips: Place your Cursor in the Border of the Section While Inspect With Cursor</strong></p>

## Usage
Run the script with the following command:

```sh
python main.py
```

### Manual Login
- The script will prompt you to log in manually to LinkedIn.
- After logging in, press **Enter** in the terminal to continue.

### User Prompts During Scraping
- **Press Enter** to continue scraping the next profile.
- **Type `next`** to skip to the next city.
- **Type `exit`** to stop the script immediately.

## Output
The extracted data will be saved in:
```
Data/LinkedIn_SCU_Alumni.csv
```
with the following fields:
- City
- Name
- Job Title
- LinkedIn Profile Link
- Profile Picture URL
- Experience
- Education
- Licenses & Certifications

## Notes
- Scraping LinkedIn data is against their terms of service; use this tool responsibly.
- Avoid running the script too frequently to prevent detection.
- Ensure your LinkedIn account is in good standing before scraping.

## License
This project is for educational purposes only. Use at your own risk.

---

**Author:** Faiz Noor Adhytia  
**Contact:** faizadhytia24@gmail.com

