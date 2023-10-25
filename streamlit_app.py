import streamlit as st
from gtts import gTTS
import os
import time
import base64

# Tiêu đề ứng dụng
st.title("Phát âm thanh từ văn bản")

# Ô nhập văn bản
text = st.text_area("Nhập văn bản", "Tôi là một giáo viên")

# Nút để phát âm thanh
if st.button("Phát âm thanh"):
    # Tạo đối tượng gTTS
    tts = gTTS(text,lang='vi')
    # Lưu tệp âm thanh tạm thời
    tts.save('temp.mp3')
    audio_placeholder=st.empty()
    
    with open('temp.mp3','rb') as f:
        data=f.read()
    b64 = base64.b64encode(data).decode()
    md = f"""
        <audio controles autoplay="true">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
    audio_placeholder.empty()
    time.sleep(0.5) 
    audio_placeholder.markdown(md,unsafe_allow_html=True)
    os.remove('temp.mp3')
