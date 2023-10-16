#streamlit==1.27.2
#SpeechRecognition==3.10.0
#pyaudio==0.2.13 #(cho SpeechRecognition lay micro )
#googletrans==4.0.0rc1 #(phien ban nay cho rieng py khi su dung googletrans, cac pban khac hay gay loi)
#gTTS==2.4.0


#https://talkenvi-b5vypm7itcecxnkuvne7h9.streamlit.app/ 
#la url app moi talkenvi
import streamlit as st
import speech_recognition as sr 
#import pyaudio
from googletrans import Translator 
from gtts import gTTS   
from io import BytesIO  
import sounddevice as sd
import wavio


#from IPython.display import Audio   #cho txt to speech
#import base64   #cho txt to speech

def speech_to_text(lang):
    # Create a speech recognition object
    recognizer = sr.Recognizer()
    # Record speech using the microphone
    fs = 44100  # Tần số mẫu (số mẫu trên giây)
    duration = 5  # Thời gian ghi âm (s)

    #st.write("(Đang ghi âm...)")
    audio_data = sd.rec(int(fs * duration), samplerate=fs, channels=2, dtype="float32")
    sd.wait()
    wavio.write('a.wav', audio_data, fs, sampwidth=2)
    #st.write("(Hoàn thành ghi âm.)")

    #with sr.Microphone() as source:
    #    audio = recognizer.listen(source)
    # Convert speech to text
    wav_file='a.wav'
    audio_file = sr.AudioFile(wav_file)
    with audio_file as source:
        audio_data = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio_data, language=lang)
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
st.subheader(":blue[Trò chuyện bằng tiếng Việt, Anh - Talk in Vietnamese, English]")
vaichon = st.radio(":green[Select one of options:]", 
                [":red[A.(Say Vi - Nói tiếng Việt):balloon:]", ":green[B.(Say En - Nói tiếng Anh):sunflower:]","STOP"], 
                index=2,horizontal=True ) 

st.write("---")
if vaichon == ":red[A.(Say Vi - Nói tiếng Việt):balloon:]":
    st.write(":blue[Selected - Đã chọn:]", ":red[A.(Say Vi - Nói tiếng Việt):balloon:]" + ":blue[(Hãy nói gì đó...)]")
    lang="vi-VN"
    lang_src='vi'
    lang_dest='en'
elif vaichon==":green[B.(Say En - Nói tiếng Anh):sunflower:]":
    st.write(":blue[Selected - Đã chọn:]", ":green[B.(Say En - Nói tiếng Anh):sunflower:]" + ":blue[(Say something...)]")
    lang="en_US"
    lang_src='en'
    lang_dest='vi'
else:    
    st.write("")
    lang=""
    lang_src=''
    lang_dest=''

#B1: ghi am giong noi va chuyen thanh text
if lang != '':
    l_text = speech_to_text(lang)
    st.write(l_text)
    #B2: dich sang text En hoac Vi
    if l_text is not None:
        txt_translated = textsrc_to_textdest(l_text, lang_src, lang_dest)
        st.write(txt_translated)
    if l_text is not None:
        audio_io = text_to_speech(txt_translated, lang_dest)
        st.audio(audio_io, format="audio/wav",start_time=0)
