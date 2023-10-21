#streamlit==1.27.2
#SpeechRecognition==3.10.0
#pyaudio==0.2.13 #(cho SpeechRecognition lay micro )
#googletrans==4.0.0rc1 #(phien ban nay cho rieng py khi su dung googletrans, cac pban khac hay gay loi)
#gTTS==2.4.0


#https://talkenvi-b5vypm7itcecxnkuvne7h9.streamlit.app/ 
#la url app moi talkenvi
# de ghi am noi va chuyen am thanh text
import pyaudio
import speech_recognition as sr
# de dich
from googletrans import Translator
#2 cai sau de chuyen text thanh am thanh
from gtts import gTTS
from io import BytesIO
import soundfile as sf
import sounddevice as sd
import streamlit as st

def speech_dich_audio(lang,lang_src,lang_dest):
    device_index = 2
    r = sr.Recognizer()
    with sr.Microphone(device_index=device_index) as source:
        if lang != 'vi':
            st.write(":blue[Say something!...(Hãy nói gì đi...)]")
        else:
            st.write(":red[Say something!...(Hãy nói gì đi...)]")
        audio = r.listen(source)
    # recognize speech using Google Speech Recognition
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        #print("Google Speech Recognition thinks you said " + r.recognize_google(audio))
        text_from_audio=r.recognize_google(audio,language=lang) #Lay ra text tu audio da thu qua micro voi giong viet
        if lang != 'vi':
            st.write(":blue["+text_from_audio+"]")
        else:        
            st.write(":red["+text_from_audio+"]")
        
        translator = Translator()
        text_translated = translator.translate(text_from_audio, src=lang_src,dest=lang_dest).text    # Dich ra En theo tai lieu web
        if lang != 'vi':
            st.write(":blue["+text_translated+"]")
        else:        
            st.write(":red["+text_translated+"]")
        
        mp3_fp = BytesIO()
        tts = gTTS(text_translated, lang=lang_dest)
        tts.write_to_fp(mp3_fp)
        #st.write(f'<audio src="{audio_url}" autoplay="true" controls></audio>') of GPT
        # Load `mp3_fp` as an mp3 file in
        # the audio library of your choice
        #chuyen doi sang dinh dang am thanh
        mp3_fp.seek(0)
        st.audio(mp3_fp, format="audio/wav",start_time=0)
        # Đọc dữ liệu âm thanh từ `BytesIO` bằng thư viện soundfile
        audio_data, sample_rate = sf.read(mp3_fp)
        # Phát âm thanh bằng thư viện sounddevice
        sd.play(audio_data, sample_rate)
        sd.wait()

        #phat am thanh tu dong
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))


##### MAIN ##################################################
st.subheader(":blue[Trò chuyện (có thông dịch) bằng tiếng Việt và tiếng...]")
noi_voi = st.selectbox("Chon nguoi Noi voi:", 
                ("English - Anh (en)","Spanish - Tây ban nha (es)","Taiwan - Đài loan (zh-TW)","Danish - Đan mạch (da)","German - Đức (de)","Dutch - Hà lan (nl)","Japanese - Nhật bản (ja)","Korean - Hản quốc (ko)"),index=0,label_visibility="hidden")
#noi_voi=noi_voi.strip()
sub1='('
sub2=')'
idx1 = noi_voi.index(sub1)
idx2 = noi_voi.index(sub2)
res = ''
# getting elements in between
for idx in range(idx1 + len(sub1), idx2):
    res = res + noi_voi[idx]
codelang=res
#print(codelang)

vaichon = st.radio(":green[Select one of options to say:]", 
                [":red[Vietnamse]", ":blue["+noi_voi+"]","Clear (Xóa)"],
                index=0,horizontal=True ) 
if vaichon=="Clear (Xóa)":
    st.write("")
else:
    if vaichon==":red[Vietnamse]":
        lang='vi'
        lang_src='vi'
        lang_dest=codelang
    else:        
        lang=codelang
        lang_src=codelang
        lang_dest='vi'

    speech_dich_audio(lang,lang_src,lang_dest)
