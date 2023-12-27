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
from streamlit_option_menu import option_menu

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
st.title(":blue[:sunglasses: Talk In 2 Languages]")

langguages = ("Vietnamese (vi)","English (en)","Latin (la)","Spanish (es)","Taiwan (zh-TW)","Danish (da)","German (de)","Dutch (nl)","French (fr)","Japanese (ja)","Korean (ko)","Thai (th)","Khmer (km)")
tieng_1 = "Vietnamese (vi)"
tieng_2 = "English (en)"

with st.sidebar:
    selected = option_menu("Setting", ["Lang 1", 'Lang 2'], 
        icons=['house', 'gear'], menu_icon="cast", default_index=0)
    if selected == "Lang 1":
        tieng_1 = st.selectbox("Reset lang 1",langguages, index=0,key='L1' )
    if selected == "Lang 2":
        tieng_2 = st.selectbox("Reset lang 2",langguages, index=1,key='L2' )

# horizontal Menu
vaichon = option_menu(None, [tieng_1[0:tieng_1.index('(')], tieng_2[0:tieng_2.index('(')]], 
    icons=['house', 'cloud-upload'], 
    menu_icon="cast", default_index=0, orientation="horizontal")



audio_bytes = audio_recorder(text='Select a lang and click mic to say : ')

st.write("---")

col1, col2 = st.columns(2)

if audio_bytes:
    if vaichon==tieng_1[0:tieng_1.index('(')]:
        codelang_1 = ma_tieng(tieng_1)
        lang_sp=codelang_1
        lang_src=codelang_1
        lang_dest=ma_tieng(tieng_2)
        xuli_ra_phat_am_dest(audio_bytes,lang_sp,lang_src,lang_dest)    
    elif vaichon==tieng_2[0:tieng_2.index('(')]:
        codelang_2 = ma_tieng(tieng_2)
        lang_sp=codelang_2
        lang_src=codelang_2
        lang_dest=ma_tieng(tieng_1)
        xuli_ra_phat_am_dest(audio_bytes,lang_sp,lang_src,lang_dest)    
    else:
        audio_bytes=bytes()
else:
    pass
