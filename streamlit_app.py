import streamlit as st
import pandas as pd
from snowflake.snowpark.functions import col
import requests

# App header
st.title("Customize Your Smoothie 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Snowflake connection (Streamlit in Snowflake)
cnx = st.connection("snowflake")
session = cnx.session()

# Name input
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be:", name_on_order)

# Pull fruit data (THIS MUST MATCH THE LAB)
my_dataframe = (
    session
    .table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))
)

# Create pandas version (REQUIRED for SEARCH_ON lookup)
pd_df = my_dataframe.to_pandas()

# Multiselect MUST use Snowpark dataframe (NOT a list)
ingredients_list = st.multiselect(
    "Choose upto 5 ingredients:",
    my_dataframe,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        # Build ingredients string EXACTLY like the lab
        ingredients_string += fruit_chosen + " "

        # Lookup SEARCH_ON from table (lab requirement)
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        st.write(
            "The search value for ",
            fruit_chosen,
            " is ",
            search_on,
            "."
        )

        st.subheader(fruit_chosen + " Nutrition Information")

        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )

        st.dataframe(
            smoothiefroot_response.json(),
            width="stretch"
        )

    # INSERT STATEMENT — DO NOT CHANGE FORMAT
    my_insert_stmt = """
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('""" + ingredients_string + """', '""" + name_on_order + """')
    """

    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(
            f"Your Smoothie is ordered, {name_on_order}!",
            icon="✅"
        )
