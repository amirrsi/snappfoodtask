from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
import time

# Setup WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Navigate to the URL
url = 'https://www.google.com/maps/search/restaurant+in+rafsanjan/@30.3886458,55.9236979,13z/data=!4m2!2m1!6e5?entry=ttu&g_ep=EgoyMDI1MDEwOC4wIKXMDSoASAFQAw%3D%3D'
driver.get(url)

# Wait for the page to load initially
time.sleep(5)

# Find the scrollable result list by XPATH
result_list = driver.find_element(By.XPATH, "/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]")
last_height = driver.execute_script("return arguments[0].scrollHeight", result_list)

# Data collection
restaurant_data = []

while True:
    time.sleep(10)  # Wait for possible dynamic content to load

    # Locate all restaurant links and names in the scrollable div
    restaurants = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "hfpxzc"))
                )
    for restaurant in restaurants:
        try:
            # Extract the restaurant link from the 'href' attribute
            restaurant_link = restaurant.get_attribute("href")
            # Extract the restaurant name
            restaurant_name = restaurant.get_attribute("aria-label")
            print(f"Restaurant Name: {restaurant_name}")
            # Check if the link is valid and the data is not already collected
            if "google.com/maps/place" in restaurant_link and all(restaurant_link != rd['Link'] for rd in restaurant_data):
                restaurant_data.append({"Name": restaurant_name, "Link": restaurant_link})
                print(f"Collected: {restaurant_name} - {restaurant_link}")

        except Exception as e:
            print(f"Error collecting data: {e}")

    # Scroll the scrollable div
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", result_list)
    time.sleep(10)

    # Check if new content has loaded
    new_height = driver.execute_script("return arguments[0].scrollHeight", result_list)
    time.sleep(10)

    if new_height == last_height:
        print("Reached the bottom of the scrollable div or no more content to load.")
        break
    last_height = new_height

# Save the data in a DataFrame
df = pd.DataFrame(restaurant_data)
print(df)

# Optional: Save DataFrame to CSV
df.to_csv('restaurants.csv', index=False)

# Close the browser
driver.quit()

