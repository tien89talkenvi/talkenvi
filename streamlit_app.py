#streamlit==1.27.2
#SpeechRecognition==3.10.0
#pyaudio==0.2.13 #(cho SpeechRecognition lay micro )
#googletrans==4.0.0rc1 #(phien ban nay cho rieng py khi su dung googletrans, cac pban khac hay gay loi)
#gTTS==2.4.0


#https://talkenvi-b5vypm7itcecxnkuvne7h9.streamlit.app/ 
#la url app moi talkenvi
import streamlit as st
import speech_recognition as sr 
from audio_recorder_streamlit import audio_recorder #pip install audio-recorder-streamlit
from googletrans import Translator 
from gtts import gTTS, gTTSError   
from io import BytesIO  
import numpy as np
import soundfile as sf
import sounddevice as sd


def speech_to_text(lang):
    #red="#FF0000" , blue="#0000FF" , yellow="#FFFF00"     
    if lang=="vi-VN":
        audio_bytesa = audio_recorder(text='A.(Say in Vi - Nói bằng tiếng Việt):',recording_color="#FFFF00",neutral_color="#FF0000",icon_size="2x")
        if audio_bytesa:
            with open('thua.wav','wb') as fa:
                fa.write(audio_bytesa)
                r = sr.Recognizer()
                with sr.AudioFile('thua.wav') as source:
                    audioa = r.record(source)  # read the entire audio file
                try:
                    texta = r.recognize_google(audioa, language=lang)
                    return texta
                except sr.UnknownValueError:
                    st.write("Không thể xác định giọng nói.")
                except sr.RequestError as e:
                    print(f"Lỗi: {e}")
    elif lang=="en_US":
        audio_bytesb = audio_recorder(text='B.(Say in En - Nói bằng tiếng Anh):',recording_color="#FFFF00",neutral_color="#0000FF",icon_size="2x")
        if audio_bytesb:
            with open('thub.wav','wb') as fb:
                fb.write(audio_bytesb)
            #st.audio(audio_bytesb, format="audio/wav")
                r = sr.Recognizer()
                with sr.AudioFile('thub.wav') as source:
                    audiob = r.record(source)  # read the entire audio file
                try:
                    textb = r.recognize_google(audiob, language=lang)
                    return textb
                except sr.UnknownValueError:
                    st.write("Không thể xác định giọng nói.")
                except sr.RequestError as e:
                    print(f"Lỗi: {e}")
    
def textsrc_to_textdest(l_text, lang_src,lang_dest):
    translator = Translator()
    translation = translator.translate(l_text, src=lang_src, dest=lang_dest)
    #st.write(translation.text)
    return translation.text

def text_to_speech(text, lang='vi'):
    try:
        tts = gTTS(text, lang=lang)
        data_io = BytesIO()
        tts.write_to_fp(data_io)
        data_io.seek(0)
        #chuyen data_io sang nparray am thanh nho sf roi choi nparray nho sd
        data, samplerate = sf.read(data_io)
        sd.play(data, samplerate)
        sd.wait()        
        return data_io
        #st.success("Chuyển văn bản thành giọng nói thành công!")
    except gTTSError as err:
        st.error(err)
    

#######################################################
st.subheader(":blue[Trò chuyện bằng tiếng Việt, Anh - Talk in Vietnamese, English]")
vaichon = st.radio(":green[Select one of options:]", 
                [":red[A.(Say Vi - Nói tiếng Việt):balloon:]", ":blue[B.(Say En - Nói tiếng Anh):sunflower:]","STOP"], 
                index=2,horizontal=True ) 

st.write("---")
if vaichon == ":red[A.(Say Vi - Nói tiếng Việt):balloon:]":
    #st.write(":blue[Selected - Đã chọn:]", ":red[A.(Say Vi - Nói tiếng Việt):balloon:]" + ":blue[(Hãy nói gì đó...)]")
    lang="vi-VN"
    lang_src='vi'
    lang_dest='en'
elif vaichon==":blue[B.(Say En - Nói tiếng Anh):sunflower:]":
    #st.write(":blue[Selected - Đã chọn:]", ":green[B.(Say En - Nói tiếng Anh):sunflower:]" + ":blue[(Say something...)]")
    lang="en_US"
    lang_src='en'
    lang_dest='vi'
else:    
    #st.write("")
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
        # dung de play lai neu can
        st.audio(audio_io, format="audio/wav",start_time=0)
