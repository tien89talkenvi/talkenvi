#https://talkenvi-b5vypm7itcecxnkuvne7h9.streamlit.app/ 
#la url app moi talkenvi
import streamlit as st
import speech_recognition as sr 
from audio_recorder_streamlit import audio_recorder #pip install audio-recorder-streamlit
from googletrans import Translator 
from gtts import gTTS, gTTSError   
from io import BytesIO  
import soundfile as sf
import sounddevice as sd

def speech_text_translate_audio(lang_sp,lang_src,lang_dest):
    if lang_sp == 'vi':
        mtextX="**A** Nói tiếng Việt (Say in Vietnamese):"
        mrecthu="#FFFF00"
        mrecstop="#FF0000"
    else:
        mtextX='**B** Nói tiếng '+noi_voi+' (Say in '+noi_voi+'):'
        mrecthu="#FFFF00"
        mrecstop="#0000FF"

    audio_bytes = audio_recorder(text=mtextX,recording_color=mrecthu,neutral_color=mrecstop,icon_size="2x",energy_threshold=(-1.0,1.0),pause_threshold=5.0)
    if audio_bytes:
        with open('thu.wav','wb') as f:
            f.write(audio_bytes)
            r = sr.Recognizer()
            with sr.AudioFile('thu.wav') as source:
                audio = r.record(source)  # read the entire audio file
            try:
                text_from_audio = r.recognize_google(audio, language=lang_sp)
                st.write(text_from_audio)
                translator = Translator()
                text_translated = translator.translate(text_from_audio, src=lang_src,dest=lang_dest).text    # Dich ra En theo tai lieu web
                st.write(text_translated)
                mp3_fp = BytesIO()
                tts = gTTS(text_translated, lang=lang_sp)
                tts.write_to_fp(mp3_fp)
                mp3_fp.seek(0)
                st.audio(mp3_fp, format="audio/wav",start_time=0)
                # Đọc dữ liệu âm thanh từ `BytesIO` bằng thư viện soundfile
                audio_data, sample_rate = sf.read(mp3_fp)
                # Phát âm thanh bằng thư viện sounddevice
                sd.play(audio_data, sample_rate)
                sd.wait()

            except sr.UnknownValueError:
                text1=''
                st.write("")
            except sr.RequestError as e:
                text1=''
                print(f"Lỗi: {e}")
                st.write("")


#######################################################
st.subheader(":blue[Trò chuyện tiếng Việt (có thông dịch) với...]")
#vaichon = st.radio(":green[Select one of options to say:]", 
#                [":orange[Vietnamse]", ":blue[English]",":green[Danish]",":orange[German]",":yellow[Taiwan]",":blue[Japanese]",":red[Korean]","CANCEL"],
#                index=7,horizontal=True ) 
noi_voi = st.selectbox("Chon nguoi Noi voi:", 
                ("English - Anh (en)","Spanish - Tây ban nha (es)","Taiwan - Đài loan (zh-TW)","Danish - Đan mạch (da)","German - Đức (de)","Dutch - Hà lan (nl)","Japanese - Nhật bản (ja)","Korean - Hản quốc (ko)"),index=0,label_visibility="hidden")
noi_voi=noi_voi.strip()
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
####
vaichon = st.radio(":green[Select one of options to say:]", 
                [":red[Vietnamse]", ":blue["+noi_voi+"]","Clear (Xóa)"],
                index=2,horizontal=True ) 
st.write("---")

if vaichon=="Clear (Xóa)":
    st.write("")
else:
    if vaichon==":red[Vietnamse]":
        lang_sp='vi'
        lang_src='vi'
        lang_dest=codelang
        speech_text_translate_audio(lang_sp,lang_src,lang_dest)
    else:        
        lang_sp=codelang
        lang_src=codelang
        lang_dest='vi'
        speech_text_translate_audio(lang_sp,lang_src,lang_dest)

