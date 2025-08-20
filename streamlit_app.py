
import streamlit as st 
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import ast

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
<div class='top-bar'>
    <div><b>Vacos.de</b></div>
    <div>Delivering to Essen 45127 | EN | Account & Lists | Orders | 🛒</div>
</div>
""", unsafe_allow_html=True)

# --- Filter and Rank based on number of reviews ---
filtered_df = laptop_df.copy()

# Count number of non-empty reviews per laptop
def review_count(reviews):
    return sum(1 for r in str(reviews).split("||") if r.strip())

filtered_df["review_count"] = filtered_df["ReviewsN"].apply(review_count)

# Sort by number of reviews (desc), then rating
filtered_df = filtered_df.sort_values(by=["review_count", "ratingAvg"], ascending=[False, False])

# --- Pagination ---
st.sidebar.write(f"Filtered results: {len(filtered_df)} laptops")
items_per_page = 20
total_items = len(filtered_df)
total_pages = (total_items - 1) // items_per_page + 1

if "page" not in st.session_state:
    st.session_state.page = 1

prev_col, next_col = st.sidebar.columns(2)
if prev_col.button("⬅️") and st.session_state.page > 1:
    st.session_state.page -= 1
if next_col.button("➡️") and st.session_state.page < total_pages:
    st.session_state.page += 1

page = st.session_state.page
start_idx = (page - 1) * items_per_page
end_idx = start_idx + items_per_page
current_df = filtered_df.iloc[start_idx:end_idx]
st.sidebar.markdown(f"**Page {page} of {total_pages}**")

# --- Display Laptops ---
st.markdown("## Laptop Results – Sorted by Review Richness")

for _, row in current_df.iterrows():
    col1, col2, col3 = st.columns([1, 2, 2])

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

    with col2:
        st.markdown(f"<div class='product-title'>{row.get('titleStandard', 'No Title')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='product-detail'>⭐ {row.get('ratingAvgDisplay', '-')}/5 ({row.get('ratingNum', '0')} reviews)</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='price-block'>€{row.get('price', '-')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='product-detail'><b>Display Size:</b> {row.get('screenSize', '-')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='product-detail'><b>Hard disk:</b> {row.get('storageType', '-')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='product-detail'><b>CPU Speed:</b> {row.get('processorSpeedBase', '-')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='product-detail'><b>Memory:</b> {row.get('systemMemoryRam', '-')}</div>", unsafe_allow_html=True)
        st.link_button("Add to basket", row.get("productURL", "#"))

    with col3:
        reviews = str(row.get("ReviewsN", "")).split("||")
        if reviews:
            st.markdown("<div class='review-box'><b>User Reviews:</b>", unsafe_allow_html=True)
            for review in reviews[:5]:
                st.markdown(f"<div class='product-detail' style='color:blue;'>• {review.strip()}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
