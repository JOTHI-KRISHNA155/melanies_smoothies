# Import python packages
import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

# App title
st.title("Customize Your Smoothie 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Name input
name_on_order = st.text_input("Name on Smoothie:")

# Order filled checkbox (VERY IMPORTANT FOR DORA)
order_filled = st.checkbox("Order Filled")

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit options table
my_dataframe = session.table("smoothies.public.fruit_options") \
                      .select(col("FRUIT_NAME"), col("SEARCH_ON"))

# Convert to pandas for SEARCH_ON lookup
pd_df = my_dataframe.to_pandas()

# Multiselect fruits
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

# If fruits selected
if ingredients_list:

    # IMPORTANT → build exact string (no trailing space)
    ingredients_string = " ".join(ingredients_list).strip()

    # Show nutrition info
    for fruit_chosen in ingredients_list:

        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen, "SEARCH_ON"
        ].iloc[0]

        st.subheader(f"{fruit_chosen} Nutrition Information")

        response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )

        st.dataframe(response.json(), use_container_width=True)

    # Submit button
    submit = st.button("Submit Order")

    if submit:

        filled_value = "TRUE" if order_filled else "FALSE"

        insert_sql = f"""
        INSERT INTO smoothies.public.orders
        (ingredients, name_on_order, order_filled, order_ts)
        VALUES
        ('{ingredients_string}', '{name_on_order}', {filled_value}, CURRENT_TIMESTAMP)
        """

        session.sql(insert_sql).collect()

        st.success(f"Your Smoothie is ordered, {name_on_order}! ✅")
