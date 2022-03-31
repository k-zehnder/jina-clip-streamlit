import streamlit as st
from helpers import set_bg_hack_url


def set_background_widget(background_url):
    set_bg_hack_url(background_url)

def sidebar_widget():
    st.sidebar.title("Options")

    input_media = st.sidebar.radio(label="Search with...", options=["text", "image"])

    st.sidebar.markdown(
        """This example lets you use a *textual* description to search through *images* of tattoos using [Jina](https://github.com/jina-ai/jina/).
        """
    )

    st.sidebar.markdown(
        "[Repo link](https://github.com/k-zehnder/jina-clip-streamlit)"
    )
    return input_media

    