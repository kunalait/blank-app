import streamlit as st 
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import ast
import random

# Load dataset
file_path = "categorized_reviews_output.csv"
laptop_df = pd.read_csv(file_path)
laptop_df.columns = laptop_df.columns.str.strip()

# --- Extract GB values ---
def extract_gb(value):
    try:
        if isinstance(value, str) and "gigabyte" in value:
            return int(value.split()[0])
        elif isinstance(value, str) and "GB" in value:
            return int(value.split("GB")[0].strip())
    except:
        return None
    return value

laptop_df["RAM"] = laptop_df["systemMemoryRam"].apply(extract_gb)
laptop_df["Storage"] = laptop_df["totalStorageCapacity"].apply(extract_gb)

# --- Page Setup ---
st.set_page_config(layout="wide")

# --- Top Bar ---
st.markdown("""
<style>
.top-bar {
    background-color: #232f3e;
    color: white;
    padding: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.search-box input {
    width: 100%;
    padding: 5px;
}
.product-title {
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 5px;
}
.product-detail {
    font-size: 14px;
    margin-bottom: 4px;
}
.price-block {
    font-size: 20px;
    color: #B12704;
    font-weight: bold;
    margin-top: 8px;
    margin-bottom: 8px;
}
.review-box {
    background-color: #f6f6f6;
    padding: 10px;
    border-radius: 5px;
    margin-top: 10px;
    margin-bottom: 10px;
}
.scroll-container {
    display: flex;
    overflow-x: auto;
    gap: 10px;
}
</style>
<div class="top-bar">
    <div><b>Vacos.de</b></div>
    <div class="search-box"><input type="text" placeholder="Search (disabled in study version)" disabled></div>
    <div>Delivering to Essen 45127 | EN | Account & Lists | Orders | 🛒</div>
</div>
""", unsafe_allow_html=True)

# --- Bottom-right floating button ---
st.markdown("""
<style>
.fixed-bottom-right {
    position: fixed;
    bottom: 30px;
    right: 30px;
    background-color: #ff914d;
    color: white;
    padding: 10px 20px;
    border-radius: 8px;
    font-weight: bold;
    box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    text-align: center;
    z-index: 9999;
}
.fixed-bottom-right:hover {
    background-color: #e67300;
}
</style>
<a href="https://www.soscisurvey.de/prodpurp/index.php?i=ZO8Z3FJQ09XL&rnd=UITP" target="_self">
    <div class="fixed-bottom-right">Next ➡️</div>
</a>
""", unsafe_allow_html=True)

# --- Sidebar: Filters (locked) ---
st.sidebar.header("Filter by (locked):")
st.sidebar.markdown("🔒 The filters below are visible but disabled for this study.")
st.sidebar.slider("Max Price", 50, 1500, 1000, disabled=True)
st.sidebar.slider("Minimum Rating", 0.0, 5.0, 3.0, 0.1, disabled=True)
st.sidebar.slider("Minimum RAM (GB)", 2, 32, 4, disabled=True)

# ---- REMOVE PURPOSE SELECTION: always show all ----
filtered_df = laptop_df.copy()
st.info("Showing all laptops (purpose selection removed for the study).")

# --- Sort (no purpose ranking) ---
# If ratingAvg is missing, fill with 0 to avoid sort errors
filtered_df["ratingAvg"] = pd.to_numeric(filtered_df.get("ratingAvg", 0), errors="coerce").fillna(0)
filtered_df = filtered_df.sort_values(by=["ratingAvg"], ascending=False)

# --- Pagination ---
st.sidebar.write(f"Filtered results: {len(filtered_df)} laptops")
items_per_page = 20
total_items = len(filtered_df)
total_pages = (total_items - 1) // items_per_page + 1

if "page" not in st.session_state:
    st.session_state.page = 1

prev_col, next_col = st.sidebar.columns(2)
with prev_col:
    if st.button("⬅️ Previous") and st.session_state.page > 1:
        st.session_state.page -= 1
with next_col:
    if st.button("Next ➡️") and st.session_state.page < total_pages:
        st.session_state.page += 1

page = st.session_state.page
start_idx = (page - 1) * items_per_page
end_idx = start_idx + items_per_page
current_df = filtered_df.iloc[start_idx:end_idx]
st.sidebar.markdown(f"**Page {page} of {total_pages}**")

# --- Display Laptops ---
st.markdown("## Laptop Results")

for _, row in current_df.iterrows():
    col1, col2, col3 = st.columns([1, 2, 2])

    # --- Column 1: Images ---
    with col1:
        try:
            img_urls = ast.literal_eval(row["imageURLs"]) if isinstance(row["imageURLs"], str) else []
            if img_urls:
                st.markdown("<div class='scroll-container'>", unsafe_allow_html=True)
                for img_url in img_urls:
                    try:
                        img_data = requests.get(img_url).content
                        st.image(Image.open(BytesIO(img_data)), width=120)
                    except:
                        st.markdown("<div class='product-detail'>[Image not available]</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
        except:
            st.markdown("<div class='product-detail'>[Invalid image format]</div>", unsafe_allow_html=True)

    # --- Column 2: Product Info ---
    with col2:
        st.markdown(f"<div class='product-title'>{row.get('titleStandard', 'No Title')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='product-detail'>⭐ {row.get('ratingAvgDisplay', '-')}/5 ({row.get('ratingNum', '0')} reviews)</div>", unsafe_allow_html=True)
        st.markdown("<div class='product-detail'><b>Limited time deal</b></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='price-block'>€{row.get('price', '-')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='product-detail'><b>Display Size:</b> {row.get('screenSize', '-')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='product-detail'><b>Hard disk:</b> {row.get('storageType', '-')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='product-detail'><b>CPU Speed:</b> {row.get('processorSpeedBase', '-')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='product-detail'><b>Memory:</b> {row.get('systemMemoryRam', '-')}</div>", unsafe_allow_html=True)
        st.link_button("Add to basket", row.get("productURL", "#"))

    # --- Column 3: Reviews (no purpose highlighting) ---
    with col3:
        good_reviews = row.get("ReviewsN", "")
        snippets = []

        if isinstance(good_reviews, str) and good_reviews.strip():
            review_list = good_reviews.split("||")
            for review in review_list:
                review = review.strip()
                if review:
                    snippets.append((review, ''))  # plain style

        if snippets:
            st.markdown("<div class='review-box'><b>What users say:</b>", unsafe_allow_html=True)
            for snip, style in snippets[:5]:
                st.markdown(f"<div class='product-detail' style='{style}'>• {snip}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

# --- Download Button ---
st.download_button(
    label="Download Filtered CSV",
    data=filtered_df.to_csv(index=False).encode('utf-8'),
    file_name="filtered_laptops.csv",
    mime="text/csv"
)
