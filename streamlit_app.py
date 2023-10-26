import streamlit as st
import streamlit.components.v1 as components  # Import Streamlit

def play_auto(data_audio):
    components.html(f"<html><body><h1>Auto play music</h1><audio controls autoplay><source src={data_audio} type='audio/mpeg'></audio></body></html>", width=600, height=200)

# Render the h1 block, contained in a frame of size 200x200.
#components.html("<html><body><h1>Hello, World</h1><audio controls autoplay><source src='out.mp3' type='audio/ogg'></audio></body></html>", width=200, height=200)
butt=st.button('Click to start')
if butt:
    data_audio='https://media.w3.org/2010/07/bunny/04-Death_Becomes_Fur.mp4'
    play_auto(data_audio)
