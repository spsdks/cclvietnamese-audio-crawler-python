import streamlit as st
from crawl import process_url, download_file
import os
from stqdm import stqdm

st.title('AssessmentQ Crawler')

with st.form("my-form", clear_on_submit=True):
    url = st.text_input('Url', placeholder = 'Enter link')
    uploaded_files = st.file_uploader("Add urls file", type=['txt'], help="Each link sperate by endline", accept_multiple_files=True)
    submitted = st.form_submit_button("Crawl")

status = st.empty()
container = st.empty()

if submitted:

    urls = []
    
    if url:
        urls = [url]

    if uploaded_files:
        for uploaded_file in uploaded_files:
            container.text(f"Reading {uploaded_file.name}...")
            content = uploaded_file.read().decode("utf-8")
            lines = content.split('\n')
            urls.extend([line.strip() for line in lines if line.strip() != ""])

    urls = list(set(urls))
        
    datas = []
    for url in urls:
        container.text(f"Processing {url}...")
        data, save_path = process_url(url)
        datas.extend(data)

    os.makedirs(save_path, exist_ok=True)

    with status.container():
        st.success(f"Found {len(datas)} files!")

    for i, data in stqdm(enumerate(datas), total = len(datas)):
        container.text(f"Downloading {data[1]}...")
        download_file(data)
    
    with status.container():
        st.success("Downloaded all files!")

    container.empty()