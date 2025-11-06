"""
UI Components for Daraz Product Scraper
Modular components for better code organization
"""

import streamlit as st
import pandas as pd


def apply_custom_css():
    """Apply custom CSS styling to the app"""
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #F85606;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        .sub-header {
            text-align: center;
            color: #666;
            margin-bottom: 2rem;
        }
        .stDownloadButton button {
            background-color: #F85606;
            color: white;
        }
        .stDownloadButton button:hover {
            background-color: #d94805;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.8rem;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)


def render_header():
    """Render the app header"""
    st.markdown('<h1 class="main-header">🛍️ Daraz Product Scraper</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Search and analyze products from Daraz.com.np</p>', unsafe_allow_html=True)


def render_sidebar():
    """Render sidebar with search settings"""
    with st.sidebar:
        st.header("Settings")
        
        # Search query input
        search_query = st.text_input(
            "Enter product name",
            placeholder="e.g., facewash, laptop, phone",
            help="Enter the product you want to search for"
        )
        
        # Maximum pages
        max_pages = st.slider(
            "Number of pages to scrape",
            min_value=1,
            max_value=10,
            value=2,
            step=1,
            help="More pages = more products but slower scraping"
        )
        
        # Show estimated time
        estimated_time = max_pages * 6
        st.caption(f"Estimated time: ~{estimated_time} seconds")
        
        # Search button
        search_button = st.button("🔎 Search Products", type="primary", use_container_width=True)
        
        # Divider
        st.divider()
        
        # Tips section
        with st.expander("Tips for Better Results"):
            st.markdown("""
            - Use specific product names
            - Start with 2-3 pages
            - Filter results after scraping
            - Download CSV for analysis
            """)
        
    return search_query, max_pages, search_button


def render_statistics(results, max_pages):
    """Render statistics cards"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Products", len(results))
    
    with col2:
        st.metric("Pages Scraped", max_pages)
    
    with col3:
        try:
            prices = [r['price'] for r in results if r['price']]
            st.metric("With Price", len(prices))
        except:
            st.metric("Products", len(results))


def render_results_table(df):
    """Render the results table with filters"""
    st.subheader("Product Results")
    
    # Add filter option
    col_filter1, col_filter2 = st.columns([3, 1])
    with col_filter1:
        search_filter = st.text_input("🔍 Filter by product name", "", key="filter", placeholder="Type to filter results...")
    
    # Apply filter if provided
    if search_filter:
        df_filtered = df[df['name'].str.contains(search_filter, case=False, na=False)]
        st.caption(f"Showing {len(df_filtered)} of {len(df)} products")
    else:
        df_filtered = df
    
    # Display table
    st.dataframe(
        df_filtered,
        use_container_width=True,
        hide_index=True,
        column_config={
            "name": st.column_config.TextColumn(
                "Product Name",
                width="large"
            ),
            "price": st.column_config.TextColumn(
                "Price",
                width="medium"
            ),
            "sold": st.column_config.TextColumn(
                "Sold",
                width="small"
            )
        },
        height=400
    )
    
    return df_filtered


def render_download_button(df, search_query):
    """Render download button"""
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download Results as CSV",
            data=csv,
            file_name=f"daraz_{search_query}_results.csv",
            mime="text/csv",
            use_container_width=True
        )


def render_welcome_screen():
    """Render welcome screen with instructions"""
    st.info("Enter a product name in the sidebar and click 'Search Products' to start")
    
    # Quick guide
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Quick Start")
        st.markdown("""
        1. Enter product name in sidebar
        2. Select pages
        3. Click "Search Products"
        4. View live updates & results
        """)
    
    with col2:
        st.markdown("### Features")
        st.markdown("""
        - **Live Updates** - See progress in real-time
        - **Smart Filtering** - Find products quickly
        - **CSV Export** - Download for analysis
        - **Clean UI** - Easy to use interface
        """)


def show_live_progress(current_page, total_pages, product_count):
    """Show live scraping progress"""
    progress = current_page / total_pages
    
    # Progress bar
    st.progress(progress, text=f"Scraping page {current_page} of {total_pages}")
    
    # Live stats
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Current Page", f"{current_page}/{total_pages}")
    with col2:
        st.metric("Products Found", product_count)
