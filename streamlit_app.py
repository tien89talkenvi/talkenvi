import streamlit as st
import speech_recognition as sr #cho speech to txt
from googletrans import Translator #(phai update bang pip install googletrans-py )
from gtts import gTTS   #cho txt to speech
from io import BytesIO  #cho txt to speech
from IPython.display import Audio   #cho txt to speech
import base64   #cho txt to speech

def speech_to_text(lang):
    # Create a speech recognition object
    recognizer = sr.Recognizer()
    # Record speech using the microphone
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
    # Convert speech to text
    try:
        text = recognizer.recognize_google(audio, language=lang)
        #st.write(text)
        return text
    except sr.UnknownValueError:
        #st.write("Không thể xác định giọng nói.")
        return None
    except sr.RequestError as e:
        st.write(f"Lỗi: {e}")
        #return None
    
def textsrc_to_textdest(l_text, lang_src,lang_dest):
    translator = Translator()
    translation = translator.translate(l_text, src=lang_src, dest=lang_dest)
    #st.write(translation.text)
    return translation.text

def text_to_speech(text, lang='vi'):
    try:
        tts = gTTS(text, lang=lang)
        audio_io = BytesIO()
        tts.write_to_fp(audio_io)
        audio_io.seek(0)
        #st.success("Chuyển văn bản thành giọng nói thành công!")
        return audio_io
    except Exception as e:
        #st.error(f"Lỗi: {e}")
        return None


#######################################################
def main():
    st.subheader(":blue[Talk in Vietnamese and English]")
    vaichon = st.radio(":green[Select one of options:]", 
                    [":red[A.(Say Vi - Nói tiếng Việt):balloon:]", ":green[B.(Say En - Nói tiếng Anh):sunflower:]"], 
                    index=None,horizontal=True ) 
    st.write("---")
    if 'A.' in vaichon:
        st.write(":blue[Selected - Đã chọn:]", vaichon + ":blue[(Hãy nói gì đó...)]")
        lang="vi-VN"
        lang_src='vi'
        lang_dest='en'
    else:
        st.write(":blue[Selected - Đã chọn:]", vaichon + ":blue[(Say something...)]")
        lang="en_US"
        lang_src='en'
        lang_dest='vi'

    #B1: ghi am giong noi va chuyen thanh text
    l_text = speech_to_text(lang)
    st.write(l_text)
    #B2: dich sang text En hoac Vi
    if l_text is not None:
        txt_translated = textsrc_to_textdest(l_text, lang_src, lang_dest)
    st.write(txt_translated)

    audio_io = text_to_speech(txt_translated, lang_dest)
    st.audio(audio_io, format="audio/wav",start_time=0)

if __name__ == '__main__':
    main()
