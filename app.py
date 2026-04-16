import streamlit as st
import os
from io import BytesIO
from pytubefix import YouTube
from pytubefix.cli import on_progress

st.set_page_config(page_title="YouTube Downloader", page_icon="▶️", layout="wide")

# Custom CSS to mimic Y2Mate design
st.markdown("""
<style>
    /* Reset some basic elements */
    .stApp {
        background-color: #f9f9f9;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Top navbar styling */
    .navbar {
        background-color: #fff;
        padding: 15px 50px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #ddd;
        margin-top: -60px;
        margin-bottom: 30px;
        margin-left: -50px;
        margin-right: -50px;
    }
    .logo {
        color: #ff0066;
        font-size: 28px;
        font-weight: bold;
        text-decoration: none;
    }
    .nav-links {
        display: flex;
        gap: 20px;
        align-items: center;
    }
    .nav-links a {
        text-decoration: none;
        color: #555;
        font-size: 14px;
        font-weight: 500;
    }
    .lang-btn {
        background-color: #ff0066;
        color: white;
        border: none;
        padding: 8px 15px;
        border-radius: 4px;
        cursor: pointer;
    }
    
    /* Main converter box */
    .converter-box {
        background-color: white;
        padding: 40px;
        border-radius: 4px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        text-align: center;
        max-width: 800px;
        margin: 0 auto;
        border: 1px solid #e0e0e0;
    }
    
    .converter-title {
        color: #666;
        font-size: 32px;
        margin-bottom: 25px;
        font-weight: 400;
    }
    
    /* Input area */
    .input-container {
        display: flex;
        margin-bottom: 15px;
    }
    
    /* Features section */
    .features-section {
        max-width: 1000px;
        margin: 50px auto;
    }
    
    .section-title {
        text-align: center;
        color: #666;
        font-size: 28px;
        margin-bottom: 20px;
        font-weight: 400;
    }
    
    .section-text {
        text-align: justify;
        color: #555;
        line-height: 1.6;
        font-size: 14px;
        margin-bottom: 40px;
    }
    
    .grid-2 {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 40px;
        margin-bottom: 40px;
    }
    
    .grid-3 {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 30px;
        text-align: center;
    }
    
    .feature-icon {
        font-size: 30px;
        color: #333;
        margin-bottom: 15px;
    }
    
    .feature-title {
        font-weight: bold;
        margin-bottom: 10px;
        color: #333;
    }
    
    .feature-desc {
        color: #666;
        font-size: 13px;
        line-height: 1.5;
    }
    
    /* Footer */
    .footer {
        border-top: 1px solid #ddd;
        padding: 40px 0;
        margin-top: 50px;
        display: grid;
        grid-template-columns: 2fr 1fr 1fr 1fr;
        gap: 20px;
        max-width: 1000px;
        margin-left: auto;
        margin-right: auto;
        color: #555;
        font-size: 13px;
    }
    
    .footer-col h4 {
        color: #333;
        margin-bottom: 15px;
        font-size: 14px;
    }
    
    .footer-col a {
        display: block;
        color: #555;
        text-decoration: none;
        margin-bottom: 8px;
    }
    
    .copyright {
        text-align: center;
        padding: 20px;
        color: #888;
        font-size: 13px;
        border-top: 1px solid #eee;
    }
    
    /* Streamlit overrides */
    .stTextInput > div > div > input {
        border-radius: 4px 0 0 4px !important;
        border: 2px solid #ff0066 !important;
        padding: 12px 15px !important;
        font-size: 16px !important;
    }
    
    .stButton > button {
        background-color: #ff0066 !important;
        color: white !important;
        border: none !important;
        border-radius: 0 4px 4px 0 !important;
        padding: 12px 30px !important;
        font-size: 16px !important;
        font-weight: bold !important;
        height: 100% !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        background-color: #e6005c !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Navbar
st.markdown("""
<div class="navbar">
    <a href="#" class="logo">Y2Mate</a>
    <div class="nav-links">
        <a href="#">🏠 Home</a>
        <a href="#">🎵 YouTube to MP3</a>
        <a href="#">🎦 YouTube to MP4</a>
        <button class="lang-btn">English ▼</button>
    </div>
</div>
""", unsafe_allow_html=True)

# Main container
col1, col2, col3 = st.columns([1, 6, 1])

with col2:
    st.markdown('<div class="converter-box">', unsafe_allow_html=True)
    st.markdown('<h1 class="converter-title">Youtube to MP4 Converter</h1>', unsafe_allow_html=True)
    
    # Initialize session state variables
    if 'current_url' not in st.session_state:
        st.session_state.current_url = ""
    if 'yt_info' not in st.session_state:
        st.session_state.yt_info = None
    if 'video_ready' not in st.session_state:
        st.session_state.video_ready = False
    if 'audio_ready' not in st.session_state:
        st.session_state.audio_ready = False
    if 'video_path' not in st.session_state:
        st.session_state.video_path = ""
    if 'audio_path' not in st.session_state:
        st.session_state.audio_path = ""

    # Input form
    form_col1, form_col2 = st.columns([4, 1])
    with form_col1:
        url = st.text_input("URL", label_visibility="collapsed", placeholder="Search or paste Youtube link here...")
    with form_col2:
        start_btn = st.button("Start ➔")
    
    if start_btn and url:
        st.session_state.current_url = url
        st.session_state.video_ready = False
        st.session_state.audio_ready = False
        st.session_state.video_path = ""
        st.session_state.audio_path = ""
        try:
            with st.spinner("Fetching video information..."):
                # Using client='IOS' to bypass YouTube's WEB player cipher issues and avoid creator login requirements
                yt = YouTube(url, client='IOS')
                st.session_state.yt_info = {"title": yt.title, "url": url}
        except Exception as e:
            st.session_state.yt_info = None
            st.error(f"Error fetching video: {str(e)}")

    st.markdown('<p style="font-size: 12px; color: #777; margin-top: 15px;">By using our service you are accepting our <a href="#" style="color: #555;">terms of service.</a></p>', unsafe_allow_html=True)
    st.markdown('<div style="background-color: #f8f9fa; padding: 10px; border-top: 1px solid #eee; margin-top: 20px;"><p style="font-size: 13px; color: #555; margin: 0;"><b>Tip:</b> Insert "<b>pi</b>" after "<b>youtube</b>" in the URL bar to download mp4 and mp3 files from Youtube in a faster way.</p></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Download logic
    if st.session_state.yt_info and st.session_state.current_url:
        st.success(f"Found: {st.session_state.yt_info['title']}")
        
        dl_col1, dl_col2 = st.columns(2)
        os.makedirs("temp_downloads", exist_ok=True)
        
        with dl_col1:
            st.info("Video (MP4)")
            if not st.session_state.video_ready:
                if st.button("Prepare Video Download", key="prep_vid"):
                    with st.spinner("Downloading video to server..."):
                        try:
                            yt = YouTube(st.session_state.current_url, client='IOS')
                            video_stream = yt.streams.get_highest_resolution()
                            video_path = video_stream.download(output_path="temp_downloads")
                            st.session_state.video_path = video_path
                            st.session_state.video_ready = True
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to prepare video: {e}")
            else:
                if os.path.exists(st.session_state.video_path):
                    with open(st.session_state.video_path, "rb") as file:
                        st.download_button(
                            label="📥 Download Video",
                            data=file,
                            file_name=f"{st.session_state.yt_info['title']}.mp4",
                            mime="video/mp4",
                            key="dl_vid"
                        )
                        
        with dl_col2:
            st.info("Audio (MP3/M4A)")
            if not st.session_state.audio_ready:
                if st.button("Prepare Audio Download", key="prep_aud"):
                    with st.spinner("Downloading audio to server..."):
                        try:
                            yt = YouTube(st.session_state.current_url, client='IOS')
                            audio_stream = yt.streams.get_audio_only()
                            audio_path = audio_stream.download(output_path="temp_downloads")
                            st.session_state.audio_path = audio_path
                            st.session_state.audio_ready = True
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to prepare audio: {e}")
            else:
                if os.path.exists(st.session_state.audio_path):
                    with open(st.session_state.audio_path, "rb") as file:
                        st.download_button(
                            label="📥 Download Audio",
                            data=file,
                            file_name=f"{st.session_state.yt_info['title']}.m4a",
                            mime="audio/m4a",
                            key="dl_aud"
                        )

# Content section
st.markdown("""
<div class="features-section">
    <h2 class="section-title">Y2Mate: Best Youtube to MP4 Downloader</h2>
    <p class="section-text">
        Y2Mate helps you to convert and download Youtube videos to mp4 format for free in HD without any signup. All You have to do is Just insert the Youtube link in the search box; we will auto fetch the video information. Click on your required video quality and wait for a few seconds to complete the conversion process. The conversion process doesn't affect the video quality. Y2Mate is the fastest Youtube MP4 Converter to convert & download your desired YT videos for offline viewing, converted mp4 files will be saved permanently on your device storage. You can download the youtube videos to any specific quality like 144p, 240p, 360p, 480p, 720p, 1080p. moreover, it's completely free and safe.
    </p>
    
    <div class="grid-2">
        <div>
            <h3 style="color:#333; font-size:18px; margin-bottom:15px;">How to Download Youtube to MP4 with Y2Mate?</h3>
            <ol style="color:#555; font-size:14px; line-height:1.8; padding-left:15px;">
                <li>Open Youtube and copy the video URL you want to download in MP4.</li>
                <li>Paste the video URL in the Search box, Tool will fetch video info.</li>
                <li>Select the Video quality you need and click the "Convert" button.</li>
                <li>After the conversion is successfully completed, hit the "Download" button.</li>
                <li>Once the video is downloaded, you can play it whenever and wherever you want.</li>
            </ol>
        </div>
        <div>
            <h3 style="color:#333; font-size:18px; margin-bottom:15px;">Why use our Youtube to MP4 Downloader?</h3>
            <ol style="color:#555; font-size:14px; line-height:1.8; padding-left:15px;">
                <li>Unlimited Conversions, so you can convert all your videos.</li>
                <li>We use the Latest Technology to convert Youtube videos faster.</li>
                <li>We Offer Unlimited Downloads, Download as much as you can.</li>
                <li>No Signup/Form submission required, our service is totally free.</li>
                <li>We support multiple qualities, e.g., 360p, 480p, 720p, and 1080p.</li>
            </ol>
        </div>
    </div>
    
    <div class="grid-3">
        <div>
            <div class="feature-icon">⏱️</div>
            <div class="feature-title">Faster Conversion</div>
            <div class="feature-desc">We use the best Servers for the conversion of your Youtube Video to MP4, moreover, the encoding will not reduce the video quality.</div>
        </div>
        <div>
            <div class="feature-icon">✔️</div>
            <div class="feature-title">Easy to use</div>
            <div class="feature-desc">Our interface is simple and easy to use, You just have to paste the video link (URL) of a Youtube video and we will do the rest.</div>
        </div>
        <div>
            <div class="feature-icon">🎁</div>
            <div class="feature-title">100% Free Downloads</div>
            <div class="feature-desc">Our YT MP4 converter and downloader is a free online service, also there are no restrictions about the number of files you want to convert.</div>
        </div>
        <div>
            <div class="feature-icon">⛔</div>
            <div class="feature-title">No Subscription Required</div>
            <div class="feature-desc">Youtube offers a premium subscription service to download videos for offline viewing. However, with Y2Mate, you can download your favorite videos to mp4 without buying a subscription.</div>
        </div>
        <div>
            <div class="feature-icon">HD</div>
            <div class="feature-title">Download HD Videos</div>
            <div class="feature-desc">Youtube reduces the video quality to stream without interruption. With Y2Mate, you can save videos in their original HD format without losing quality.</div>
        </div>
        <div>
            <div class="feature-icon">▶️</div>
            <div class="feature-title">Watch Offline Anytime</div>
            <div class="feature-desc">Download youtube videos and save them in mp4 format to watch anytime, anywhere, without using your internet data. It's also useful when traveling in areas without internet connectivity.</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    <div class="footer-col">
        <h4>Disclaimer</h4>
        <p style="color:#777; line-height:1.5;">Y2Mate is an independent tool and is not affiliated with YouTube. Use it responsibly and respect content creators' rights.</p>
    </div>
    <div class="footer-col">
        <h4>Pages</h4>
        <a href="#">F.A.Q.</a>
        <a href="#">Contact Us</a>
    </div>
    <div class="footer-col">
        <h4>Legal</h4>
        <a href="#">Privacy Policy</a>
        <a href="#">Terms of Service</a>
    </div>
    <div class="footer-col">
        <h4>More Tools</h4>
        <a href="#">Shorts Downloader</a>
        <a href="#">Donate to Y2Mate ❤️</a>
    </div>
</div>
<div class="copyright">
    © 2026 Y2Mate.is - All Rights Reserved.
</div>
""", unsafe_allow_html=True)
