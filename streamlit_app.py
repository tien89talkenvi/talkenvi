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
import streamlit.components.v1 as stc
import base64
import time

def auto_phat_audio(audio_path):
    # khi ham nay chay thi mp3_fp nhu 1 tệp mp3/wav sẽ được tải và dữ liệu âm thanh được chuyển đổi 
    # thành văn bản bằng base64. Việc phát lại âm thanh được thực hiện trên ứng dụng bằng cách 
    # chỉ định văn bản đã chuyển đổi làm nguồn của thẻ âm thanh HTML. 
    # Chìa khóa ở đây là chỉ định ``autoplay=True'' trong thẻ âm thanh. 
    # Với thông số kỹ thuật này, âm thanh sẽ được tự động phát khi ứng dụng chạy.
    audio_placeholder = st.empty()
    file_ = open(audio_path, "rb") #no mo roi
    contents = file_.read()
    file_.close()
    #<audio autoplay=True> #cai nay thay vao duoi thi no khong co thanh bar 
    audio_str = "data:audio/ogg;base64,%s"%(base64.b64encode(contents).decode())
    audio_html = """
                    <audio controls autoplay=True controlslist="nodownload">
                    <source src="%s" type="audio/ogg" autoplay=True>
                    Your browser does not support the audio element.
                    </audio>
                """ %audio_str
    audio_placeholder.empty()
    time.sleep(0.5) #
    audio_placeholder.markdown(audio_html, unsafe_allow_html=True)

def thuam_txt_dichtxt_phatam(audio_bytes,lang_sp,lang_src,lang_dest):
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
            mp3_fp = BytesIO()
            tts = gTTS(text_translated, lang=lang_dest)
            tts.save('temp.mp3')
            #tts.write_to_fp(mp3_fp)
            #mp3_fp.seek(0)
            #st.audio(mp3_fp, format="audio/wav",start_time=0)
            #auto_phat_audio(mp3_fp)
            auto_phat_audio('temp.mp3')
    except sr.UnknownValueError:
        st.write("Không nhận thức được tiếng nói")
    except sr.RequestError as e:
        st.write("Sorry!!")
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

mtext1="Click on mic để nói tiếng VIỆT (Vietnamese):"
mtext2='Click on mic để nói tiếng '+tieng_khac

vaichon = st.radio(":green[Select one of options to say:]", [":red[Nói tiếng VIỆT (Vietnamese)]",":blue[Nói tiếng "+tieng_khac+"]",'CLEAR'],index=2,horizontal=True ) 

st.write("---")

if vaichon==":red[Nói tiếng VIỆT (Vietnamese)]":
    audio_bytes1 = audio_recorder(text=mtext1,recording_color="#FFFF00",neutral_color="#FF0000",icon_size="2x",energy_threshold=(-1.0,1.0),pause_threshold=3.0)
    lang_sp='vi'
    lang_src='vi'
    lang_dest=codelang
    if audio_bytes1: #neu co du lieu trong bien audio_bytes2
        thuam_txt_dichtxt_phatam(audio_bytes1,lang_sp,lang_src,lang_dest)

elif vaichon==":blue[Nói tiếng "+tieng_khac+"]":
    audio_bytes2 = audio_recorder(text=mtext2,recording_color="#FFFF00",neutral_color="#0000FF",icon_size="2x",energy_threshold=(-1.0,1.0),pause_threshold=3.0)
    lang_sp=codelang
    lang_src=codelang
    lang_dest='vi'
    if audio_bytes2: #neu co du lieu trong bien audio_bytes2
        thuam_txt_dichtxt_phatam(audio_bytes2,lang_sp,lang_src,lang_dest)

else:
    pass

