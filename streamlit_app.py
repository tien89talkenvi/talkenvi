#ma nay do chatGPT cho, thu dung cookies proxy de tranh bi chan
import streamlit as st
import yt_dlp
import json
import requests
import streamlit.components.v1 as components 
import os
import xml.etree.ElementTree as ET
import time
from urllib.parse import urlparse, parse_qs


#----------------------- cac def ---------------------
def get_subtitle_urls(info_dict):
    def extract_urls(subs_dict):
        urls = {}
        for lang, tracks in subs_dict.items():
            ttml_url = None
            for track in tracks:
                ext = track.get("ext")
                if ext == "ttml" and not ttml_url:
                    ttml_url = track.get("url")
            # Ưu tiên TTML, fallback sang VTT nếu không có
            if ttml_url:
                urls[lang] = {"ext": "ttml", "url": ttml_url}
        return urls

    subtitles = info_dict.get("subtitles", {})
    auto_captions = info_dict.get("automatic_captions", {})

    return {
        "official_subtitles": extract_urls(subtitles),
        "automatic_captions": extract_urls(auto_captions)
    }

def time_to_seconds(t):
    h, m, s = t.split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)

def parse_ttml_with_seconds(ttml_string):
    root = ET.fromstring(ttml_string)
    namespace = {'ttml': root.tag.split('}')[0].strip('{')}

    subtitles = []
    for p in root.findall('.//ttml:body//ttml:p', namespaces=namespace):
        begin = p.attrib.get('begin')
        end = p.attrib.get('end')
        text = ''.join(p.itertext()).strip()

        if begin and end and text:
            subtitles.append({
                'start': round(time_to_seconds(begin),3),
                'end': round(time_to_seconds(end),3),
                'text': text,
                'textdich': text
            })
    return subtitles


def lap_html_video(videoId, subtitles):
    subtitle_js = json.dumps(subtitles)
    video_id = videoId

    html_code = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Sync Translated Subtitles with YouTube</title>

<style>
body {{ font-family: Arial; padding: 10px; text-align: center;}}
#player {{ margin-bottom: 20px; }}
#status {{ font-size: 16px; margin-top: 10px; }}
h2 {{text-align: center;}}
</style>
</head>
<body>
<h2 >Xem YouTube với phụ đề dịch nói</h2>
<select id="voiceSelect" onchange="dichSubT()"></select><br><br>
<div id="player"></div>
<div id="status">Status: Waiting...</div>
<br>

<script>
let player;
let currentIndex = 0;
let langSpeak="vi-VN";
let langDich = "vi";
const voiceSelect = document.getElementById("voiceSelect");

let subtitles = {subtitle_js}

function onYouTubeIframeAPIReady() {{
    player = new YT.Player('player', {{
        height: '315',
        width: '465',
        videoId:  '{video_id}', 
        events: {{
            'onReady': onPlayerReady,
            'onStateChange': onPlayerStateChange
        }}
    }});
}}

function onPlayerReady(event) {{
    document.getElementById("status").textContent = "Status: Ready. Click play!";
}}

function onPlayerStateChange(event) {{
    if (event.data === YT.PlayerState.PLAYING) {{
        checkTimeLoop();
    }}
}}

function checkTimeLoop() {{
    const interval = setInterval(() => {{
        if (player.getPlayerState() !== YT.PlayerState.PLAYING) {{
            clearInterval(interval);
            return;
        }}

        const currentTime = player.getCurrentTime();

        if (currentIndex < subtitles.length) {{
            const sub = subtitles[currentIndex];
            if (currentTime >= sub.start && currentTime <= sub.end) {{
                speak(sub.textdich);
                currentIndex++;
            }}
        }}
    }}, 300);
}}

function speak(text) {{
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = langSpeak;
    utter.rate = 1.0;
    speechSynthesis.cancel(); // Ngăn giọng cũ nếu đang nói
    speechSynthesis.speak(utter);
    document.getElementById("status").textContent = text;
}}
function populateVoices() {{
    const voices = speechSynthesis.getVoices();

    voiceSelect.innerHTML = ""; // Xóa sạch trước khi thêm mới

    voices.forEach((voice, index) => {{
    const option = document.createElement("option");
    option.textContent = `${{voice.name}} (${{voice.lang}})` + (voice.default ? " [default]" : "");
    option.value = voice.name;
    option.dataset.lang = voice.lang;
    voiceSelect.appendChild(option);
    }});

    // Tìm giọng có lang là 'vi-VN'
    const viIndex = voices.findIndex(voice => voice.lang === 'en-US');
    if (viIndex !== -1) {{
    voiceSelect.selectedIndex = viIndex;
    }}
}}

// Một số trình duyệt cần đợi event 'voiceschanged' mới lấy được giọng
speechSynthesis.onvoiceschanged = populateVoices;

// Gọi luôn lần đầu (nhiều trình duyệt hiện đại vẫn trả về danh sách ngay lập tức)
populateVoices();

