import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from webdriver_manager.chrome import ChromeDriverManager

# ===== Config =====
CREDENTIALS_FILE = "credentials.json"   # Google Sheets API JSON key file
SHEET_NAME = "Ecommerce Scraper Data"   # Sheet name

# ===== Google Sheet Init =====
def init_sheet(credentials_file, sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
    client = gspread.authorize(creds)
    try:
        sheet = client.open(sheet_name).sheet1
    except Exception:
        sheet = client.create(sheet_name).sheet1
    return sheet

# ===== Write Data to Google Sheet =====
def write_rows_to_sheet(sheet, rows):
    existing = sheet.get_all_values()
    if not existing:
        sheet.append_row(rows[0])
        data_rows = rows[1:]
    else:
        data_rows = rows
    for row in data_rows:
        sheet.append_row(row)
        time.sleep(1)

# ===== Selenium Driver Init =====
def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.set_window_size(1200, 1000)
    return driver

# ===== Scraper Function =====
def scrape_example_site(driver, keywords):
    url = f"https://www.daraz.com.bd/catalog/?q={keywords}"
    driver.get(url)
    time.sleep(3)

    products = []
    items = driver.find_elements(By.CSS_SELECTOR, ".Bm3ON")  # Container class
    for it in items[:20]:
        try:
            title = it.find_element(By.CSS_SELECTOR, ".RfADt").text.strip()
            price = it.find_element(By.CSS_SELECTOR, ".aBrP0").text.strip()
            link = it.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            products.append({'product': title, 'price': price, 'link': link})
        except Exception:
            continue
    return products

# ===== Main Function =====
def main():
    keyword = input("Enter the keyword: ").strip()
    driver = init_driver()  # Fixed: Removed CHROME_DRIVER_PATH
    sheet = init_sheet(CREDENTIALS_FILE, SHEET_NAME)
    
    rows = [["keyword", "site", "product", "price", "link"]]
    site_name = "Daraz"
    
    scraped = scrape_example_site(driver, keyword)
    for p in scraped:
        rows.append([keyword, site_name, p['product'], p['price'], p['link']])
    
    write_rows_to_sheet(sheet, rows)
    driver.quit()
    print("✅ Done! Data written to Google Sheet.")

if __name__ == "__main__":
    main()