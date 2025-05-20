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
# Ham nay de xet xem url co phai cua youtube hay khong
def parse_youtube_url(url):
    """
    Trả về video_id nếu url là YouTube; ngược lại trả về None.
    Hỗ trợ:
      - https://www.youtube.com/watch?v=ID
      - https://youtu.be/ID
      - https://www.youtube.com/embed/ID
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # Chỉ chấp nhận youtube.com hoặc youtu.be
        if not any(domain.endswith(d) for d in ("youtube.com", "youtu.be")):
            return None

        # youtube.com/watch?v=ID
        if "youtube.com" in domain:
            qs = parse_qs(parsed.query)
            vid = qs.get("v")
            if vid:
                return vid[0]
            # hoặc đường embed: /embed/ID
            path_parts = parsed.path.split("/")
            if len(path_parts) >= 3 and path_parts[1] == "embed":
                return path_parts[2]

        # youtu.be/ID
        if "youtu.be" in domain:
            return parsed.path.lstrip("/")

    except Exception:
        pass

    return None

# Ham nay de xet xem yt co phu de goc hay phu de tu sinh hay khong
def get_subtitle_urls(info_dict):
    def extract_urls(subs_dict):
        urls = {}
        for lang, tracks in subs_dict.items():
            ttml_url = None
            vtt_url = None
            for track in tracks:
                ext = track.get("ext")
                if ext == "ttml" and not ttml_url:
                    ttml_url = track.get("url")
                elif ext == "vtt" and not vtt_url:
                    vtt_url = track.get("url")
            # Ưu tiên TTML, fallback sang VTT nếu không có
            if ttml_url:
                urls[lang] = {"ext": "ttml", "url": ttml_url}
            elif vtt_url:
                urls[lang] = {"ext": "vtt", "url": vtt_url}
        return urls

    subtitles = info_dict.get("subtitles", {})
    auto_captions = info_dict.get("automatic_captions", {})

    return {
        "official_subtitles": extract_urls(subtitles),
        "automatic_captions": extract_urls(auto_captions)
    }

def get_subtitle_urls(info_dict):
    def extract_urls(subs_dict):
        urls = {}
        for lang, tracks in subs_dict.items():
            ttml_url = None
            vtt_url = None
            for track in tracks:
                ext = track.get("ext")
                if ext == "ttml" and not ttml_url:
                    ttml_url = track.get("url")
                elif ext == "vtt" and not vtt_url:
                    vtt_url = track.get("url")
            # Ưu tiên TTML, fallback sang VTT nếu không có
            if ttml_url:
                urls[lang] = {"ext": "ttml", "url": ttml_url}
            elif vtt_url:
                urls[lang] = {"ext": "vtt", "url": vtt_url}
        return urls

    subtitles = info_dict.get("subtitles", {})
    auto_captions = info_dict.get("automatic_captions", {})

    return {
        "official_subtitles": extract_urls(subtitles),
        "automatic_captions": extract_urls(auto_captions)
    }
# subtitle_data = get_subtitle_urls(info_dict)
# print(subtitle_data)

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
                'start': time_to_seconds(begin),
                'end': time_to_seconds(end),
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

#--- sidebar ben trai--------------------------

with st.sidebar:
    st.title("🤖 Xem youtube với phụ đề dịch nói")
    video_url = st.text_input("🔗 Nhập URL video YouTube: vd:  https://www.youtube.com/watch?v=Xwb1OrkPupM&t=5s", "")

    use_cookies = st.checkbox("📂 Dùng cookies.txt (nếu bị chặn)")
    use_proxy = st.checkbox("🌍 Dùng proxy")

    # Tuỳ chọn proxy
    proxy_url = ""
    if use_proxy:
        proxy_url = st.text_input("Proxy URL (VD: http://123.45.67.89:8080)", "")

    # kiem tra xem video_url co hop le khong
    vid = parse_youtube_url(video_url)
    #st.write(f"{video_url!r} ->", "YouTube ID =" , vid if vid else "Không phải YouTube")

    if st.button("Lấy thông tin") and vid:
        tbaodong1 = st.empty()
        tbaodong1.write('⏳ Đang xử lý...')

        #st.info("⏳ Đang xử lý...")
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'ratelimit': 500000,  # giới hạn tốc độ tải: 500 KB/s
            'sleep_interval_requests': 2,  # nghỉ 2 giây giữa các request
            'skip_download': True,
            'forcejson': True,
        }

        if use_cookies:
            ydl_opts['cookiefile'] = 'cookies.txt'

        if use_proxy and proxy_url:
            ydl_opts['proxy'] = proxy_url

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video_url, download=False)
                videoID = info_dict['id']
                # xet phu de                    
                subtitle_data = get_subtitle_urls(info_dict)
                #st.write(subtitle_data)

                # xet phu de truyen thong
                if subtitle_data["official_subtitles"] != {}:
                    if subtitle_data["official_subtitles"]["en"]:
                        dangPdEn = subtitle_data["official_subtitles"]["en"]["ext"]
                        urlPdEn = subtitle_data["official_subtitles"]["en"]["url"]
                        ttLayPdEn = [dangPdEn, urlPdEn]
                        #st.write(ttLayPdEn)   
                        f = requests.get(ttLayPdEn[1])
                        if dangPdEn == "ttml":
                            ttml_content = f.text
                            subtitles = parse_ttml_with_seconds(ttml_content)
                            #st.write('pdtt','ttml')
                            #st.write(subtitles)

                        elif dangPdEn == "vtt":
                            vtt_content = f.text
                        else:
                            subtitles = ''
                elif subtitle_data["automatic_captions"] != {}:
                    if subtitle_data["automatic_captions"]["en"]:
                        dangPdEn = subtitle_data["automatic_captions"]["en"]["ext"]
                        urlPdEn = subtitle_data["automatic_captions"]["en"]["url"]
                        ttLayPdEn = [dangPdEn, urlPdEn]
                        #st.write(ttLayPdEn)   
                        f = requests.get(ttLayPdEn[1])
                        if dangPdEn == "ttml":
                            ttml_content = f.text
                            subtitles = parse_ttml_with_seconds(ttml_content)
                            #st.write('pdauto','ttml')
                            #st.write(subtitles)

                        elif dangPdEn == "vtt":
                            vtt_content = f.text
                        else:
                            subtitles = ''
                else:
                    subtitles = ''
                    #st.write('No Pd')

                # Hiển thị một số thông tin cơ bản
                st.subheader("📄 Thông tin video:")
                st.write(f"**Tiêu đề:** {info_dict.get('title')}")
                st.write(f"**Tác giả:** {info_dict.get('uploader')}")
                st.write(f"**Thời lượng:** {info_dict.get('duration')} giây")
                st.write(f"**Lượt xem:** {info_dict.get('view_count')}")
                st.write(f"**Ngày đăng:** {info_dict.get('upload_date')}")
                st.write(f"**Trực tiếp:** {'Có' if info_dict.get('is_live') else 'Không'}")
                st.write(f"**Phụ đề:** {'Có' if subtitles else 'Không'}")

                #with st.expander("📦 Xem toàn bộ info_dict"):
                #    st.json(info)


                html_code = lap_html_video(videoID, subtitles)   
                tbaodong1.write('✅ Đã đủ thông tin và youtube đang hiển thị.')

        except Exception as e:
            st.error(f"❌ Lỗi: {str(e)}")
    #else:
    #    tbaodong1 = st.empty()  # giu cho roi ghi vao 
    #    tbaodong1.write('❌ Thông tin nhập không hợp lệ hoặc chưa nhập!')

#-------man hinh chinh-------------------------
#st.write('🤖YouTube với phụ để dịch nói')
if videoID and html_code:
    #st.write('Da co videoId and subtitlesJson')
    #st.title("🎤 Subtitle Viewer with Word-by-Word Voice Highlight")
    components.html(html_code, height=600, scrolling=True)

    # https://www.ted.com/talks/148348 TED 8P khong co caption
    # https://www.youtube.com/watch?v=6Af6b_wyiwI&t=4s 8p bilgate
    # https://www.youtube.com/watch?v=mO2Nwv2xSyQ   #VOA
    #"https://www.ted.com/talks/148348",  # TED 8P khong co caption
    #"https://www.youtube.com/watch?v=6Af6b_wyiwI&t=4s" # 8p bilgate
    #"https://www.youtube.com/watch?v=tPIboKLoXg8&t=1s" # VOA bai hoc
    #"https://youtu.be/Zgfi7wnGZlE?si=TzeWpiERRxzdJKVA" # obama

    # tien89talkenvi\st_tien.py
    # tien89talkenvi\gpt_cho.py