const tag = document.createElement('script');
tag.src = "https://www.youtube.com/iframe_api";
document.body.appendChild(tag);

function dichSubT(){{
    let ichon = voiceSelect.selectedIndex;// const selectedOption = select.selectedOptions[0];
    // Lấy name (hiển thị trong .value) và lang (đã lưu trong data-lang)
    //const voiceName = selectedOption.value;
    langSpeak = voiceSelect[ichon].dataset.lang;
    langDich = langSpeak.slice(0,2); 
    //alert(langSpeak+" , "+langDich);

    let sourceLanguage = 'en';
    let targetLanguage = langDich;
    console.log(sourceLanguage, targetLanguage);
    //tao texts la list chua cac text cua subtitles
    let texts = subtitles.map(item => item.text);
    let textdichs = subtitles.map(item => item.textdich);

    //console.log(texts);
    
    Array.prototype.forEach.call(texts, function(cau,i) {{
        let inputText = cau;
        let outputTextEle = textdichs[i];
    //  console.log(inputText);

        const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=${{sourceLanguage}}&tl=${{targetLanguage}}&dt=t&q=${{encodeURI(inputText)}}`;

        const xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function () {{
            if (this.readyState == 4 && this.status == 200){{
                const responseReturned = JSON.parse(this.responseText);
                const translations = responseReturned[0].map((text) => text[0]);
                const outputText = translations.join(" ");
                //outputTextEle.textdich = outputText;
                subtitles[i].textdich = outputText;
                console.log(subtitles[i].textdich);

            }}
        }};
        //---------------------
        xhttp.open("GET", url);
        xhttp.send();
    }});
}}

</script>
</body>
</html>
"""
    #components.html(html_code, height=600, scrolling=True)
    return html_code

#--------------------------MAIN ---------------------------------------
#st.set_page_config(page_title="YouTube Video Info", layout="centered")
st.set_page_config(
  page_title="Xem yt voi phu de dich noi",
  page_icon="  ",
  #layout="wide",
  layout="centered",
  #initial_sidebar_state="expanded",
)
# css Ẩn header và menu mặc định
        #MainMenu {visibility: hidden;}
        #footer {visibility: hidden;}
        #header {visibility: hidden;}

hide_streamlit_style = """
    <style>
        .block-container {
            padding-top: 0.4rem;
            padding-bottom: 0rem;
            padding-left: 0.2rem;
        }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

#--cac bien global--
videoID=''
subtitles=[]
html_code=''
save_dir=""

#--- sidebar ben trai--------------------------

with st.sidebar:
    st.title("🤖 Xem youtube với phụ đề dịch nói")
    video_url = st.text_input("🔗 Nhập URL video YouTube: vd:  https://www.youtube.com/watch?v=Xwb1OrkPupM&t=5s", "")

    if st.button("Lấy thông tin"):
        tbaodong1 = st.empty()
        tbaodong1.write('⏳ Đang xử lý...')

        #st.info("⏳ Đang xử lý...")
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            #'ratelimit': 500000,  # giới hạn tốc độ tải: 500 KB/s
            #'sleep_interval_requests': 2,  # nghỉ 2 giây giữa các request
            'skip_download': True,
            'forcejson': True
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video_url, download=False)
                videoID = info_dict['id']
                st.write("videoID: ",videoID)
                # xet phu de                    
                subtitle_data = get_subtitle_urls(info_dict)
                # xet phu de truyen thong
                if subtitle_data["automatic_captions"] != {}:
                    if subtitle_data["automatic_captions"]["en"]:
                        dangPdEn = subtitle_data["automatic_captions"]["en"]["ext"]
                        urlPdEn = subtitle_data["automatic_captions"]["en"]["url"]
                        ttLayPdEn = [dangPdEn, urlPdEn]
                        f = requests.get(ttLayPdEn[1])
                        if dangPdEn == "ttml":
                            ttml_content = f.text
                            subtitles = parse_ttml_with_seconds(ttml_content)
                            print("Co subtitles")
                    else:
                        st.write("No en subtitles!")           
                else:
                    subtitles = []
                    st.write("No subtitles!")

                if len(subtitles)>0:
                    tepjson = "phude.json"
                    output_file = os.path.join(save_dir, f"{tepjson}")
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(subtitles, f, ensure_ascii=False, indent=2)

                    st.write(f"✅ Đã lưu vào: {output_file}")
            
            html_code = lap_html_video(videoID, subtitles)   
            st.write('✅ Đã đủ thông tin và youtube hiển thị.')
        

        except Exception as e:
            st.write(f"❌ Lỗi: {str(e)}")

if videoID and html_code:
    #st.write('Da co videoId and subtitlesJson')
    #st.title("🎤 Subtitle Viewer with Word-by-Word Voice Highlight")
    components.html(html_code, height=600, scrolling=True)
