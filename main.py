import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

def extract_colors(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    style_tags = soup.find_all('style')
    color_set = set()
    for tag in style_tags:
        colors = re.findall(r'#[0-9a-fA-F]{6}|rgba?\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*(?:,\s*[\d.]+)?\)|\b\w+\b', tag.string)
        color_set.update(colors)
    return color_set

st.title('Website Color Palette Extractor')

url = st.text_input('Enter Website URL:')
if url:
    if st.button('Extract Colors'):
        colors = extract_colors(url)
        st.write('Color Palette:')
        st.write(colors)
