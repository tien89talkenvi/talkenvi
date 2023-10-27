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
import time
def text_to_speech(text):
    tts = gTTS(text)
    #tts.save('zz0.mp3')

    audio_bytes = BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)

    audio_bs4 = base64.b64encode(audio_bytes.read()).decode("utf-8")
    audio_placeholder=st.empty()
    audio_placeholder.empty()
    audio_tag_str = f'<audio src="data:audio/mpeg;base64,{audio_bs4}" controls autoplay></audio>'
    audio_placeholder.markdown(audio_tag_str, unsafe_allow_html=True)
    time.sleep(3)
    audio_placeholder.empty()

########################
butt=st.button('Start')
if butt:
    text="I am a teacher."
    text_to_speech(text)
    text="I am learning English"
    text_to_speech(text)
