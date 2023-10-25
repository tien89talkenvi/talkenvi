from gtts import gTTS, gTTSError   
import time
import streamlit as st
import pybase64
from io import BytesIO

def gtts_text_to_speech(text_say,lang_say):
    audio_placeholder=st.empty()    #kdong 1 cho trong
    tts = gTTS(text_say, lang=lang_say)
    mp3_fp = BytesIO()  #kdong mp3_fp la doi tuong dang bytesio 
    tts.write_to_fp(mp3_fp) #tts ghi dl vao mp3_fp
    mp3_fp.seek(0)  #lay tu dau du lieu mp3_fp
    data = mp3_fp.read()
    b64 = pybase64.b64encode(data).decode()
    md = f"""
        <audio autoplay="true">
        <source src="data:audio/mp3;base64,{b64}" type="audio/ogg">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mpeg">
        Your browser does not support the audio tag.
        </audio>
        """
    audio_placeholder.empty()
    time.sleep(2) 
    audio_placeholder.markdown(md,unsafe_allow_html=True)

######################################
tienthu=st.button('TTTTTTTTTTTT')
if tienthu:
    gtts_text_to_speech(text_say='I am a teacher.',lang_say='en')

    gtts_text_to_speech(text_say='Tôi là người việt nam.',lang_say='vi')

    gtts_text_to_speech(text_say='Tôi từ Việt nam tới.',lang_say='vi')

    gtts_text_to_speech(text_say='I am being in Houston.',lang_say='en')

