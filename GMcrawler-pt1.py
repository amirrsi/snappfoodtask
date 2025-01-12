import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def setup_driver():
    """Sets up the Selenium WebDriver."""
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()))

def extract_data(driver, url):
    """Extracts data from the given URL using Selenium."""
    try:
        driver.get(url)
        time.sleep(6)  # Adjust the timing based on the website's response time

        # Example of data extraction, update these selectors based on your needs
        rating = driver.find_element(By.XPATH, '/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/span[1]/span[1]').text
        reviews = driver.find_element(By.XPATH, '/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/span[2]/span/span').text
        phone = driver.find_element(By.CSS_SELECTOR, '#QA0Szd > div > div > div.w6VYqd > div:nth-child(2) > div > div.e07Vkf.kA9KIf > div > div > div:nth-child(9) > div:nth-child(5) > button > div > div.rogA2c > div.Io6YTe.fontBodyMedium.kR99db.fdkmkc').text

        return rating, reviews, phone
    except Exception as e:
        print(f"Error while extracting data from {url}: {e}")
        return None, None, None  # Return None for each field in case of any error

def main():
    # Load CSV file
    df = pd.read_csv('restaurants.csv')  # Replace 'your_file.csv' with your actual file path

    # Setup WebDriver
    driver = setup_driver()

    # Initialize new columns
    df['Rating'] = ''
    df['Reviews'] = ''
    df['Phone'] = ''

    # Iterate through DataFrame rows
    for index, row in df.iterrows():
        url = row['Link']  # Adjust 'URL' based on your CSV column name
        rating, reviews, phone = extract_data(driver, url)

        # Store the extracted data in the DataFrame
        df.at[index, 'Rating'] = rating
        df.at[index, 'Reviews'] = reviews
        df.at[index, 'Phone'] = phone

    # Save the updated DataFrame back to CSV
    df.to_csv('updated_file.csv', index=False)  # Saves the data into a new file, you can overwrite the original if desired

    # Close the WebDriver
    driver.quit()

if __name__ == "__main__":
    main()
