import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time


def convert_price_to_number(price_str):
    if not price_str:
        return 0
    price_str = price_str.replace('₹', '').replace(',', '').strip().upper()
    try:
        if 'CR' in price_str:
            value = float(price_str.replace('CR', '').strip())
            return int(value * 1_00_00_000)
        elif 'L' in price_str:
            value = float(price_str.replace('L', '').strip())
            return int(value * 1_00_000)
        elif 'K' in price_str:
            value = float(price_str.replace('K', '').strip())
            return int(value * 1_000)
        else:
            return int(float(price_str))
    except:
        return 0


def scrape_apartments_from_html(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    listings = soup.find_all('article', class_='listing-card')
    print(f"Found {len(listings)} listings on this page.")
    data = []

    for listing in listings:
        try:
            name_tag = listing.find('span', class_='project-name')
            apartment_name = name_tag.text.strip() if name_tag else "N/A"

            location_tag = listing.find('div', class_='favorite-btn')
            location = location_tag.get('data-locality', 'N/A') if location_tag else "N/A"

            price_tag = listing.find('p', class_='listing-price').find('strong')
            price = price_tag.text.strip() if price_tag else "N/A"
            min_price = max_price = convert_price_to_number(price)

            photo_tag = listing.find('figure', class_='listing-img').find('img')
            photo_url = photo_tag['src'].strip() if photo_tag and 'src' in photo_tag.attrs else "N/A"

            listing_url_tag = listing.find('h2', class_='heading').find('a')
            listing_url = listing_url_tag['href'].strip() if listing_url_tag and 'href' in listing_url_tag.attrs else "N/A"

            data.append({
                'Apartment Name': apartment_name,
                'Location': location,
                'Minimum Price': min_price,
                'Maximum Price': max_price,
                'Photo URL': photo_url,
                'Listing URL': listing_url
            })

        except Exception as e:
            print(f"Skipping listing due to error: {e}")
            continue

    return pd.DataFrame(data)


if __name__ == "__main__":
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")

    service = Service("C:/Users/musab/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    target_url = "https://www.squareyards.com/resale/search?buildingType=1&propertyType=1&propertyTypeName=Apartment&possessionStatus=Ready%20To%20Move&cityId=5"
    driver.get(target_url)
    time.sleep(3)

    all_data = []
    page_number = 1
    max_pages = 20

    while page_number <= max_pages:
        print(f"\nProcessing Page {page_number}...")

        last_height = driver.execute_script("return document.body.scrollHeight")
        for _ in range(10):
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(1.2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        html_content = driver.page_source
        df = scrape_apartments_from_html(html_content)

        new_listings = df.to_dict(orient="records")
        remaining_slots = 100 - len(all_data)

        if remaining_slots <= 0:
            print("Reached 100 listings limit. Stopping.")
            break

        if len(new_listings) > remaining_slots:
            all_data.extend(new_listings[:remaining_slots])
            print("Collected 100 listings. Stopping.")
            break
        else:
            all_data.extend(new_listings)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        next_page = page_number + 1
        try:
            selector = f'li.applyPagination[data-page="{next_page}"]'
            next_button = driver.find_element(By.CSS_SELECTOR, selector)
            driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
            time.sleep(1)

            print(f"Clicking pagination button for page {next_page}...")
            next_button.click()
            page_number += 1
            time.sleep(3)
        except Exception as e:
            print(f"No pagination found for page {next_page}. Ending. ({e})")
            break

    driver.quit()

    if all_data:
        final_df = pd.DataFrame(all_data)
        final_df.to_csv("apartments_data.csv", index=False, encoding="utf-8")
        print(f"\nSaved {len(final_df)} listings to 'apartments_data.csv' (prices saved as numbers)")
        print(final_df.head())
    else:
        print("No listings scraped.")
