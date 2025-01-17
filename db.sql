CREATE TABLE company_data (
    name TEXT,
    gm_rate DOUBLE PRECISION,
    zoodex_rating DOUBLE PRECISION,
    zoodex_review DOUBLE PRECISION,
    gm_review DOUBLE PRECISION,
    zoodex_csat DOUBLE PRECISION,
    gm_csat DOUBLE PRECISION,
    zoodex_normalized_csat DOUBLE PRECISION,
    gm_normalized_csat DOUBLE PRECISION,
    final_csat DOUBLE PRECISION,
    cluster INTEGER,
    class TEXT
);
\COPY final_restaurant_data FROM '/Users/amirreisi/Documents/personal/snappfood project/final/final_restaurant_data.csv' WITH (FORMAT csv, HEADER);
df = pd.read_csv(path)
conn = sqlite3.connect('restaurantsdata.db')
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS CSAT;")
cursor.execute("DROP TABLE IF EXISTS Review;")
cursor.execute("DROP TABLE IF EXISTS Rate;")
cursor.execute("DROP TABLE IF EXISTS Restaurant;")

cursor.execute("DROP TABLE IF EXISTS CSAT;")
cursor.execute("DROP TABLE IF EXISTS Review;")
cursor.execute("DROP TABLE IF EXISTS Rate;")
cursor.execute("DROP TABLE IF EXISTS Restaurant;")

# Creating tables
create_restaurant_table = """
CREATE TABLE Restaurant (
    Restaurant_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT,
    Location TEXT
);
"""

create_rate_table = """
CREATE TABLE Rate (
    Rate_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Restaurant_ID INTEGER,
    Rate REAL,
    Rate_normalized REAL,
    FOREIGN KEY (Restaurant_ID) REFERENCES Restaurant (Restaurant_ID)
);
"""

create_review_table = """
CREATE TABLE Review (
    Review_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Restaurant_ID INTEGER,
    Review INTEGER,
    Review_normalized REAL,
    FOREIGN KEY (Restaurant_ID) REFERENCES Restaurant (Restaurant_ID)
);
"""

create_csat_table = """
CREATE TABLE CSAT (
    CSAT_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Restaurant_ID INTEGER,
    CSAT REAL,
    Normalized_CSAT REAL,
    Cluster INTEGER,
    Class TEXT,
    FOREIGN KEY (Restaurant_ID) REFERENCES Restaurant (Restaurant_ID)
);
"""

cursor.execute(create_restaurant_table)
cursor.execute(create_rate_table)
cursor.execute(create_review_table)
cursor.execute(create_csat_table)


# Insert data to table
restaurants = df[['Name', 'Location']]
restaurants.to_sql('Restaurant', conn, if_exists='append', index=False)

restaurant_ids = pd.read_sql_query("SELECT rowid, Name FROM Restaurant", conn)
restaurant_ids.rename(columns={'rowid': 'Restaurant_ID'}, inplace=True)
df_merged = df.merge(restaurant_ids, on='Name', how='left')

rate_data = df_merged[['Restaurant_ID', 'Rate', 'Rate_normalized']]
rate_data.to_sql('Rate', conn, if_exists='append', index=False)

review_data = df_merged[['Restaurant_ID', 'Review', 'Review_normalized']]
review_data.to_sql('Review', conn, if_exists='append', index=False)

csat_data = df_merged[['Restaurant_ID', 'CSAT', 'Normalized_CSAT', 'Cluster', 'Class']]
csat_data.to_sql('CSAT', conn, if_exists='append', index=False)

conn.commit()
