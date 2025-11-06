"""
Simple Streamlit App for Daraz Product Scraper
Modular and clean implementation with live updates
"""

import streamlit as st
import pandas as pd
from scraper import scrape_daraz
from ui_components import (
    apply_custom_css,
    render_header,
    render_sidebar,
    render_statistics,
    render_results_table,
    render_download_button,
    render_welcome_screen
)

# Page configuration
st.set_page_config(
    page_title="Daraz Product Scraper",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling
apply_custom_css()

# Render header
render_header()

# Render sidebar and get user inputs
search_query, max_pages, search_button = render_sidebar()

# Main content area
if search_button:
    if not search_query:
        st.warning("Please enter a product name to search")
    else:
        # Create placeholders for live updates
        status_placeholder = st.empty()
        progress_placeholder = st.empty()
        stats_placeholder = st.empty()
        
        # Progress callback function for live updates
        def update_progress(current_page, total_pages, product_count, status_message):
            """Update the UI with live scraping progress"""
            with status_placeholder:
                st.info(f"{status_message}")
            
            with progress_placeholder:
                progress = current_page / total_pages if total_pages > 0 else 0
                st.progress(progress, text=f"Page {current_page}/{total_pages}")
            
            with stats_placeholder:
                if product_count > 0:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("� Current Page", f"{current_page}/{total_pages}")
                    with col2:
                        st.metric("�️ Products Found", product_count)
        
        try:
            # Call scraper with progress callback
            results = scrape_daraz(
                search_query=search_query,
                max_results=1000,
                max_pages=max_pages,
                progress_callback=update_progress
            )
            
            # Clear progress indicators
            status_placeholder.empty()
            progress_placeholder.empty()
            stats_placeholder.empty()
            
            # Display results
            if results:
                st.success(f"Successfully scraped {len(results)} products!")
                
                # Display statistics
                render_statistics(results, max_pages)
                
                st.divider()
                
                # Create DataFrame
                df = pd.DataFrame(results)
                
                # Display results table with filters
                df_filtered = render_results_table(df)
                
                # Download button
                render_download_button(df_filtered, search_query)
            else:
                st.error("No products found. Please try a different search term.")
                
        except Exception as e:
            status_placeholder.empty()
            progress_placeholder.empty()
            stats_placeholder.empty()
            st.error(f"An error occurred: {str(e)}")
            st.info("Try again or reduce the number of pages.")

else:
    # Show welcome screen
    render_welcome_screen()

