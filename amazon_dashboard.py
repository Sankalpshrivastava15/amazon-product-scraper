import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from bs4 import BeautifulSoup
import time

# Page config
st.set_page_config(
    page_title="Amazon Product Scraper Dashboard",
    page_icon="🛒",
    layout="wide"
)

# Your ScraperAPI key
API_KEY = 'f9600874b3ccbcc25ed7f2dc93be0b81'

def scrape_amazon(search_query, max_pages=3):
    """Scrape Amazon using ScraperAPI"""
    all_products = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for page in range(1, max_pages + 1):
        status_text.text(f"Scraping page {page} of {max_pages}...")
        
        url = f"https://www.amazon.in/s?k={search_query}&page={page}"
        payload = {
            'api_key': API_KEY,
            'url': url,
            'country_code': 'in'
        }
        
        try:
            response = requests.get('https://api.scraperapi.com/', params=payload, timeout=60)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                products = soup.find_all('div', {'data-component-type': 's-search-result'})
                
                for product in products:
                    try:
                        title_elem = product.select_one('h2 a.a-link-normal span')
                        if not title_elem:
                            title_elem = product.select_one('h2 span')
                        title = title_elem.get_text(strip=True) if title_elem else None
                        
                        price_elem = product.select_one('span.a-price:nth-of-type(1) span.a-offscreen')
                        if not price_elem:
                            price_elem = product.select_one('span.a-price-whole')
                        price = price_elem.get_text(strip=True) if price_elem else "N/A"
                        
                        link_elem = product.select_one('h2 a.a-link-normal')
                        link = "https://www.amazon.in" + link_elem['href'] if link_elem and link_elem.get('href') else "N/A"
                        
                        img_elem = product.select_one('img.s-image')
                        image = img_elem['src'] if img_elem and img_elem.get('src') else "N/A"
                        
                        rating_elem = product.select_one('span.a-icon-alt')
                        rating = rating_elem.get_text(strip=True) if rating_elem else "N/A"
                        
                        if title:
                            all_products.append({
                                'Title': title,
                                'Price': price,
                                'Rating': rating,
                                'URL': link,
                                'Image': image
                            })
                    except Exception as e:
                        continue
            
            progress_bar.progress(page / max_pages)
            time.sleep(1)
        
        except Exception as e:
            st.error(f"Error on page {page}: {e}")
    
    status_text.text("Scraping complete!")
    return all_products

# Dashboard UI
st.title("🛒 Amazon India Product Scraper")
st.markdown("Search and analyze Amazon products with real-time scraping")

# Sidebar
with st.sidebar:
    st.header("Search Settings")
    search_query = st.text_input("Search Query", value="laptop", help="Enter product to search")
    max_pages = st.slider("Number of Pages", 1, 5, 3, help="Each page ~20-30 products")
    
    scrape_button = st.button("🔍 Start Scraping", type="primary", use_container_width=True)

# Main content
if scrape_button:
    with st.spinner("Scraping Amazon..."):
        products = scrape_amazon(search_query, max_pages)
    
    if products:
        df = pd.DataFrame(products)
        
        # Extract numeric price
        df['Price_Numeric'] = df['Price'].str.extract(r'([\d,]+\.?\d*)')[0].str.replace(',', '')
        df['Price_Numeric'] = pd.to_numeric(df['Price_Numeric'], errors='coerce')
        
        # Metrics at top
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Products", len(df))
        with col2:
            st.metric("Avg Price", f"₹{df['Price_Numeric'].mean():,.0f}")
        with col3:
            st.metric("Min Price", f"₹{df['Price_Numeric'].min():,.0f}")
        with col4:
            st.metric("Max Price", f"₹{df['Price_Numeric'].max():,.0f}")
        
        st.markdown("---")
        
        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Charts", "🗂️ Data Table", "🖼️ Product Cards", "📥 Export"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                # Price distribution
                fig1 = px.histogram(df, x='Price_Numeric', nbins=20, 
                                   title='Price Distribution',
                                   labels={'Price_Numeric': 'Price (₹)'})
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                # Top 10 by price
                top10 = df.nlargest(10, 'Price_Numeric')[['Title', 'Price_Numeric']]
                top10['Title_Short'] = top10['Title'].str[:30]
                fig2 = px.bar(top10, x='Price_Numeric', y='Title_Short',
                             orientation='h', title='Top 10 Most Expensive')
                st.plotly_chart(fig2, use_container_width=True)
        
        with tab2:
            # Searchable table
            st.subheader("Product Data Table")
            search = st.text_input("🔍 Filter products", "")
            if search:
                filtered_df = df[df['Title'].str.contains(search, case=False, na=False)]
            else:
                filtered_df = df
            
            st.dataframe(
                filtered_df[['Title', 'Price', 'Rating']],
                use_container_width=True,
                height=500
            )
        
        with tab3:
            # Product cards with images
            st.subheader("Product Gallery")

            # Show more products option
            num_products = st.slider("Number of products to display", 6, len(df), 12, step=3)

            cols = st.columns(3)
            for idx, row in df.head(num_products).iterrows():
                with cols[idx % 3]:
                    # Product image
                    if row['Image'] != "N/A":
                        st.image(row['Image'], use_container_width=True)
                    else:
                        st.info("No image available")

                    # Product title
                    st.markdown(f"**{row['Title'][:70]}**")

                    # Price and rating
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown(f"💰 **{row['Price']}**")
                    with col_b:
                        st.markdown(f"⭐ {row['Rating']}")

                    # Clickable Amazon link button
                    if row['URL'] != "N/A" and row['URL'] != "#":
                        # Use markdown link if st.link_button is not available
                        st.markdown(f"[🛒 View on Amazon]({row['URL']})")

                    st.divider()


        
        with tab4:
            # Export options
            st.subheader("Export Data")
            
            col1, col2 = st.columns(2)
            with col1:
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"amazon_{search_query}_{time.strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                json = df.to_json(orient='records', indent=2)
                st.download_button(
                    label="📥 Download JSON",
                    data=json,
                    file_name=f"amazon_{search_query}_{time.strftime('%Y%m%d')}.json",
                    mime="application/json",
                    use_container_width=True
                )
    else:
        st.error("❌ No products found. Try a different search query.")

else:
    # Show instructions when not scraping
    st.info("👈 Enter a search query and click 'Start Scraping' to begin")
    
    st.markdown("""
    ### How to Use:
    1. Enter a product name in the sidebar (e.g., "laptop", "headphones", "camera")
    2. Select how many pages to scrape (each page = ~20-30 products)
    3. Click "Start Scraping" and wait for results
    4. Explore charts, tables, and product cards
    5. Export data as CSV or JSON
    
    ### Features:
    - 📊 Interactive price charts
    - 🔍 Searchable product table
    - 🖼️ Visual product gallery
    - 📥 CSV/JSON export
    """)
