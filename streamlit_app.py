import streamlit as st
import time
butt=st.button('Click on')
if butt:
    html_string = """
                <audio controls autoplay>
                <source src="https://media.w3.org/2010/07/bunny/04-Death_Becomes_Fur.mp4" type="audio/mp4">
                </audio>
                """
    sound = st.empty()
    sound.markdown(html_string, unsafe_allow_html=True)  # will display a st.audio with the sound you specified in the "src" of the html_string and autoplay it
    #time.sleep(2)  # wait for 2 seconds to finish the playing of the audio
    #sound.empty()  # optionally delete the element afterwards
