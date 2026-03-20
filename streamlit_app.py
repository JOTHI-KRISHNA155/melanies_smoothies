# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# App Title
st.title("Customize your Smoothie 🍓")

st.write("Choose fruits and place your smoothie order.")

# Name input
name_on_order = st.text_input('Name on Smoothie')

# Checkbox for order filled
order_filled = st.checkbox('Order Filled')

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit options
my_dataframe = session.table("smoothies.public.fruit_options") \
                      .select(col('FRUIT_NAME'))

# Multiselect fruits
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)

# If fruits selected
if ingredients_list:

    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string = ' '.join(ingredients_list)

        st.subheader(fruit_chosen + " Nutrition Information")

        response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + fruit_chosen
        )

        st.dataframe(data=response.json(), use_container_width=True)

    # Submit button
    submit = st.button('Submit Order')

    if submit:

        filled_value = 'TRUE' if order_filled else 'FALSE'

        insert_sql = f"""
        INSERT INTO smoothies.public.orders
        (ingredients, name_on_order, order_filled, order_ts)
        VALUES
        ('{ingredients_string}', '{name_on_order}', {filled_value}, CURRENT_TIMESTAMP)
        """

        session.sql(insert_sql).collect()

        st.success('Your Smoothie Order has been placed!', icon="✅")
