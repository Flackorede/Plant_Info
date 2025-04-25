import streamlit as st
import requests
import os

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

def get_plant_info(plant_name):
    url = "https://api.together.xyz/v1/completions"
    prompt = f"Give me concise, interesting information about the plant '{plant_name}'. Include its common uses, appearance, and any unique facts."
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "meta-llama/Llama-3-8b-chat-hf",
        "prompt": prompt,
        "max_tokens": 300,
        "temperature": 0.7,
        "top_p": 0.9
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        res_json = response.json()
        if "choices" in res_json and len(res_json["choices"]) > 0:
            return res_json["choices"][0]["text"].strip()
        else:
            return "No information found for this plant."
    except Exception as e:
        return f"Error: {e}"

st.set_page_config(page_title="Plant Info Finder", page_icon="🌱", layout="centered")

st.title("🌱 Plant Info Finder")
plant_name = st.text_input("Enter a plant name:")
if st.button("Get Info"):
    if plant_name.strip() == "":
        st.warning("Please enter a plant name.")
    else:
        with st.spinner("Fetching info from Together.ai..."):
            info = get_plant_info(plant_name)
        st.success("Plant Information:")
        st.write(info)
st.markdown("---")
st.caption("Powered by Together.ai LLM • Built with Streamlit • Hosted on Render")
