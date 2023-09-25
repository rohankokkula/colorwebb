import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

def extract_inline_and_internal_styles(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    color_set = set()

    # Extracting colors from style tags
    for style_tag in soup.find_all('style'):
        color_set.update(re.findall(r'#[0-9a-fA-F]{6}|rgba?\(\d+,\d+,\d+(?:,[\d.]+)?\)', style_tag.string or ""))

    # Extracting colors from inline styles
    for element in soup.find_all(style=True):
        color_set.update(re.findall(r'#[0-9a-fA-F]{6}|rgba?\(\d+,\d+,\d+(?:,[\d.]+)?\)', element['style']))

    return color_set

def extract_external_styles(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    color_set = set()

    # Extracting colors from external stylesheets
    for link_tag in soup.find_all('link', {'rel': 'stylesheet'}):
        href = link_tag.get('href')
        if href:
            if not href.startswith('http'):
                import urllib.parse
                href = urllib.parse.urljoin(url, href)
            stylesheet_content = requests.get(href).text
            color_set.update(re.findall(r'#[0-9a-fA-F]{6}|rgba?\(\d+,\d+,\d+(?:,[\d.]+)?\)', stylesheet_content))
    
    return color_set

st.title('Website Color Palette Extractor')

url = st.text_input('Enter Website URL:')
if url:
    if st.button('Extract Colors'):
        colors = set()
        colors.update(extract_inline_and_internal_styles(url))
        colors.update(extract_external_styles(url))
        st.write('Color Palette:')
        for color in colors:
            st.write(color)
