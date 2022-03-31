import streamlit as st
from config import SERVER, PORT, DEBUG
from helpers import search_by_text, resize_image, set_bg_hack_url
from widgets import title_widget, sidebar_widget


# NOTE: Must have indexed documents in "workspace" and also have jina-clip-streamlit/searcher/app.py actively running in another tab for this file to work

# ---------- Main area
title_widget(
    title="💉  Jina Tattoo Explorer", 
    background_url="https://i.pinimg.com/originals/3f/13/2e/3f132e57ddc000574d5bef0f39f124a5.gif"
)

# ---------- Sidebar
input_media = sidebar_widget()

# ---------- Wait for user inputs
if input_media == "text":
    text_query = st.text_input(label="Search term", placeholder="skulls")
    text_search_button = st.button("Search")
    if text_search_button:
        matches = search_by_text(text_query)
        st.success("success") # TODO: show time taken also here

# elif input_media == "image":
#     image_query = st.file_uploader(label="Image file")
#     image_search_button = st.button("Search")
#     if image_search_button:
#         matches = get_matches_from_image(
#             input=image_query,
#             limit=limit,
#             filters=filters,
#             server=server,
#             port=port,
#         )

if "matches" in locals():
    matches = [m for m in matches["@m"]]
    for match in matches:
        pic_cell, fname = st.columns([5, 3])
        image = resize_image(match.uri, resize_factor=3)
        pic_cell.image(image, use_column_width="auto")
        score = match.scores["cosine"].value
        fname.button(key=match.id, label=f"score: {score:.5f}")
        fname.write(" ")