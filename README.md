# SquareYards Apartment Scraper

This project scrapes apartment resale listings from SquareYards using Selenium for dynamic content loading and BeautifulSoup for HTML parsing. The scraper extracts up to the **top 100 Ready-to-Move apartment listings** including details such as apartment name, location, price (in rupees), image URL, and listing URL.

## Approach

SquareYards listings load dynamically and require scrolling and pagination. This scraper:

- Launches a Chrome browser using Selenium.
- Scrolls through the listing page to load all properties.
- Clicks the pagination buttons to move to the next page.
- Uses BeautifulSoup to parse the loaded HTML and extract required data.
- Converts price text (e.g., ₹65.25 L) into clean numeric rupee values (e.g., 6525000).
- Limits extraction to the first 100 listings for efficiency.
- Saves the data into a CSV file with numeric pricing for easy analysis.

## Setup Instructions

### Prerequisites

- Python 3.x
- Google Chrome browser
- [ChromeDriver](https://sites.google.com/chromium.org/driver/) (must match your Chrome version)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/squareyards-scraper.git
   cd squareyards-scraper
