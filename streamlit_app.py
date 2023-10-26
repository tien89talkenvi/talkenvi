from gtts import gTTS, gTTSError   
import time
import streamlit as st
import base64
from io import BytesIO



def gtts_text_to_speech(text_say,lang_say):
    audio_placeholder=st.empty()    #kdong 1 cho trong
    tts = gTTS(text_say, lang=lang_say)
    mp3_fp = BytesIO()  #kdong mp3_fp la doi tuong dang bytesio 
    tts.write_to_fp(mp3_fp) #tts ghi dl vao mp3_fp
    mp3_fp.seek(0)  #lay tu dau du lieu mp3_fp
    data = mp3_fp.read()
    b64 = base64.b64encode(data).decode('utf-8') 
    audio_tag = f'<audio autoplay="true" src="data:audio/wav;base64,{b64}">' 
    audio_placeholder.empty()
    time.sleep(2) 
    audio_placeholder.markdown(audio_tag,unsafe_allow_html=True)

######################################
tienthu=st.button('TTTTTTTTTTTT')
if tienthu:
    gtts_text_to_speech(text_say='I am a teacher.',lang_say='en')

    gtts_text_to_speech(text_say='Tôi là người việt nam.',lang_say='vi')

    gtts_text_to_speech(text_say='Tôi từ Việt nam tới.',lang_say='vi')

    gtts_text_to_speech(text_say='I am being in Houston.',lang_say='en')




