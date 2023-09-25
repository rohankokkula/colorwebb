import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import cssutils
import webcolors

def rgba_to_hex(rgba):
    return "#{:02x}{:02x}{:02x}".format(rgba[0], rgba[1], rgba[2]).lower()

def named_to_hex(name):
    return webcolors.name_to_hex(name).lower()


def extract_colors_from_string(string):
    color_set = set()
    if string:
        # Find hex colors
        color_set.update(re.findall(r'#[0-9a-fA-F]{6}', string))
        
        # Find rgb and rgba colors and convert them to hex
        for rgba_match in re.findall(r'rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*[\d.]+)?\)', string):
            color_set.add(rgba_to_hex(tuple(map(int, rgba_match))))
        
        # Find named colors and convert them to hex
        for named_color_match in re.findall(r'\b\w+\b', string):
            try:
                color_set.add(named_to_hex(named_color_match))
            except ValueError:  # Not a valid color name
                pass

    return color_set

def extract_inline_and_internal_styles(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    color_set = set()

    for style_tag in soup.find_all('style'):
        color_set.update(extract_colors_from_string(style_tag.string))

    for element in soup.find_all(style=True):
        color_set.update(extract_colors_from_string(element['style']))

    return color_set

def extract_external_styles(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    color_set = set()

    for link_tag in soup.find_all('link', {'rel': 'stylesheet'}):
        href = link_tag.get('href')
        if href:
            if not href.startswith('http'):
                import urllib.parse
                href = urllib.parse.urljoin(url, href)
            stylesheet_content = requests.get(href).text
            color_set.update(extract_colors_from_string(stylesheet_content))
    
    return color_set

st.title('Website Color Palette Extractor')

url = st.text_input('Enter Website URL:')
if url:
    if st.button('Extract Colors'):
        colors = set()
        colors.update(extract_inline_and_internal_styles(url))
        colors.update(extract_external_styles(url))
        
        if colors:
            st.write('Color Palette:')
            wrapper_start = '<div style="display: flex; flex-wrap: wrap;">'
            wrapper_end = '</div>'
            color_boxes = []
            
            for color in colors:
                color_box = f'<div style="flex: 1 1 calc(25% - 10px); margin: 5px; background: {color}; text-align: center;">' \
                            f'<div style="width: 100%; height: 100px;"></div>' \
                            f'<div style="width: 100%; background: #fff; color: #000; font-size: 12px;">{color}</div>' \
                            f'</div>'
                color_boxes.append(color_box)

            wrapped_color_boxes = wrapper_start + ''.join(color_boxes) + wrapper_end
            st.markdown(wrapped_color_boxes, unsafe_allow_html=True)
