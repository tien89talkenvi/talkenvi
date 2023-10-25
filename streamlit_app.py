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
#import streamlit.components.v1 as stc
import base64
import time

def auto_phat_audio(file_mp3):
    mymidia_placeholder = st.empty()
    with open(file_mp3,'rb') as f:
        mymidia_bytes=f.read()
    mymidia_str = "data:audio/ogg;base64,%s"%(base64.b64encode(mymidia_bytes).decode())
    mymidia_html = """
                    <audio controls autoplay class="stAudio">
                    <source src="%s" type="audio/ogg">
                    Your browser does not support the audio element.
                    </audio>
                """%mymidia_str

    mymidia_placeholder.empty()
    time.sleep(1)
    mymidia_placeholder.markdown(mymidia_html, unsafe_allow_html=True)

    #audio_placeholder=st.empty()
    #data = mp3_fp.read()
    #b64 = base64.b64encode(data).decode()
    #md = f"""
    #    <audio controls autoplay="true">
    #    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    #    </audio>
    #    """
    #audio_placeholder.empty()
    #time.sleep(0.2) 
    #audio_placeholder.markdown(md,unsafe_allow_html=True)

def xuli_ra_phat_am_dest(audio_bytes,lang_sp,lang_src,lang_dest):
    with open('thu.wav','wb') as f:
        f.write(audio_bytes)
    r = sr.Recognizer()
    with sr.AudioFile('thu.wav') as source:
        audio = r.record(source)  # read the entire audio file
        try:
            text_from_audio = r.recognize_google(audio, language=lang_sp)
            st.write(text_from_audio)
            if text_from_audio != '':
                translator = Translator()
                text_translated = translator.translate(text_from_audio, src=lang_src,dest=lang_dest).text    # Dich ra En theo tai lieu web
                st.write(text_translated)
            if text_translated !='':
                #mp3_fp = BytesIO()
                tts = gTTS(text_translated, lang=lang_dest)
                file_mp3='out.mp3'
                tts.save(file_mp3)

                #tts.write_to_fp(mp3_fp)
                #mp3_fp.seek(0)  #phai co dong nay thi auto_phat_audio moi phat dc
                #st.audio(mp3_fp, format="audio/wav",start_time=0)
                auto_phat_audio(file_mp3)
        except sr.UnknownValueError:
            st.write("Không nhận thức được tiếng nói")
        except sr.RequestError as e:
            st.write(f"Lỗi: {e}")
            #print(f"Lỗi: {e}")

#######################################################
st.subheader(":blue[Trò chuyện có thông dịch bằng tiếng Việt và tiếng...]")
tieng_khac = st.selectbox(":blue[(Talk with interpretation in Vietnamese and ...)]", 
                ("English - Anh (en)","Spanish - Tây ban nha (es)","Taiwan - Đài loan (zh-TW)","Danish - Đan mạch (da)","German - Đức (de)","Dutch - Hà lan (nl)","Japanese - Nhật bản (ja)","Korean - Hản quốc (ko)"),index=0)
sub1='('
sub2=')'
idx1 = tieng_khac.index(sub1)
idx2 = tieng_khac.index(sub2)
res = ''
# getting elements in between
for idx in range(idx1 + len(sub1), idx2):
    res = res + tieng_khac[idx]
codelang=res
#print(codelang)

vaichon = st.radio(":green[Select one of options to say:]", [":red[Nói tiếng VIỆT (Vietnamese)]",":blue[Nói tiếng "+tieng_khac+"]",'CLEAR'],index=2,horizontal=True ) 

st.write("---")

if vaichon==":red[Nói tiếng VIỆT (Vietnamese)]":
    lang_sp='vi'
    lang_src='vi'
    lang_dest=codelang
    mtext="Click on mic rồi nói tiếng VIỆT (Vietnamese):"
    # Chay ham hien mic voi cac tham so va thu am roi tra ve audio_bytes thu duoc
    audio_bytes1 = audio_recorder(text=mtext,recording_color="#FFFF00",neutral_color="#FF0000",icon_size="2x",energy_threshold=(-1.0,1.0),pause_threshold=3.0)
    if audio_bytes1:
        # chay ham Xu li audio_bytes da thu de cho ra ket qua cuoi cung la phat ra am thanh dest
        xuli_ra_phat_am_dest(audio_bytes1,lang_sp,lang_src,lang_dest)

elif vaichon==":blue[Nói tiếng "+tieng_khac+"]":
    lang_sp=codelang
    lang_src=codelang
    lang_dest='vi'
    mtext='Click on mic rồi nói tiếng '+tieng_khac
    # Chay ham hien mic voi cac tham so va thu am roi tra ve audio_bytes thu duoc
    audio_bytes2 = audio_recorder(text=mtext,recording_color="#FFFF00",neutral_color="#0000FF",icon_size="2x",energy_threshold=(-1.0,1.0),pause_threshold=3.0)
    if audio_bytes2:
        # chay ham Xu li audio_bytes da thu de cho ra ket qua cuoi cung la phat ra am thanh dest
        xuli_ra_phat_am_dest(audio_bytes2,lang_sp,lang_src,lang_dest)

else:
    pass

