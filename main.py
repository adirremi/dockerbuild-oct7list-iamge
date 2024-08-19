import psycopg2
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from time import sleep
import re

def is_valid_name(name):
    """Checks if the name is valid and does not contain a title or number instead of a name."""
    invalid_keywords = ["רס\"ר", "סגן", "טפסר", "סמל", "רס\"מ", "רס\"ל"]
    if any(keyword in name for keyword in invalid_keywords) or len(name.split()) < 2:
        return False
    return True

def parse_details(details):
    """Attempts to parse the age and city from the string."""
    try:
        match = re.search(r'בן (\d+) (.+)', details) or re.search(r'בת (\d+) (.+)', details)
        if match:
            age = int(match.group(1))
            city = match.group(2).strip()
            return age, city
        else:
            return None, 'Unknown'
    except (ValueError, IndexError):
        return None, 'Unknown'

def clean_and_split_name(name):
    """Cleans and splits the name if needed, handling 'Z"L' or other connecting words."""
    if "ז\"ל" in name:
        name_parts = name.split('ז"ל')
        name = name_parts[0].strip() + ' ז"ל'
    return name.strip()

def parse_age(details):
    """Attempts to parse the age from the string."""
    try:
        match = re.search(r'בן (\d+)', details) or re.search(r'בת (\d+)', details)
        if match:
            age = int(match.group(1))
            return age
        else:
            return None
    except (ValueError, IndexError):
        return None

# Connect to PostgreSQL database
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT", 5432)
)
cur = conn.cursor()

# Create table if it doesn't exist
cur.execute('''
CREATE TABLE IF NOT EXISTS fallen_soldiers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    city VARCHAR(255),
    age INTEGER,
    description TEXT
);
''')
conn.commit()

# Check if the 'description' column exists; if not, add it
cur.execute('''
SELECT column_name FROM information_schema.columns WHERE table_name='fallen_soldiers' AND column_name='description';
''')
if not cur.fetchone():
    cur.execute('''
    ALTER TABLE fallen_soldiers ADD COLUMN description TEXT;
    ''')
    conn.commit()

# Function to add a fallen soldier to the database if not already present
def add_fallen_soldier_to_db(name, city, age, description):
    cur.execute('''
    SELECT id FROM fallen_soldiers WHERE name = %s AND city = %s AND age = %s AND description = %s;
    ''', (name, city, age, description))
    result = cur.fetchone()
    if result is None:
        cur.execute('''
        INSERT INTO fallen_soldiers (name, city, age, description)
        VALUES (%s, %s, %s, %s);
        ''', (name, city, age, description))
        conn.commit()

# Selenium settings
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-extensions")
chrome_options.binary_location = "/usr/bin/google-chrome-stable"

# השתמש ב-ChromeDriver שהתקנת בקונטיינר
# הגדרת הנתיב למנהל ההתקן של Chrome
service = Service('/usr/bin/chromedriver')
driver = webdriver.Chrome(service=service, options=chrome_options)

#driver = webdriver.Chrome(options=chrome_options)

# Website URL
url = 'https://noflim.davar1.co.il/'
driver.get(url)

# Function to scroll down and store data
def scroll_and_store():
    last_height = driver.execute_script("return document.body.scrollHeight")
    printed_texts = set()  # Set to keep track of already printed texts

    i = 1
    while True:
        # Find all the cards with fallen soldier names
        #cards = driver.find_elements(By.CSS_SELECTOR, '#root > main > div > div.flex.w-full.flex-col.items-center.gap-4.overflow-y-scroll.pb-4.no-scrollbar.px-0.min-\[360px\]\:px-2 > div > a > div')
        cards = driver.find_elements(By.CSS_SELECTOR, r'#root > main > div > div.flex.w-full.flex-col.items-center.gap-4.overflow-y-scroll.pb-4.no-scrollbar.px-0.min-\[360px\]\:px-2 > div > a > div')

        if cards:
            for card in cards:
                try:
                    name = card.find_element(By.CSS_SELECTOR, 'div:nth-child(1) > div:nth-child(3)').text.strip()
                    details = card.find_element(By.CSS_SELECTOR, 'div:nth-child(1) > div:nth-child(4)').text.strip()
                    description = card.find_element(By.CSS_SELECTOR, 'div.text-xs.mt-auto').text.strip()

                    if not is_valid_name(name):
                        continue

                    age, city = parse_details(details)
                    age = age if age is not None else 'Unknown'

                except Exception as e:
                    print(f"Error extracting data: {e}", flush=True)
                    continue  # Continue if elements are not found

                combined_text = f"{name}, {city[1:]}, {age}, {description}"

                if combined_text not in printed_texts:
                    printed_texts.add(combined_text)
                    print(f"{i}. {combined_text}", flush=True)
                    i += 1
                    add_fallen_soldier_to_db(name, city[1:], age, description)

        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait for loading
        sleep(2)

        # Check new height of the page
        new_height = driver.execute_script("return document.body.scrollHeight")

        # Exit loop if height did not change
        if new_height == last_height:
            break

        last_height = new_height

# Scroll down and collect data
scroll_and_store()

# Close WebDriver and database connection
driver.quit()
cur.close()
conn.close()
