#https://talkenvi-b5vypm7itcecxnkuvne7h9.streamlit.app/ 
import streamlit as st
import speech_recognition as sr 
from audio_recorder_streamlit import audio_recorder #pip install audio-recorder-streamlit
from googletrans import Translator 
from gtts import gTTS, gTTSError   
from io import BytesIO  
import base64
import time
from streamlit.components.v1 import html

def thuc_hien_dao(tieng_1,tieng_2):
    index_t1=3
    index_t2=2
    with col1:
        tieng_1 = st.selectbox(":red[---NÓI]", 
                    ("Vietnamese - Viet (vi)","English - Anh (en)","Spanish - Tây ban nha (es)","Taiwan - Đài loan (zh-TW)","Danish - Đan mạch (da)","German - Đức (de)","Dutch - Hà lan (nl)","French - Pháp (fr)","Japanese - Nhật bản (ja)","Korean - Hản quốc (ko)","Thai - Thái lan (th)","Khmer - Campuchia (km)"),index=index_t1,key=1)

    with col2:
        tieng_2 = st.selectbox(":blue[---NGHE (đã dịch)]", 
                    ("Vietnamese - Viet (vi)","English - Anh (en)","Spanish - Tây ban nha (es)","Taiwan - Đài loan (zh-TW)","Danish - Đan mạch (da)","German - Đức (de)","Dutch - Hà lan (nl)","French - Pháp (fr)","Japanese - Nhật bản (ja)","Korean - Hản quốc (ko)","Thai - Thái lan (th)","Khmer - Campuchia (km)"),index=index_t2,key=2)


def ma_tieng(tieng):
    global codelang_1,codelang_2
    sub1='('
    sub2=')'
    idx1 = tieng.index(sub1)
    idx2 = tieng.index(sub2)
    res = ''
    # getting elements in between
    for idx in range(idx1 + len(sub1), idx2):
        res = res + tieng[idx]
    codelang=res
    return codelang

def auto_phat_audio(mp3_fp):
    audio_placeholder=st.empty()
    data = mp3_fp.read()
    audio_b64 = base64.b64encode(data).decode()
    my_html=f'''
            <audio autoplay>
             <source src="data:audio/mp3;base64,{audio_b64}">
            </audio>
            '''
    audio_placeholder.empty()
    time.sleep(0.2)
    html(my_html) 
    #audio_placeholder.markdown(md,unsafe_allow_html=True)

def xuli_ra_phat_am_dest(audio_bytes,lang_sp,lang_src,lang_dest):
    with open('thu.wav','wb') as f:
        f.write(audio_bytes)
    r = sr.Recognizer()
    with sr.AudioFile('thu.wav') as source:
        audio = r.record(source)  # read the entire audio file
        try:
            text_from_audio = r.recognize_google(audio, language=lang_sp)
            with col1:
                st.write(":red["+text_from_audio+"]")
            if text_from_audio != '':
                translator = Translator()
                text_translated = translator.translate(text_from_audio, src=lang_src,dest=lang_dest).text    # Dich ra En theo tai lieu web
            with col2:
                st.write(":blue["+text_translated+"]")
            if text_translated !='':
                mp3_fp = BytesIO()
                try:
                    tts = gTTS(text_translated, lang=lang_dest)
                    tts.write_to_fp(mp3_fp)
                    mp3_fp.seek(0)  #phai co dong nay thi auto_phat_audio moi phat dc
                    with col2:
                        st.audio(mp3_fp, format="audio/wav",start_time=0)
                        auto_phat_audio(mp3_fp)
                except gTTSError as err:
                    st.error(err)
        except sr.UnknownValueError:
            st.write("Không nhận thức được tiếng nói")
        except sr.RequestError as e:
            st.write(f"Lỗi: {e}")
            #print(f"Lỗi: {e}")

#######################################################
st.subheader(":blue[Trò chuyện có thông dịch bằng hai ngôn ngữ]")

colA, colB,colC = st.columns(3)
with colA:
    st.write(':green[Thiết lập hai ngôn ngữ đàm thoại:]')        
with colB:
    tieng_1 = st.selectbox(":red[---NÓI]", 
                ("Vietnamese - Viet (vi)","English - Anh (en)","Spanish - Tây ban nha (es)","Taiwan - Đài loan (zh-TW)","Danish - Đan mạch (da)","German - Đức (de)","Dutch - Hà lan (nl)","French - Pháp (fr)","Japanese - Nhật bản (ja)","Korean - Hản quốc (ko)","Thai - Thái lan (th)","Khmer - Campuchia (km)"),index=0,key=1,label_visibility="hidden" )
with colC:
    tieng_2 = st.selectbox(":blue[---NGHE (đã dịch)]", 
                ("Vietnamese - Viet (vi)","English - Anh (en)","Spanish - Tây ban nha (es)","Taiwan - Đài loan (zh-TW)","Danish - Đan mạch (da)","German - Đức (de)","Dutch - Hà lan (nl)","French - Pháp (fr)","Japanese - Nhật bản (ja)","Korean - Hản quốc (ko)","Thai - Thái lan (th)","Khmer - Campuchia (km)"),index=1,key=2,label_visibility="hidden" )

audio_bytes = audio_recorder(text='')

if audio_bytes:
    vaichon = st.radio(":green[Chọn một ngôn ngữ dưới đây rồi nhấp micro để NÓI:]", [":red["+tieng_1+"]",":blue["+tieng_2+"]",'CLEAR'],index=2,horizontal=True ) 

    col1, col2 = st.columns(2)

    if vaichon==":red["+tieng_1+"]":
        codelang_1 = ma_tieng(tieng_1)
        lang_sp=codelang_1
        lang_src=codelang_1
        lang_dest=ma_tieng(tieng_2)
        xuli_ra_phat_am_dest(audio_bytes,lang_sp,lang_src,lang_dest)    
    elif vaichon==":blue["+tieng_2+"]":
        codelang_2 = ma_tieng(tieng_2)
        lang_sp=codelang_2
        lang_src=codelang_2
        lang_dest=ma_tieng(tieng_1)
        xuli_ra_phat_am_dest(audio_bytes,lang_sp,lang_src,lang_dest)    
    else:
        audio_bytes=bytes()
