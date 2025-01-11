from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re 
import pandas as pd
from selenium import webdriver

driver = webdriver.Chrome()  
wait = WebDriverWait(driver, 10)
url = "https://zoodex.ir/storesList/rafsanjan/resturant"
def save_links_to_file(links, file_name):
    """Save links to a file."""
    pd.DataFrame({"Links": list(links)}).to_csv(file_name, index=False)

def load_links_from_file(file_name):
    """Load links from a file."""
    if os.path.exists(file_name):
        return set(pd.read_csv(file_name)["Links"].tolist())
    return set()

try:
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(3)
    links_file = "links.csv"
    processed_links_file = "processed_links.csv"
    restaurant_links = load_links_from_file(links_file)
    processed_links = load_links_from_file(processed_links_file)
    restaurant_data = []
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        time.sleep(10)
        restaurants = driver.find_elements(By.CSS_SELECTOR, "a.store-card--wrapper.p-relative")
        
        for restaurant in restaurants:
            try:
                restaurant_link = restaurant.get_attribute("href")
                if "storeMenu" in restaurant_link and restaurant_link not in restaurant_links:
                    restaurant_links.add(restaurant_link)
                    print(f"Collected Link: {restaurant_link}")
                    save_links_to_file(restaurant_links, links_file)  
            except Exception as e:
                print(f"Error collecting link: {e}")
        
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(10)
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        time.sleep(15)
        if new_height == last_height:
            print("Reached the bottom of the page or no more content to load.")
            break
        last_height = new_height

    print(f"\nTotal links collected: {len(restaurant_links)}")

    unprocessed_links = restaurant_links - processed_links 
    for link in unprocessed_links:
        try:
            driver.get(link)
            time.sleep(5)

            try:
                time.sleep(10)
                span_element = driver.find_element(By.XPATH, '//span[@data-v-52c59304="" and contains(@class, "ellipsis-text")]')
                name = span_element.text.strip()
            except Exception:
                name = "Not Found"
            try:
                review_element = driver.find_element(By.XPATH, "//*[@id='app']/div/main/div/div/div/div/div/div/div/div[2]/div[1]/div[3]/div[1]/div[2]/div[3]/span/span[1]")
                number_of_reviews = review_element.text.strip()
                print(f"Number of Reviews: {number_of_reviews}")
            except Exception:
                number_of_reviews = "Not Found"
                print("No reviews found.")

            try:
                rating_element = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div/div/main/div/div/div/div/div/div/div/div[2]/div[1]/div[3]/div[1]/div[2]/div[1]/span[2]")
                rating = rating_element.text.strip()
                print(f"Rating: {rating}")
            except Exception:
                rating = "Not Found"
                print("No rating found.")
            try:
                    additional_click_element = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div/div/main/div/div/div/div/div/div/div/div[2]/div[2]/div[1]/div[2]/div/div[2]/div/a[2]/span")
                    additional_click_element.click()
                    print(f"Clicked on the additional element for '{name}'.")
                    
                    time.sleep(5)
            except Exception as e:
                    print(f"Error clicking the additional element for '{name}': {e}")
            try:
                location_link_element = driver.find_element(By.XPATH, "//a[@target='_blank' and contains(@class, 'bg-white') and contains(@href, 'google.com/maps')]")
                location_url = location_link_element.get_attribute("href")
                print(f"Location URL for '{name}': {location_url}")

                lat_lng_match = re.search(r"@(-?\d+\.\d+),(-?\d+\.\d+)", location_url)
                if lat_lng_match:
                    latitude = lat_lng_match.group(1)
                    longitude = lat_lng_match.group(2)
                    lat_long = f"{latitude}, {longitude}"
                    print(f"Latitude: {latitude}, Longitude: {longitude}")
                else:
                    lat_long = "Not Found"
                    print("Latitude and Longitude not found in URL.")
            except Exception as e:
                location_url = "Not Found"
                lat_long = "Not Found"
            restaurant_data.append({
                "Restaurant Name": name,
                "Rating": rating,
                "Number of Reviews": number_of_reviews,
                "Lat/Long URL": location_url,
                "Lat/Long": lat_long
            })

            processed_links.add(link)
            save_links_to_file(processed_links, processed_links_file)  

        except Exception as e:
            print(f"Error processing link {link}: {e}")

    if restaurant_data:
        df = pd.DataFrame(restaurant_data)
        print("\nCollected Restaurant Data:")
        print(df)

        chunk_size = 10
        try:
            for i in range(0, len(df), chunk_size):
                chunk = df.iloc[i:i + chunk_size]
                chunk_file_name = f"restaurant_data_chunk_{i // chunk_size + 1}.csv"
                chunk.to_csv(chunk_file_name, index=False)
                print(f"Chunk {i // chunk_size + 1} saved to '{chunk_file_name}'.")
        except Exception as e:
            print(f"Error saving data chunks: {e}")
    else:
        print("No data collected to save.")

finally:
    driver.quit()