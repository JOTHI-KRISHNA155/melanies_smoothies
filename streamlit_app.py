# Import python packages
import streamlit as st
import pandas as pd
import requests

# Page title
st.title("Customize Your Smoothie 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Name input
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be:", name_on_order)

# Snowflake connection (Cloud-safe)
conn = st.connection("snowflake")
session = conn.session()


# Query fruit options (NO Snowpark)
fruit_df = conn.query("""
    SELECT FRUIT_NAME, SEARCH_ON
    FROM SMOOTHIES.PUBLIC.FRUIT_OPTIONS
""")

# Multiselect expects a list
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        search_on = fruit_df.loc[
            fruit_df["FRUIT_NAME"] == fruit_chosen, "SEARCH_ON"
        ].iloc[0]

        st.write(f"🔍 Search value for {fruit_chosen}: {search_on}")

        st.subheader(f"{fruit_chosen} Nutrition Information")
        response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )
        st.dataframe(response.json(), use_container_width=True)

    # Insert query (SQL, not Snowpark)
    insert_sql = f"""
        INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    if st.button("Submit Order"):
        conn.query(insert_sql)
        st.success(f"Your Smoothie is ordered, {name_on_order}! ✅")
