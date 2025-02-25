# unittest_main.py
import unittest
from unittest.mock import patch, MagicMock
from main import login_linkedin, scroll_page, extract_profile_data, save_to_csv
from selenium.webdriver.common import By

class TestLinkedInScraper(unittest.TestCase):

    @patch('main.webdriver.Chrome')
    @patch('main.time.sleep')
    def test_login_linkedin(self, MockSleep, MockChrome):
        # Mocking the WebDriver
        mock_driver = MagicMock()
        MockChrome.return_value = mock_driver
        
        # Mocking successful login (mocking WebDriverWait and element interactions)
        mock_driver.get.return_value = None
        mock_driver.find_element.return_value.send_keys = None
        mock_driver.find_element.return_value.text = "Success"

        login_linkedin()  # Call the login function

        # Check that the login attempted to visit the LinkedIn login page
        mock_driver.get.assert_called_with("https://www.linkedin.com/login")
        mock_driver.find_element.assert_any_call(By.ID, "username")
        mock_driver.find_element.assert_any_call(By.ID, "password")

    @patch('main.webdriver.Chrome')
    @patch('main.time.sleep')
    def test_scroll_page(self, MockSleep, MockChrome):
        # Mocking the WebDriver
        mock_driver = MagicMock()
        MockChrome.return_value = mock_driver

        # Simulating a scrolling behavior
        mock_driver.execute_script.return_value = 100  # Return a height change on scrolling
        scroll_page()  # Call the scroll_page function
        
        # Ensure scroll script was executed multiple times
        mock_driver.execute_script.assert_called_with("window.scrollTo(0, document.body.scrollHeight);")

    @patch('main.webdriver.Chrome')
    @patch('main.time.sleep')
    def test_extract_profile_data(self, MockSleep, MockChrome):
        # Mocking the WebDriver
        mock_driver = MagicMock()
        MockChrome.return_value = mock_driver
        
        # Mocking elements on the LinkedIn profile
        mock_driver.find_element.return_value.text = "John Doe"
        mock_driver.find_element.return_value.get_attribute.return_value = "https://example.com/image.jpg"
        mock_driver.find_elements.return_value = [MagicMock(), MagicMock()]
        mock_driver.find_elements()[0].find_element.return_value.text = "Software Engineer at XYZ"
        
        # Call the function to extract profile data
        profile_data = extract_profile_data("https://linkedin.com/testprofile")

        # Assert that the correct data was extracted
        self.assertEqual(profile_data["Name"], "John Doe")
        self.assertEqual(profile_data["Profile Image"], "https://example.com/image.jpg")
        self.assertIn("Software Engineer at XYZ", profile_data["Experience"])

    @patch('main.pd.DataFrame.to_csv')
    def test_save_to_csv(self, MockToCsv):
        # Simulate scraped data
        mock_data = [{
            "Name": "John Doe",
            "Job Title": "Software Engineer",
            "Profile Image": "test_image_url",
            "Experience": ["Software Engineer at XYZ"],
            "Education": ["Test University"],
            "Education Year": ["2022-2025"],
            "Licenses & Certifications": ["Certified Tester"],
            "Skills": ["Python"]
        }]

        # Call the save function
        save_to_csv(mock_data)

        # Verify that the to_csv function is called correctly
        MockToCsv.assert_called_with("LinkedIn_SCU_Alumni.csv", index=False)

if __name__ == "__main__":
    unittest.main()
