import streamlit as st
from helpers import search_by_text, resize_image, search_by_image
from widgets import sidebar_widget, set_background_widget


# NOTE: Must have indexed documents in "workspace" AND also have jina-clip-streamlit/text_searcher/app.py AND jina-clip-streamlit/image_searcher/app.py actively running in two other tabs for this file to work

# ---------- Main area
set_background_widget(
    background_url="https://i.pinimg.com/originals/3f/13/2e/3f132e57ddc000574d5bef0f39f124a5.gif"
)
st.title("💉  Jina Tattoo Explorer")

# ---------- Sidebar
input_media = sidebar_widget()

# ---------- Wait for user inputs
if input_media == "text":
    text_query = st.text_input(label="Search term")
    text_search_button = st.button("Search")
    if text_search_button:
        matches = search_by_text(text_query)
        st.success("success")

elif input_media == "image":
    image_query = st.file_uploader(label="Image file")
    image_search_button = st.button("Search")
    if image_search_button:
        matches = search_by_image(image_query)
        st.success("success")

if "matches" in locals():
    matches = list(matches["@m"])
    for match in matches:
        print(match.uri)
        pic_cell, fname = st.columns([5, 3])
        image = resize_image(match.uri, resize_factor=3)
        
        pic_cell.image(image, use_column_width="auto")
        score = match.scores["cosine"].value
        
        fname.button(key=match.id, label=f"score: {score:.5f}")
        fname.write(" ")