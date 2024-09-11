import streamlit as st
import time
import concurrent.futures

# Function that takes time to run
def long_computation(n):
    time.sleep(n)  # Simulating a long-running computation
    return f"Completed after {n} seconds!"

# A wrapper function to execute the task in the background
def run_in_background(fn, *args):
    with concurrent.futures.ProcessPoolExecutor() as executor:
        future = executor.submit(fn, *args)
        return future

# Streamlit app
st.title("Non-blocking Long Computation")

# Button to trigger the long computation
if st.button("Run Long Computation"):
    st.write("Computation started...")

    # Submit the function to run in the background
    # future = run_in_background(long_computation, 5)
    # print(future.done())

    with st.spinner("Computing... Please wait..."):
        # Polling in a loop while waiting for the computation to finish
        # while not future.done():
        #     # time.sleep(0.1)  # Allow time for future to run
        #     print(future.done())
        #     pass
        future = run_in_background(long_computation, 5)
        print(future.done())
        st.write("dadasda")

    # Get the result when it's done
    result = future.result()
    st.text(result)

st.write("Streamlit is still responsive while the function runs.")
