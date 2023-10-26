#Gradio là một thư viện Python mã nguồn mở được sử dụng để xây dựng các ứng dụng web 
#và trình diễn khoa học dữ liệu và học máy.
#Với Gradio, bạn có thể nhanh chóng tạo giao diện người dùng đẹp mắt xung quanh các mô hình học máy 
#hoặc quy trình khoa học dữ liệu của mình và cho phép mọi người "dùng thử" bằng cách kéo và thả hình ảnh 
#của riêng họ, dán văn bản, ghi âm giọng nói của chính họ và tương tác với bản demo của bạn, 
#tất cả thông qua trình duyệt.
#gradio==3.50.2 pip install

#vdu co ban
#import gradio as gr
#def greet(name):
#    return "Hello " + name + "!"
#demo = gr.Interface(fn=greet, inputs="text", outputs="text")
#demo.launch()
###############

from gtts import gTTS
from io import BytesIO
import base64
import streamlit as st

def text_to_speech(text):
    tts = gTTS(text)
    tts.save('zz0.mp3')

    audio_bytes = BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)

    audio = base64.b64encode(audio_bytes.read()).decode("utf-8")
    audio_player = f'<audio src="data:audio/mpeg;base64,{audio}" controls autoplay></audio>'
    return audio_player   

########################
butt=st.button('Start')
if butt:
    text="I am a teacher."
    audio_player = text_to_speech(text)
    st.markdown(audio_player, unsafe_allow_html=True)
