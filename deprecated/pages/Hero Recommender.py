import sys
sys.path.insert(0,'..')

import streamlit as st
import dota_functions

st.title('Looking for new heroes to try?')

with st.form(key='account_id_form'):
	text_input = st.text_input(label='Enter your Dota account id (example - 191312823)')
	submit_button = st.form_submit_button(label='Recommend heroes for me!')

st.write("Here are your top 3 hero recommendations")

if submit_button:
	
    st.dataframe(data=dota_functions.recommendation_wrapper(int(float(text_input)), query_period=30))
