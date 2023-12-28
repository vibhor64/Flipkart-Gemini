import bardapi
import streamlit as st
import main
import socket
import csv
import geocoder
import google.generativeai as genai

# Set up BARD AI API credentials
# token = 'dQgXUuYI8k6yct8ovVUjv3vCAJQqaDUZp0XDUDu9U2ZA_iyFMU2WUgPHczdpZ5CBnovCrg.'
# Under Inspect element, go to applications, select the token inside "__Secure-1PSID"

# The genai package also supports the PaLM family of models
GOOGLE_API_KEY='AIzaSyDbQus67GYsqO6k10dlif8wwoGgdIw2X54'
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

st.title("Product Review Summarizer")
review = st.text_area("Enter the link:")

def get_geolocation():
    try:
        g = geocoder.ip('me')
        return g
    except Exception as e:
        st.error(f"Error fetching geolocation data: {e}")
        return None

def storeData(item_name, response):
    # Get IP Address
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    # print("ip address: ", ip_address, item_name)

    # Get User-Agent
    user_agent="NaN"
    try:
        user_agent = st.report_thread.get_report_ctx().enqueue(lambda: st.server.server.Server.get_current()._ctx.request.headers.get("User-Agent")).result()
    except Exception as e:
        pass
    
    # Get Geolocation
    location_data = get_geolocation()
    if location_data:
        with open('data.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([ip_address, item_name, user_agent, response, location_data.lat, location_data.lng, location_data.city,location_data.state,location_data.country])
        return 
       
    with open('data.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([ip_address, item_name, user_agent, response])
     

if st.button("Summarize"):
        if review:
            item_name, rating_list, review_text = main.scrapeFlip(review)
            if not review_text: 
                print('No reviews found, our product rating might not be accurate...')
                st.error('No reviews found, our product rating might not be accurate...')
                item_name = str(item_name)
                prompt = str("I found this item on Flipkart named" + item_name + "Summarize this product based off its ratings and product description within 30 lines. Be sure to generate a table containing pros and cons of this product, and also give a score out of 10 wheather one should buy this product or not.")
                print("Waiting for Gemini ⏳")
                # response = bardapi.core.Bard(token).get_answer(prompt)
                response = model.generate_content(prompt)
                response = response.text
                storeData(item_name, response)
                st.write(response)
                print("Target Demolished 🔥")
            else:
                if rating_list:
                    rating_str = ", ".join(str(rating) for rating in rating_list)
                else: rating_str = ''
                review_str = ",".join(str(review) for review in review_text)
                item_name = str(item_name)
                prompt = str("I found this item on Flipkart named " + item_name + "Summarize these flipkart reviews based off its product ratings, description on its webpage, within 30 lines. Be sure to generate a table containing pros and cons of this product"+"The reviews are: " + review_str + "and their respective ratings are:"+ rating_str + "and also give a score out of 10 wheather one should buy this product or not. Keep in mind it is a flipkart product.")           

                print("Waiting for Gemini ⏳")
                # response = bardapi.core.Bard(token).get_answer(prompt)
                response = model.generate_content(prompt)
                response = response.text
                storeData(item_name, response)
                st.write(response)
                print("Target Demolished 🔥")
        else:
            st.warning("Please provide a valid link")
            
# streamlit run c:\Users\vibho\Documents\Coding\Python\flipkartScrape\app.py
