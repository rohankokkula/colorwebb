import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import webcolors
from collections import defaultdict

def rgba_to_hex(rgba):
    return "#{:02x}{:02x}{:02x}".format(rgba[0], rgba[1], rgba[2]).lower()

def named_to_hex(name):
    return webcolors.name_to_hex(name).lower()

def extract_colors_from_string(string, color_counter):
    if string:
        color_set = set(re.findall(r'#[0-9a-fA-F]{6}', string))
        
        for color in color_set:
            color_counter[color.lower()] += 1
        
        for rgba_match in re.findall(r'rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*[\d.]+)?\)', string):
            color_counter[rgba_to_hex(tuple(map(int, rgba_match)))] += 1
        
        for named_color_match in re.findall(r'\b\w+\b', string):
            try:
                color_counter[named_to_hex(named_color_match)] += 1
            except ValueError:
                pass
    
    return color_counter

def extract_inline_and_internal_styles(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    color_counter = defaultdict(int)

    for style_tag in soup.find_all('style'):
        color_counter = extract_colors_from_string(style_tag.string, color_counter)

    for element in soup.find_all(style=True):
        color_counter = extract_colors_from_string(element['style'], color_counter)

    return color_counter

def extract_external_styles(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    color_counter = defaultdict(int)

    for link_tag in soup.find_all('link', {'rel': 'stylesheet'}):
        href = link_tag.get('href')
        if href:
            if not href.startswith('http'):
                import urllib.parse
                href = urllib.parse.urljoin(url, href)
            stylesheet_content = requests.get(href).text
            color_counter = extract_colors_from_string(stylesheet_content, color_counter)
    
    return color_counter

st.title('Website Color Palette Extractor')

url = st.text_input('Enter Website URL:')

if url:
    if st.button('Extract Colors'):
        color_counter_internal = extract_inline_and_internal_styles(url)
        color_counter_external = extract_external_styles(url)
        
        # Combine the internal and external color counters
        color_counter = color_counter_internal
        for color, count in color_counter_external.items():
            color_counter[color] += count
        
        if color_counter:
            st.write('Color Palette:')
            wrapper_start = '<div style="display: flex; flex-wrap: wrap;">'
            wrapper_end = '</div>'
            color_boxes = []
            
            # Sort the color_counter dictionary by frequency (values), in descending order.
            sorted_colors = sorted(color_counter.items(), key=lambda x: x[1], reverse=True)
            
            for color, count in sorted_colors:
                color_box = f'<div style="flex: 1 1 calc(25% - 10px); margin: 5px; background: {color}; text-align: center;">' \
                            f'<div style="width: 100%; height: 100px;"></div>' \
                            f'<div style="width: 100%; background: #fff; color: #000; font-size: 12px;">{color} ({count})</div>' \
                            f'</div>'
                color_boxes.append(color_box)

            wrapped_color_boxes = wrapper_start + ''.join(color_boxes) + wrapper_end
            st.markdown(wrapped_color_boxes, unsafe_allow_html=True)
