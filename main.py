import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import webcolors
from collections import defaultdict, Counter

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

def is_greyscale(color):
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    return r == g == b

def identify_primary_secondary_colors(color_counter):
    non_greyscale_colors = {color: count for color, count in color_counter.items() if not is_greyscale(color)}
    sorted_colors = sorted(non_greyscale_colors.items(), key=lambda x: x[1], reverse=True)

    primary_color, secondary_colors, tertiary_colors = None, [], []
    if sorted_colors:
        primary_color = sorted_colors[0][0]
        secondary_colors = [color[0] for color in sorted_colors[1:3] if color]  # Next two frequent colors
        tertiary_colors = [color[0] for color in sorted_colors[3:] if color]  # All other colors

    return primary_color, secondary_colors, tertiary_colors


st.title('Website Color Palette Extractor')

url = st.text_input('Enter Website URL:', key='url_input')

if url:
    if st.button('Extract Colors', key='extract_button'):
        color_counter_internal = extract_inline_and_internal_styles(url)
        color_counter_external = extract_external_styles(url)

        color_counter = color_counter_internal
        for color, count in color_counter_external.items():
            color_counter[color] += count

        if color_counter:
            primary, secondary, tertiary = identify_primary_secondary_colors(color_counter)
            st.write(f'Primary Color: {primary}')
            st.write(f'Secondary Colors: {", ".join(secondary) if secondary else "None"}')
            st.write(f'Tertiary Colors: {", ".join(tertiary) if tertiary else "None"}')

            wrapper_start = '<div style="display: flex; flex-wrap: wrap;">'
            wrapper_end = '</div>'
            color_boxes = []

            sorted_colors = sorted(color_counter.items(), key=lambda x: x[1], reverse=True)
            
            for color, count in sorted_colors:
                color_box = f'''
    <div style="flex: 1 1 calc(25% - 10px); margin: 5px; cursor: pointer;" onclick="navigator.clipboard.writeText('{color}')">
        <div style="width: 100%; height: 100px; background: {color}; border-radius: 8px;"></div>
        <div style="width: 100%; background: #fff; color: #000; font-size: 12px; text-align: center; border-radius: 0px 0px 8px 8px;">{color} ({count})</div>
    </div>'''

                color_boxes.append(color_box)

            wrapped_color_boxes = wrapper_start + ''.join(color_boxes) + wrapper_end
            st.markdown(wrapped_color_boxes, unsafe_allow_html=True)
