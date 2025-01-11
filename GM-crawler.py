from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re 
import pandas as pd
from selenium import webdriver
import os

driver = webdriver.Chrome()  
wait = WebDriverWait(driver, 10)
url = "https://www.google.com/maps/search/%D8%B1%D8%B3%D8%AA%D9%88%D8%B1%D8%A7%D9%86+%D9%87%D8%A7%DB%8C+%D8%B1%D9%81%D8%B3%D9%86%D8%AC%D8%A7%D9%86%E2%80%AD/@30.394533,55.9582691,13z/data=!3m1!4b1?entry=ttu&g_ep=EgoyMDI1MDEwOC4wIKXMDSoASAFQAw%3D%3D"

def save_links_to_file(links, file_name):
    """Save links to a file."""
    pd.DataFrame({"Links": list(links)}).to_csv(file_name, index=False)

def load_links_from_file(file_name):
    """Load links from a file."""
    if os.path.exists(file_name):
        return set(pd.read_csv(file_name)["Links"].tolist())

try:
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(3)

    links_file = "GM-links.csv"
    processed_links_file = "GM-processed_links.csv"

    restaurant_links = load_links_from_file(links_file)
    processed_links = load_links_from_file(processed_links_file)

    GM_estaurant_data = []

    result_list = driver.find_element(By.XPATH, "/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]")
    last_height = driver.execute_script("return arguments[0].scrollHeight", result_list)
    
    while True:
        time.sleep(10)
        restaurants = driver.find_elements(By.CSS_SELECTOR, "a.hfpxzc") 

        for restaurant in restaurants:
            try:
                restaurant_link = restaurant.get_attribute("href")
                if "google.com/maps/place" in restaurant_link and restaurant_link not in restaurant_links:
                    restaurant_links.add(restaurant_link)
                    print(f"Collected Link: {restaurant_link}")
                    save_links_to_file(restaurant_links, links_file)  
            except Exception as e:
                print(f"Error collecting link: {e}")

        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", result_list)
        time.sleep(10)

        new_height = driver.execute_script("return arguments[0].scrollHeight", result_list)
        if new_height == last_height:
            print("Reached the bottom of the scrollable div or no more content to load.")
            break
        last_height = new_height

    print(f"\nTotal links collected: {len(restaurant_links)}")

    unprocessed_links = restaurant_links - processed_links  
    for link in unprocessed_links:
        try:
            driver.get(link)
            time.sleep(10)

            try:
                name_element = driver.find_element(By.XPATH, '//*[contains(@class, "DUwDvf lfPIob")]//*[contains(@class, "a5H0ec") or text()]')
                restaurant_name = name_element.text.strip()
                print(f"Restaurant Name: {restaurant_name}")
            except Exception as e:
                print(f"Error extracting restaurant name: {e}")


            try:
                review_element = driver.find_element(By.XPATH, '/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/span[2]/span/span')
                number_of_reviews = review_element.text.strip()
                print(f"Number of Reviews: {number_of_reviews}")
            except Exception:
                number_of_reviews = "Not Found"
                print("No reviews found.")

            try:
                rating_element = driver.find_element(By.XPATH, '/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/span[1]/span[1]')
                rating = rating_element.text.strip()
                print(f"Rating: {rating}")
            except Exception:
                rating = "Not Found"
                print("No rating found.")

            # Extract location URL and latitude/longitude
            try:
                location_link_element = driver.find_element(By.XPATH, "//a[@target='_blank' and contains(@class, 'bg-white') and contains(@href, 'google.com/maps')]")
                location_url = location_link_element.get_attribute("href")
                print(f"Location URL: {location_url}")

                lat_lng_match = re.search(r"@(-?\d+\.\d+),(-?\d+\.\d+)", location_url)
                if lat_lng_match:
                    latitude = lat_lng_match.group(1)
                    longitude = lat_lng_match.group(2)
                    lat_long = f"{latitude}, {longitude}"
                    print(f"Latitude: {latitude}, Longitude: {longitude}")
                else:
                    lat_long = "Not Found"
            except Exception as e:
                location_url = "Not Found"
                lat_long = "Not Found"
                print(f"Error extracting location link: {e}")

            GM_restaurant_data.append({
                "Restaurant Name": restaurant_name,
                "Rating": rating,
                "Number of Reviews": number_of_reviews,
                "Lat/Long URL": location_url,
                "Lat/Long": lat_long
            })

            processed_links.add(link)
            save_links_to_file(processed_links, processed_links_file)  

        except Exception as e:
            print(f"Error processing link {link}: {e}")

    if GM_restaurant_data:
        df = pd.DataFrame(GM_restaurant_data)
        print("\nCollected Restaurant Data:")
        print(df)

        chunk_size = 10
        for i in range(0, len(df), chunk_size):
            chunk = df.iloc[i:i + chunk_size]
            chunk_file_name = f"GM_restaurant_data_chunk_{i // chunk_size + 1}.csv"
            chunk.to_csv(chunk_file_name, index=False)
            print(f"Chunk {i // chunk_size + 1} saved to '{chunk_file_name}'.")
    else:
        print("No data collected to save.")

finally:
    driver.quit()
