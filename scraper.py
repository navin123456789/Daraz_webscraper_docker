"""
Simple Web Scraper for Daraz.com.np
This file contains the scraping functions to extract product information
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import re


def extract_products_from_page(driver):
    """
    Extract products from the current page
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        List of dictionaries with product info (name, price, sold)
    """
    products = []
    
    # Find product containers on the page
    product_selectors = [
        "div[data-qa-locator='product-item']",
        "div.box--ujueT",
        ".ant-col-xs-24",
        "div[class*='box--']",
        ".ant-col"
    ]
    
    # Try to find products using different selectors
    product_elements = []
    for selector in product_selectors:
        try:
            product_elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if len(product_elements) > 5:
                break
        except:
            continue
    
    # Extract information from each product
    for product in product_elements:
        try:
            # Extract product name
            name = None
            try:
                name_elem = product.find_element(By.CSS_SELECTOR, "a[title], .c16H9d, .c1Atzq")
                name = name_elem.text.strip() or name_elem.get_attribute("title")
            except:
                try:
                    links = product.find_elements(By.TAG_NAME, "a")
                    for link in links:
                        name = link.text.strip() or link.get_attribute("title")
                        if name and len(name) > 10:
                            break
                except:
                    pass
            
            # Extract price
            price = None
            try:
                price_elem = product.find_element(By.CSS_SELECTOR, "[class*='price'], .c3gUW0")
                price = price_elem.text.strip()
            except:
                # Try to find price in all text
                try:
                    all_text = product.text
                    price_match = re.search(r'Rs\.?\s*[\d,]+|NPR\s*[\d,]+', all_text)
                    if price_match:
                        price = price_match.group(0)
                except:
                    pass
            
            # Extract sold information
            sold = "N/A"
            try:
                sold_elem = product.find_element(By.CSS_SELECTOR, "[class*='sold']")
                sold = sold_elem.text.strip()
            except:
                try:
                    all_text = product.text
                    sold_match = re.search(r'(\d+\.?\d*[km]?\+?)\s*(sold|orders?)', all_text, re.IGNORECASE)
                    if sold_match:
                        sold = sold_match.group(0)
                except:
                    pass
            
            # Only add if we have name and price
            if name and price:
                products.append({
                    'name': name,
                    'price': price,
                    'sold': sold
                })
        except Exception as e:
            print(f"Error extracting product: {e}")
            continue
    
    return products


def scrape_daraz(search_query, max_results=100, max_pages=6, progress_callback=None):
    """
    Scrape Daraz.com.np for products across multiple pages
    
    Args:
        search_query: Product to search for (e.g., "facewash")
        max_results: Maximum number of products to return (default: 50)
        max_pages: Maximum number of pages to scrape (default: 3)
        progress_callback: Optional callback function(page, total_pages, product_count, status)
    
    Returns:
        List of product dictionaries
    """
    driver = None
    all_results = []
    seen_products = set()  # Track unique products to avoid duplicates
    
    try:
        # Setup Chrome browser
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in background
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')  # Added for cloud deployment
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # Avoid detection
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        print("Setting up Chrome browser...")
        if progress_callback:
            progress_callback(0, max_pages, 0, "Setting up browser...")
        
        # Try to use system Chromium (for cloud deployments) or fallback to ChromeDriverManager (for local)
        import os
        import glob
        
        # Check for environment variables first (Docker/Railway)
        chrome_bin = os.environ.get('CHROME_BIN')
        chromedriver_path = os.environ.get('CHROMEDRIVER_PATH')
        
        if chrome_bin and os.path.exists(chrome_bin):
            print(f"Using Chrome from environment: {chrome_bin}")
            chrome_options.binary_location = chrome_bin
            
            if chromedriver_path and os.path.exists(chromedriver_path):
                print(f"Using ChromeDriver from environment: {chromedriver_path}")
                service = Service(chromedriver_path)
            else:
                print("Using ChromeDriverManager")
                service = Service(ChromeDriverManager().install())
        else:
            # Try to find system installations
            chromium_paths = ['/usr/bin/chromium', '/usr/bin/chromium-browser', '/nix/store/*/bin/chromium']
            chromedriver_paths = ['/usr/bin/chromedriver', '/nix/store/*/bin/chromedriver']

            # Find chromium binary
            binary = None
            for path_pattern in chromium_paths:
                if '*' in path_pattern:
                    # Handle wildcard paths (for Nix store)
                    matches = glob.glob(path_pattern)
                    if matches:
                        binary = matches[0]
                        break
                elif os.path.exists(path_pattern):
                    binary = path_pattern
                    break
            
            # Find chromedriver
            driver_path = None
            for path_pattern in chromedriver_paths:
                if '*' in path_pattern:
                    matches = glob.glob(path_pattern)
                    if matches:
                        driver_path = matches[0]
                        break
                elif os.path.exists(path_pattern):
                    driver_path = path_pattern
                    break
            
            if binary:
                print(f"Using system chromium: {binary}")
                chrome_options.binary_location = binary
                if driver_path:
                    print(f"Using chromedriver: {driver_path}")
                    service = Service(driver_path)
                else:
                    print("Using ChromeDriverManager")
                    service = Service(ChromeDriverManager().install())
            else:
                # Local development - use ChromeDriverManager
                print("Using ChromeDriverManager for local development")
                service = Service(ChromeDriverManager().install())
        
        print("Initializing Chrome driver...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(30)  # Add timeout
        print("Chrome driver initialized successfully")
        
        # Go to Daraz homepage
        print("Opening Daraz.com.np...")
        if progress_callback:
            progress_callback(0, max_pages, 0, "Opening Daraz.com.np...")
        
        driver.get("https://www.daraz.com.np")
        time.sleep(2)  # Reduced from 3 to 2 seconds
        
        # Find search box and enter query
        print(f"Searching for: {search_query}")
        if progress_callback:
            progress_callback(0, max_pages, 0, f"Searching for '{search_query}'...")
        
        search_box = None
        
        # Try different selectors to find search box
        search_selectors = [
            "input[placeholder*='Search']",
            "input[type='search']",
            "input[name='q']",
            "#q",
            "input.search-box__input"
        ]
        
        for selector in search_selectors:
            try:
                print(f"Trying selector: {selector}")
                search_box = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                if search_box and search_box.is_displayed():
                    print(f"Found search box with selector: {selector}")
                    break
            except Exception as e:
                print(f"Selector {selector} failed: {str(e)[:50]}")
                continue
        
        if not search_box:
            print("ERROR: Could not find search box with any selector!")
            print("Trying direct URL method as fallback...")
            if progress_callback:
                progress_callback(0, max_pages, 0, "Using direct search URL...")
            
            # Fallback: Go directly to search results URL
            search_url = f"https://www.daraz.com.np/catalog/?q={search_query.replace(' ', '+')}"
            print(f"Navigating to: {search_url}")
            driver.get(search_url)
            time.sleep(3)
        else:
            # Enter search query and submit
            print(f"Entering search query: {search_query}")
            if progress_callback:
                progress_callback(0, max_pages, 0, f"Entering search query...")
            
            try:
                search_box.clear()
                search_box.send_keys(search_query)
                time.sleep(1)  # Brief pause
                search_box.send_keys(Keys.RETURN)
                print("Search query submitted successfully")
            except Exception as e:
                print(f"Error entering search query: {e}")
                raise Exception(f"Failed to enter search query: {str(e)}")
        
        # Wait for search results to load
        print("Waiting for results...")
        if progress_callback:
            progress_callback(1, max_pages, 0, "Loading search results...")
        
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='grid'], div[class*='product'], .ant-row"))
            )
            print("Search results loaded successfully")
        except Exception as e:
            print(f"Warning: Timeout waiting for results. Trying to continue anyway... {e}")
            # Take a screenshot for debugging if needed
            # driver.save_screenshot("debug_screenshot.png")
        
        time.sleep(2)  # Reduced from 3 to 2 seconds
        
        # Scrape pages
        page_number = 1
        
        # Loop through pages (primarily based on max_pages)
        while page_number <= max_pages:
            print(f"Scraping page {page_number}...")
            if progress_callback:
                progress_callback(page_number, max_pages, len(all_results), f"Scraping page {page_number}...")
            
            # Extract products from current page
            page_products = extract_products_from_page(driver)
            
            # Add unique products to results
            for product in page_products:
                # Create unique key from name and price
                product_key = (product['name'].strip().lower(), product['price'].strip())
                
                if product_key not in seen_products:
                    seen_products.add(product_key)
                    all_results.append(product)
                    
                    # Update progress with new product count
                    if progress_callback and len(all_results) % 5 == 0:  # Update every 5 products
                        progress_callback(page_number, max_pages, len(all_results), f"Found {len(all_results)} products...")
            
            # Safety check: if we have too many products, stop (but this shouldn't happen often)
            if len(all_results) >= max_results:
                print(f"Reached max_results limit: {len(all_results)}")
                break
            
            # Try to go to next page
            if page_number < max_pages:
                next_page_found = False
                try:
                    # Wait a bit for page to fully load
                    time.sleep(1.5)  # Reduced from 2 to 1.5 seconds
                    
                    # Scroll to bottom to ensure pagination is loaded
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1.5)  # Reduced from 2 to 1.5 seconds
                    
                    # Try multiple methods to find next page button
                    next_selectors = [
                        "li.ant-pagination-next:not(.ant-pagination-disabled) a",
                        "a[aria-label='Next Page']",
                        "a[aria-label='next']",
                        ".ant-pagination-next:not(.ant-pagination-disabled) a",
                        "li.ant-pagination-next a",
                        "a[title='Next Page']",
                        "a[title='next']",
                        ".ant-pagination-next a",
                        "li[class*='pagination-next']:not([class*='disabled']) a",
                        "a[class*='next']"
                    ]
                    
                    # Also try to find by text
                    try:
                        all_links = driver.find_elements(By.TAG_NAME, "a")
                        for link in all_links:
                            link_text = link.text.strip().lower()
                            link_aria = (link.get_attribute("aria-label") or "").lower()
                            link_class = (link.get_attribute("class") or "").lower()
                            
                            # Check if link has "next" text/symbol and is not disabled
                            if (('next' in link_text or '>' in link_text or 'next' in link_aria) and 
                                'disabled' not in link_class):
                                try:
                                    if link.is_displayed():
                                        driver.execute_script("arguments[0].scrollIntoView(true);", link)
                                        time.sleep(1)
                                        driver.execute_script("arguments[0].click();", link)
                                        next_page_found = True
                                        break
                                except:
                                    continue
                    except:
                        pass
                    
                    # Try CSS selectors
                    if not next_page_found:
                        for selector in next_selectors:
                            try:
                                next_button = driver.find_element(By.CSS_SELECTOR, selector)
                                # Check if button is not disabled
                                button_class = next_button.get_attribute("class") or ""
                                parent_class = ""
                                try:
                                    parent = next_button.find_element(By.XPATH, "..")
                                    parent_class = parent.get_attribute("class") or ""
                                except:
                                    pass
                                
                                if 'disabled' not in button_class.lower() and 'disabled' not in parent_class.lower():
                                    if next_button.is_displayed():
                                        # Scroll to button
                                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                                        time.sleep(1)
                                        
                                        # Try clicking
                                        try:
                                            next_button.click()
                                        except:
                                            driver.execute_script("arguments[0].click();", next_button)
                                        
                                        next_page_found = True
                                        break
                            except:
                                continue
                    
                    # Alternative: Try to construct next page URL
                    if not next_page_found:
                        try:
                            current_url = driver.current_url
                            next_page_num = page_number + 1
                            
                            # Check if URL has page parameter
                            if 'page=' in current_url or 'p=' in current_url:
                                # Extract and replace page number
                                import re
                                page_match = re.search(r'[?&](?:page|p)=(\d+)', current_url)
                                if page_match:
                                    # Replace existing page number
                                    new_url = re.sub(r'([?&])(?:page|p)=\d+', f'\\1page={next_page_num}', current_url)
                                else:
                                    # Add page parameter
                                    new_url = current_url + ('&' if '?' in current_url else '?') + f'page={next_page_num}'
                            else:
                                # Add page parameter
                                new_url = current_url + ('&' if '?' in current_url else '?') + f'page={next_page_num}'
                            
                            print(f"Trying URL method: {new_url}")
                            driver.get(new_url)
                            next_page_found = True
                        except Exception as e:
                            print(f"Error constructing URL: {e}")
                    
                    if next_page_found:
                        # Wait for new page to load
                        print(f"Navigating to page {page_number + 1}...")
                        time.sleep(3)  # Reduced from 4 to 3 seconds
                        
                        # Wait for products to load on new page
                        WebDriverWait(driver, 15).until(  # Reduced from 20 to 15 seconds
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='grid'], div[class*='product'], .ant-row, .box--"))
                        )
                        time.sleep(2)  # Reduced from 3 to 2 seconds
                        
                        page_number += 1
                        print(f"Successfully navigated to page {page_number}")
                    else:
                        print("No more pages found - cannot find next page button")
                        break
                        
                except Exception as e:
                    print(f"Error navigating to next page: {e}")
                    # Try URL method as fallback
                    try:
                        current_url = driver.current_url
                        next_page = page_number + 1
                        if 'page=' in current_url:
                            new_url = current_url.replace(f'page={page_number}', f'page={next_page}')
                        else:
                            new_url = current_url + ('&' if '?' in current_url else '?') + f'page={next_page}'
                        driver.get(new_url)
                        time.sleep(3)  # Reduced from 4 to 3 seconds
                        page_number += 1
                        print(f"Used URL method to navigate to page {page_number}")
                    except:
                        print("Could not navigate to next page")
                        break
            else:
                break
        
        print(f"Scraping complete! Found {len(all_results)} products from {page_number} page(s)")
        
    except Exception as e:
        print(f"Error during scraping: {e}")
    
    finally:
        # Close browser
        if driver:
            driver.quit()
    
    return all_results
