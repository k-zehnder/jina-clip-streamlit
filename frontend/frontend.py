import streamlit as st
from config import (
    SERVER,
    PORT,
    DEBUG,
)
from helpers import search_by_text, get_client, resize_image

# NOTE: Must have indexed documents in "workspace" and also have beta-jina-first/searcher/app.py actively running in another tab for this file to work


title = "👕 Multimodal fashion search with Jina"

st.set_page_config(page_title=title, layout="wide")

# Sidebar
st.sidebar.title("Options")

input_media = st.sidebar.radio(label="Search with...", options=["text", "image"])

#
st.sidebar.title("About")

st.sidebar.markdown(
    """This example lets you use a *textual* description to search through *images* of fashion items using [Jina](https://github.com/jina-ai/jina/).
#### Why are the images so pixelated?
To speed up indexing, we indexed relatively low-resolution graphics. We're looking at hosting hi-res images elsewhere and showing those instead. But for the purposes of a tech demo it seems like overkill.
"""
)

st.sidebar.markdown(
    "[Repo link](https://github.com/alexcg1/jina-multimodal-fashion-search)"
)

# Main area
st.title(title)

if input_media == "text":
    text_query = st.text_input(label="Search term", placeholder="Blue dress")
    text_search_button = st.button("Search")
    if text_search_button:
        c = get_client()
        matches = search_by_text(c, 'video games')
        # print(matches)

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
    # print(matches.summary())
    print(f'[INFO] printing match uris...')
    print([m.uri for m in matches["@m"]])

    matches = [m for m in matches["@m"]]
    for match in matches:
        pic_cell, desc_cell, price_cell = st.columns([1, 6, 1])

        image = resize_image(match.uri, resize_factor=3)

        pic_cell.image(image, use_column_width="auto")
        # desc_cell.markdown(
        #     f"##### {match.tags['productDisplayName']} {print_stars(match.tags['rating'])}"
        # )
        # desc_cell.markdown(
        #     f"*{match.tags['masterCategory']}*, *{match.tags['subCategory']}*, *{match.tags['articleType']}*, *{match.tags['baseColour']}*, *{match.tags['season']}*, *{match.tags['usage']}*, *{match.tags['year']}*"
        # )
        # price_cell.button(key=match.id, label=str(match.tags["price"]))