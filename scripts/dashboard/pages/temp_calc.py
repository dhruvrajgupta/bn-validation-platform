import streamlit as st

st.sidebar.markdown("Temperature calculator")

st.markdown("Temperature calculator")
temp_var = st.number_input('enter celcius')
st.write(f'fahrenheit is: {temp_var*9/5+32}F')