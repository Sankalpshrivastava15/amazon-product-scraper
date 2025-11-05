# amazon-product-scraper

# amazon-product-scraper

A Python tool for scraping product details from Amazon listings, built by [@Sankalpshrivastava15](https://github.com/Sankalpshrivastava15).  
Currently supports basic extraction of product metadata — e.g., title, price, ratings — using simple HTTP requests (no API access).

---

## 🚀 Features

- Fetch product information (title, price, rating, number of reviews) from Amazon product pages.  
- Export scraped data to a CSV or JSON file (as per your script configuration).  
- Simple, lightweight, and easy to extend for custom scraping tasks.  
- Built purely in Python — no external scraping APIs required.

---

## 🧰 Getting Started

### Prerequisites  
- Python 3.7+ installed on your system.  
- A working internet connection (since the script sends HTTP requests to Amazon).  
- Optional: A virtual environment (recommended) to isolate dependencies.

### Installation  
```bash
# Clone the repository
git clone https://github.com/Sankalpshrivastava15/amazon-product-scraper.git
cd amazon-product-scraper

# (Optional) Create & activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

required modules for project
requests
beautifulsoup4
pandas
numpy
selenium
webdriver-manager
lxml
html5lib
streamlit
pyarrow
tqdm
fake-useragent
matplotlib
