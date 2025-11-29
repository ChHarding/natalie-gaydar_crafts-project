import pandas as pd
import streamlit as st


@st.cache_data
def load_data():
    return pd.read_csv(r"data\projects_craft.csv")


def get_by_user_input(craft_data):
    # First remove duplicate projects
    craft_data = craft_data.drop_duplicates(subset=['Project-Title'], keep='first')
    categories = ['3D Printing', 'Arduino', 'Art', 'Boats', 'Books & Journals', 
                'Cardboard', 'Cards', 'Christmas', 'Clay', 'Cleaning', 'Clocks', 'Costumes & Cosplay', 
                'Digital Graphics', 'Duct Tape', 'Embroidery', 'Fashion', 'Felt', 'Fiber Arts', 'Furniture', 'Gift Wrapping', 
                'Halloween', 'Holidays', 'Home Improvement', 'Jewelry', 'Kids', 'Knitting & Crochet', 'Knots', 'Launchers', 
                'Leather', 'Life Hacks', 'Mason Jars', 'Math', 'Metalworking', 'Molds & Casting', 'Music', 'No-Sew', 'Paper', 
                'Parties & Weddings', 'Photography', 'Printmaking', 'Relationships', 'Reuse', 'Science', 'Sewing', 'Soapmaking', 
                'Speakers', 'Tools', 'Toys & Games', 'Wallets', 'Water', 'Wearables', 'Woodworking']

    subcategory = st.selectbox("Category:", [""] + categories)
    if subcategory == "":
        subcategory = None

    number_of_results = st.slider("Number (1-20):", 1, 20, 5)

    choice = st.selectbox("Sort by:", ["Most Viewed", "Most Favorited"], index=0)
    sort_by_favorite = choice == "Most Favorited"

    if sort_by_favorite:
        sort_category = "Favorites"
    else:
        sort_category = "Views"

    if subcategory is not None:
        filtered_data = craft_data[craft_data['Subcategory'] == subcategory]
        top_viewed = filtered_data.nlargest(number_of_results, sort_category)
    else:
        top_viewed = craft_data.nlargest(number_of_results, sort_category) 
    
    # CH reindex the resulting DataFrame to have sequential indexes starting from 0
    top_viewed = top_viewed.reset_index(drop=True)

    return top_viewed