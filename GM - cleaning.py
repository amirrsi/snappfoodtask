import pandas as pd
import re
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
import scipy.stats as stats

dataset_path = "/Users/amirreisi/Documents/personal/snappfood project/final/raw-GM-.csv"
GMdata = pd.read_csv(dataset_path)
GMdata.head()
# Extracting lat o long 
def extract_lat_lon(url):
    pattern = r"!3d([-\d\.]+)!4d([-\d\.]+)"
    match = re.search(pattern, url)
    if match:
        return float(match.group(1)), float(match.group(2))
    return None, None

# Apply the function and create new columns
GMdata[['latitude', 'longitude']] = GMdata.apply(
    lambda row: pd.Series(extract_lat_lon(row['Link'])),
    axis=1
)
GMdata.head()

#Handling Duplicates
GMdata.drop_duplicates(inplace=True)

#REORDERING DataFrame
new_order = ['Name', 'Rating', 'Reviews', 'latitude', 'longitude','Link']
df = GMdata[new_order]