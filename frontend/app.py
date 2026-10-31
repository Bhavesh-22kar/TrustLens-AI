import html
import json
import os
from datetime import datetime
from typing import Any

import requests
import streamlit as st

st.set_page_config(
    page_title="TrustLens AI | Intelligent News Verification",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Deployed FastAPI backend
API_BASE_URL = os.getenv(
    "TRUSTLENS_API_URL",
    "https://backend-3331680c.fastapicloud.dev",
).rstrip("/")
MAX_TEXT_CHARS = 10_000
MAX_CONTEXT_CHARS = 5_000
MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_VIDEO_BYTES = 50 * 1024 * 1024
IMAGE_TYPES = ["jpg", "jpeg", "png", "webp"]
VIDEO_TYPES = ["mp4", "webm", "mov", "avi"]
PAGES = ["Overview", "Text Analysis", "Image Analysis", "Video Analysis", "Multimodal Analysis", "Analysis History", "About Project"]

# ---------- Premium visual system ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');
:root{--ink:#14213d;--muted:#68758d;--blue:#4169e1;--cyan:#19b8c9;--line:#e5ebf5;--surface:#ffffff;}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;}
.stApp{background:radial-gradient(ellipse at 82% 0%,rgba(65,105,225,.10),transparent 34%),linear-gradient(180deg,#f7f9fe 0%,#f1f5fb 100%);color:var(--ink);}
.block-container{max-width:1380px;padding-top:1.2rem;padding-bottom:3rem;}
[data-testid="stHeader"]{background:rgba(247,249,254,.88);}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#101d38 0%,#172b4d 100%);border-right:1px solid rgba(255,255,255,.08);}
[data-testid="stSidebar"] *{color:#eaf1ff!important;}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p{color:#aebed9!important;}
[data-testid="stSidebar"] hr{border-color:rgba(255,255,255,.16);}
.brand-mark{display:flex;align-items:center;gap:11px;padding:.55rem .2rem 1.1rem;}
.brand-icon{width:42px;height:42px;border-radius:14px;background:linear-gradient(135deg,#4c7dff,#20c6cf);display:flex;align-items:center;justify-content:center;font-size:22px;box-shadow:0 8px 22px rgba(31,151,211,.28);}
.brand-name{font-family:'Space Grotesk',sans-serif;font-size:1.38rem;font-weight:700;letter-spacing:-.7px;color:#fff;}
.brand-name span{color:#65dce4;}
.sidebar-note{font-size:.78rem;color:#9fb2d2!important;margin-top:-.45rem;margin-bottom:1.1rem;}
.side-label{font-size:.7rem;letter-spacing:1.5px;text-transform:uppercase;color:#8298bb!important;font-weight:700;margin:.8rem 0 .35rem;}
.hero{position:relative;overflow:hidden;padding:2.1rem 2.25rem;border-radius:25px;background:linear-gradient(115deg,#142747 0%,#1b3b70 56%,#245ca3 100%);color:white;margin:.2rem 0 1.4rem;box-shadow:0 18px 45px rgba(24,54,103,.18);}
.hero:after{content:' ';position:absolute;width:330px;height:330px;border-radius:50%;right:-75px;top:-180px;border:1px solid rgba(255,255,255,.16);box-shadow:0 0 0 35px rgba(255,255,255,.035),0 0 0 75px rgba(255,255,255,.025);}
.hero-kicker{font-size:.76rem;text-transform:uppercase;letter-spacing:2px;font-weight:700;color:#8ce5eb;margin-bottom:.7rem;}
.hero h1{font-family:'Space Grotesk',sans-serif;font-size:2.45rem;line-height:1.1;letter-spacing:-1.2px;color:#fff;margin:0 0 .7rem;}
.hero p{max-width:720px;color:#d4e1f6;font-size:1rem;line-height:1.65;margin:0;}
.hero-chip{display:inline-flex;align-items:center;gap:7px;margin-top:1.2rem;padding:.48rem .8rem;border-radius:999px;background:rgba(255,255,255,.11);border:1px solid rgba(255,255,255,.16);font-size:.78rem;color:#e8f7ff;}
.section-head{display:flex;align-items:flex-end;justify-content:space-between;gap:1rem;margin:1.35rem 0 .85rem;}
.section-head h2{font-family:'Space Grotesk',sans-serif;font-size:1.45rem;color:#172746;margin:0;letter-spacing:-.5px;}
.section-head p{margin:0;color:var(--muted);font-size:.88rem;}
.surface{background:#fff;border:1px solid var(--line);border-radius:19px;padding:1.15rem 1.25rem;box-shadow:0 8px 26px rgba(32,61,110,.045);}
.feature-card{height:100%;min-height:168px;background:linear-gradient(150deg,#fff 0%,#f8fbff 100%);border:1px solid #e3eaf5;border-radius:19px;padding:1.2rem;box-shadow:0 8px 24px rgba(36,65,112,.045);}
.feature-icon{width:43px;height:43px;border-radius:13px;display:flex;align-items:center;justify-content:center;background:#eaf1ff;font-size:1.35rem;margin-bottom:.85rem;}
.feature-card h3{font-family:'Space Grotesk',sans-serif;color:#1b2b49;font-size:1.08rem;margin:0 0 .35rem;}
.feature-card p{color:#718099;font-size:.86rem;line-height:1.5;margin:0;}
.metric{background:#fff;border:1px solid #e4eaf4;border-radius:17px;padding:1.05rem 1.15rem;box-shadow:0 7px 22px rgba(35,60,105,.04);min-height:112px;}
.metric-label{font-size:.72rem;font-weight:800;letter-spacing:1px;color:#8190a8;text-transform:uppercase;}
.metric-value{font-family:'Space Grotesk',sans-serif;font-size:1.8rem;font-weight:700;color:#2458c6;margin-top:.35rem;}
.metric-sub{font-size:.76rem;color:#8b97aa;margin-top:.1rem;}
.result-banner{background:linear-gradient(110deg,#eaf2ff,#effbfc);border:1px solid #dbe8fb;border-radius:16px;padding:1rem 1.15rem;margin:.8rem 0 1rem;}
.result-banner strong{font-family:'Space Grotesk',sans-serif;font-size:1.25rem;color:#17376c;}
.status-pill{display:inline-block;padding:.42rem .85rem;border-radius:999px;background:#fff2cc;color:#895a00;font-weight:800;font-size:.82rem;border:1px solid #ffe4a1;}
.info-tile{background:#fff;border:1px solid var(--line);border-radius:16px;padding:1rem;height:100%;}
.info-tile h4{margin:0 0 .35rem;color:#243858;font-size:.95rem;}
.info-tile p{margin:0;color:#75839a;font-size:.83rem;line-height:1.5;}
div.stButton>button{border-radius:11px;border:1px solid #d9e2f0;font-weight:700;min-height:2.65rem;transition:all .18s ease;}
div.stButton>button[kind="primary"]{background:linear-gradient(110deg,#4169e1,#2854bf);border:0;color:white;box-shadow:0 7px 18px rgba(48,91,202,.2);}
div.stButton>button[kind="primary"]:hover{background:linear-gradient(110deg,#315bd2,#1f479f);transform:translateY(-1px);}
.stTextArea textarea,.stTextInput input{border-radius:12px!important;border-color:#dce5f1!important;background:#fff!important;}
[data-testid="stFileUploader"]{background:#fff;border:1px dashed #a9bddc;border-radius:15px;padding:.5rem;}
[data-testid="stProgressBar"]>div>div{background:linear-gradient(90deg,#4169e1,#19b8c9);}
div[data-testid="stExpander"]{border:1px solid #e3eaf4;border-radius:13px;background:#fff;}
.footer{margin-top:2.5rem;padding:1.1rem 0;border-top:1px solid #e2e9f3;text-align:center;color:#8b97aa;font-size:.78rem;}
.small-muted{color:#7d8ba2;font-size:.82rem;}
@media(max-width:800px){.hero{padding:1.5rem}.hero h1{font-size:1.85rem}.block-container{padding-left:1rem;padding-right:1rem;}}
</style>
""", unsafe_allow_html=True)

# ---------- State ----------
for key, default in {
    "history": [], "latest_result": None, "api_base": API_BASE_URL,
    "latest_response": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ---------- API helpers ----------
def api_url(endpoint: str) -> str:
    return st.session_state.api_base.rstrip("/") + endpoint

def parse_api_response(response: requests.Response) -> dict:
    """Validate the HTTP response and normalize backend errors."""
    try:
        data = response.json()
    except ValueError:
        body = (response.text or "")[:500]
        raise RuntimeError(
            f"Backend returned non-JSON content (HTTP {response.status_code}): {body}"
        )

    if not response.ok:
        detail = data.get("detail") or data.get("error") or data.get("message")
        if isinstance(detail, (dict, list)):
            detail = json.dumps(detail, ensure_ascii=False)
        raise RuntimeError(str(detail or f"Backend returned HTTP {response.status_code}"))

    if not isinstance(data, dict):
        raise RuntimeError("Unexpected backend response format.")
    if data.get("success") is False:
        raise RuntimeError(str(data.get("error") or data.get("message") or "Analysis failed."))
    if not isinstance(data.get("result"), dict):
        raise RuntimeError(
            "The backend response did not contain a valid 'result' object. "
            "Check the endpoint response format in FastAPI /docs."
        )
    return data

def call_text_api(text: str) -> dict:
    try:
        response = requests.post(
            api_url("/analyze-text"),
            json={"news_text": text},
            timeout=(15, 300),
        )
        return parse_api_response(response)
    except requests.exceptions.Timeout as exc:
        raise RuntimeError("Text analysis timed out. Please try again in a moment.") from exc
    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(
            "Could not connect to FastAPI Cloud. Check the backend URL and deployment status."
        ) from exc

def call_file_api(endpoint: str, uploaded_file, context: str = "") -> dict:
    """Send one uploaded image/video using the backend's `file` + `context` fields."""
    uploaded_file.seek(0)
    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            uploaded_file.type or "application/octet-stream",
        )
    }
    try:
        response = requests.post(
            api_url(endpoint),
            files=files,
            data={"context": context},
            timeout=(15, 600),
        )
        return parse_api_response(response)
    except requests.exceptions.Timeout as exc:
        raise RuntimeError(
            "The media analysis timed out. Video analysis can take longer; please retry with a smaller file."
        ) from exc
    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError("Could not connect to the deployed FastAPI backend.") from exc

def call_multimodal_api(text: str, image_file=None, video_file=None) -> dict:
    """Send multimodal fields matching the FastAPI endpoint signature."""
    files = {}
    if image_file is not None:
        image_file.seek(0)
        files["image"] = (
            image_file.name, image_file.getvalue(),
            image_file.type or "application/octet-stream",
        )
    if video_file is not None:
        video_file.seek(0)
        files["video"] = (
            video_file.name, video_file.getvalue(),
            video_file.type or "application/octet-stream",
        )
    try:
        response = requests.post(
            api_url("/analyze-multimodal"),
            data={"news_text": text},
            files=files or None,
            timeout=(15, 900),
        )
        return parse_api_response(response)
    except requests.exceptions.Timeout as exc:
        raise RuntimeError("Multimodal analysis timed out. Try a smaller media file.") from exc
    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError("Could not connect to the deployed FastAPI backend.") from exc

def score_number(value: Any, default: float = 0) -> float:
    try:
        if isinstance(value, str):
            value = value.strip().replace("%", "")
        return max(0.0, min(100.0, float(value)))
    except (TypeError, ValueError):
        return default

def save_result(result: dict, content_type: str, description: str, response_data: dict | None = None):
    item = dict(result)
    item.update({"content_type": content_type, "news_text": description, "analyzed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    st.session_state.latest_result = item
    st.session_state.history.insert(0, item)
    st.session_state.history = st.session_state.history[:20]
    st.session_state.latest_response = response_data

def render_result(result: dict, meta: dict | None = None):
    classification = str(result.get("classification") or "Uncertain")
    confidence = score_number(result.get("confidence"))
    trust = score_number(result.get("trust_score"))
    status = str(result.get("verification_status") or "Needs Further Verification")
    safe_classification = html.escape(classification)
    safe_status = html.escape(status)
    st.markdown(
        f'<div class="result-banner"><div class="small-muted">TRUSTLENS AI ASSESSMENT</div>'
        f'<strong>{safe_classification}</strong><div style="margin-top:.45rem">'
        f'<span class="status-pill">{safe_status}</span></div></div>',
        unsafe_allow_html=True,
    )
    a, b, c = st.columns(3)
    for col, label, value, sub in [
        (a, "Model confidence", f"{confidence:g}%", "Confidence in the AI assessment"),
        (b, "Trust score", f"{trust:g}/100", "Estimated credibility indicator"),
        (c, "Verification status", status, "Evidence assessment returned by model"),
    ]:
        with col:
            st.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value" style="font-size:{"1.25rem" if label == "Verification status" else "1.8rem"}">{value}</div><div class="metric-sub">{sub}</div></div>', unsafe_allow_html=True)
            if label != "Verification status":
                st.progress(int(value.split("/")[0].replace("%", "")))
    st.markdown("### 🧠 AI Explanation")
    st.markdown('<div class="surface">', unsafe_allow_html=True)
    st.write(result.get("explanation") or "No explanation available.")
    st.markdown('</div>', unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        st.markdown("### 🚩 Key Concerns")
        concerns = result.get("key_concerns") or []
        if isinstance(concerns, list) and concerns:
            for concern in concerns:
                st.write(f"• {concern}")
        else:
            st.info("No specific concerns were returned by the model.")
    with right:
        st.markdown("### 💡 Recommendation")
        st.markdown('<div class="surface">', unsafe_allow_html=True)
        st.write(result.get("recommendation") or "Verify this information using reliable sources before sharing.")
        st.markdown('</div>', unsafe_allow_html=True)
    extra = {k: v for k, v in result.items() if k not in {"classification", "confidence", "trust_score", "verification_status", "explanation", "key_concerns", "recommendation", "content_type", "news_text", "analyzed_at"}}
    if extra or meta:
        with st.expander("View technical analysis details"):
            if extra:
                st.json(extra)
            if meta:
                st.json(meta)
    st.caption("Research note: AI-generated classifications and scores are assessments, not proof of factual authenticity. Verify important claims with reliable primary sources.")

def show_downloads(item: dict):
    raw = json.dumps(item, indent=2, ensure_ascii=False, default=str)
    report = (
        "TrustLens AI — Analysis Report\n" + "=" * 34 + "\n\n"
        f"Type: {item.get('content_type', 'analysis')}\nDate: {item.get('analyzed_at', '')}\n"
        f"Classification: {item.get('classification', 'Uncertain')}\nConfidence: {item.get('confidence', 0)}\n"
        f"Trust score: {item.get('trust_score', 0)}/100\nStatus: {item.get('verification_status', 'Needs Further Verification')}\n\n"
        f"Explanation:\n{item.get('explanation', '')}\n\nKey concerns:\n"
        + "\n".join(f"- {x}" for x in (item.get("key_concerns") or []))
        + f"\n\nRecommendation:\n{item.get('recommendation', '')}\n"
    )
    x, y = st.columns(2)
    with x:
        st.download_button("⬇️ Download JSON", raw, "trustlens_analysis.json", "application/json", use_container_width=True)
    with y:
        st.download_button("📄 Download report", report, "trustlens_report.txt", "text/plain", use_container_width=True)

def page_intro(eyebrow: str, title: str, description: str, icon: str):
    st.markdown(f'<div class="section-head"><div><p>{eyebrow}</p><h2>{icon} {title}</h2></div></div><p class="small-muted" style="margin-top:-.5rem;margin-bottom:1.1rem">{description}</p>', unsafe_allow_html=True)

def display_latest(content_type: str):
    item = st.session_state.latest_result
    if item and item.get("content_type") == content_type:
        st.divider()
        page_intro("YOUR RESULT", "Analysis report", "Review the assessment generated for your latest submission.", "📊")
        render_result(item, item.get("multimodal_meta"))
        show_downloads(item)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown('<div class="brand-mark"><div class="brand-icon">🔎</div><div class="brand-name">TrustLens <span>AI</span></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-note">INTELLIGENT NEWS CREDIBILITY STUDIO</div>', unsafe_allow_html=True)
    st.markdown('<div class="side-label">Connection</div>', unsafe_allow_html=True)
    st.session_state.api_base = st.text_input("FastAPI backend URL", value=st.session_state.api_base, label_visibility="collapsed", help="Your deployed FastAPI base URL. Default is the TrustLens AI cloud deployment.")
    if st.button("↗ Check backend connection", use_container_width=True):
        try:
            r = requests.get(api_url("/health"), timeout=(5, 15))
            r.raise_for_status()
            health_data = r.json()
            st.success("Backend is reachable")
            st.caption(f"Health response: {health_data}")
        except requests.RequestException as exc:
            st.error(f"Backend unavailable: {exc}")
    st.markdown('<div class="side-label">Workspace</div>', unsafe_allow_html=True)
    page = st.radio("Navigate", PAGES, label_visibility="collapsed", format_func=lambda p: {
        "Overview":"🏠  Overview", "Text Analysis":"📰  Text analysis", "Image Analysis":"🖼️  Image analysis",
        "Video Analysis":"🎬  Video analysis", "Multimodal Analysis":"🔗  Multimodal analysis",
        "Analysis History":"🗂️  Analysis history", "About Project":"ℹ️  About project"}[p])
    st.divider()
    st.markdown('<div class="sidebar-note">MCA RESEARCH PROJECT · V1</div>', unsafe_allow_html=True)
    st.caption(f"{len(st.session_state.history)} analyses in this session")

# ---------- Hero ----------
st.markdown('''<div class="hero"><div class="hero-kicker">✦ AI-POWERED CREDIBILITY INTELLIGENCE</div><h1>See beyond the headline.</h1><p>Explore news credibility with explainable AI. Analyze text, images, videos, or combine multiple formats to surface signals, concerns, and context.</p><div class="hero-chip">● Multi-modal analysis&nbsp;&nbsp; · &nbsp;&nbsp;Explainable insights&nbsp;&nbsp; · &nbsp;&nbsp;One workspace</div></div>''', unsafe_allow_html=True)

# ---------- Pages ----------
if page == "Overview":
    page_intro("YOUR VERIFICATION WORKSPACE", "Choose what you want to investigate", "Start with one content type or combine formats for a broader assessment.", "✦")
    cards = [
        ("📰", "Text analysis", "Review headlines, articles, claims, and social posts.", "Text Analysis"),
        ("🖼️", "Image analysis", "Inspect news photographs, screenshots, and visual claims.", "Image Analysis"),
        ("🎬", "Video analysis", "Assess video clips and the context supplied with them.", "Video Analysis"),
        ("🔗", "Multimodal analysis", "Compare text, image, and video inputs together.", "Multimodal Analysis"),
    ]
    cols = st.columns(4)
    for col, (icon, title, desc, _) in zip(cols, cards):
        with col:
            st.markdown(f'<div class="feature-card"><div class="feature-icon">{icon}</div><h3>{title}</h3><p>{desc}</p></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    for col, label, value, sub in [
        (c1, "Analysis this session", str(len(st.session_state.history)), "Recent checks stored in this session"),
        (c2, "Input modes", "04", "Text · Image · Video · Multimodal"),
        (c3, "Backend", "FastAPI", "Connected to deployed cloud API"),
    ]:
        with col:
            st.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-sub">{sub}</div></div>', unsafe_allow_html=True)
    st.markdown("### A simple verification workflow")
    steps = st.columns(3)
    for col, n, title, desc in zip(steps, ["01", "02", "03"], ["Submit content", "Review AI signals", "Make an informed decision"], ["Paste a claim or upload media.", "Read the score, explanation, and concerns.", "Cross-check important claims with primary sources."]):
        with col:
            st.markdown(f'<div class="info-tile"><div class="metric-label">STEP {n}</div><h4>{title}</h4><p>{desc}</p></div>', unsafe_allow_html=True)
    if st.session_state.latest_result:
        st.markdown("### Latest assessment")
        render_result(st.session_state.latest_result)
        show_downloads(st.session_state.latest_result)

elif page == "Text Analysis":
    page_intro("CONTENT INVESTIGATION", "Analyze a news claim", "Paste a headline, article, or social-media claim to receive an explainable AI assessment.", "📰")
    samples = {
        "Medical claim": "Scientists have discovered a medicine that can cure every disease in just one day.",
        "Government claim": "The government announced a major new policy today. Please verify this claim with official sources.",
        "Social media claim": "A social media post claims that a famous company has announced free products for everyone without any official source.",
    }
    with st.container(border=True):
        sample = st.selectbox("Try a sample claim (optional)", ["Choose a sample"] + list(samples))
        text_input = st.text_area("News article or claim", value=samples.get(sample, ""), max_chars=MAX_TEXT_CHARS, height=210, placeholder="Paste the full text or claim here...")
        st.caption(f"{len(text_input)} / {MAX_TEXT_CHARS} characters")
        if st.button("✦ Analyze news text", type="primary", use_container_width=True):
            if not text_input.strip():
                st.warning("Please enter a news article or claim.")
            else:
                try:
                    with st.spinner("Examining the claim and preparing an explanation..."):
                        payload = call_text_api(text_input.strip())
                    save_result(payload["result"], "text", text_input.strip(), payload)
                    st.success("Text assessment completed.")
                except (requests.RequestException, RuntimeError) as exc:
                    st.error(f"Text analysis failed: {exc}")
    display_latest("text")

elif page == "Image Analysis":
    page_intro("VISUAL INVESTIGATION", "Analyze a news image", "Upload a photograph, screenshot, poster, or other visual used to support a news claim.", "🖼️")
    with st.container(border=True):
        image_file = st.file_uploader("Choose an image", type=IMAGE_TYPES, key="single_image", help="JPG, JPEG, PNG, or WEBP · Maximum 10 MB")
        if image_file:
            st.image(image_file, caption=image_file.name, use_container_width=True)
            if image_file.size > MAX_IMAGE_BYTES:
                st.error("Image must be smaller than 10 MB.")
        context = st.text_area("Context or related claim (optional)", max_chars=MAX_CONTEXT_CHARS, height=110, placeholder="Where was this image shared? What claim is being made?")
        if st.button("✦ Analyze image", type="primary", use_container_width=True):
            if image_file is None:
                st.warning("Please upload an image.")
            elif image_file.size > MAX_IMAGE_BYTES:
                st.error("Image must be smaller than 10 MB.")
            else:
                try:
                    with st.spinner("Inspecting the image and analyzing its context..."):
                        payload = call_file_api("/analyze-image", image_file, context.strip())
                    save_result(payload["result"], "image", context.strip() or f"Image analysis: {image_file.name}", payload)
                    st.success("Image assessment completed.")
                except (requests.RequestException, RuntimeError) as exc:
                    st.error(f"Image analysis failed: {exc}")
    display_latest("image")

elif page == "Video Analysis":
    page_intro("VIDEO INVESTIGATION", "Analyze a news video", "Upload a video clip and add context to assess the content and credibility signals.", "🎬")
    with st.container(border=True):
        video_file = st.file_uploader("Choose a video", type=VIDEO_TYPES, key="single_video", help="MP4, WEBM, MOV, or AVI · Maximum 50 MB")
        if video_file:
            st.video(video_file)
            st.caption(f"{video_file.name} · {video_file.size / (1024*1024):.2f} MB")
            if video_file.size > MAX_VIDEO_BYTES:
                st.error("Video must be 50 MB or smaller.")
        context = st.text_area("Context or related claim (optional)", max_chars=MAX_CONTEXT_CHARS, height=110, placeholder="Add the headline, source, date, or claim associated with this video...")
        if st.button("✦ Analyze video", type="primary", use_container_width=True):
            if video_file is None:
                st.warning("Please upload a video.")
            elif video_file.size > MAX_VIDEO_BYTES:
                st.error("Video must be 50 MB or smaller.")
            else:
                try:
                    with st.spinner("Analyzing video content. This may take a little while..."):
                        payload = call_file_api("/analyze-video", video_file, context.strip())
                    save_result(payload["result"], "video", context.strip() or f"Video analysis: {video_file.name}", payload)
                    st.success("Video assessment completed.")
                except (requests.RequestException, RuntimeError) as exc:
                    st.error(f"Video analysis failed: {exc}")
    display_latest("video")

elif page == "Multimodal Analysis":
    page_intro("CROSS-MODAL INVESTIGATION", "Connect the evidence", "Submit related text, images, and videos together to explore consistency and contradictions across formats.", "🔗")
    with st.container(border=True):
        mm_text = st.text_area("📰 News text or claim", max_chars=MAX_TEXT_CHARS, height=150, placeholder="Enter the claim or article connected to the media...")
        left, right = st.columns(2)
        with left:
            mm_image = st.file_uploader("🖼️ Add an image (optional)", type=IMAGE_TYPES, key="multi_image")
            if mm_image:
                st.image(mm_image, use_container_width=True)
                if mm_image.size > MAX_IMAGE_BYTES:
                    st.error("Image must be smaller than 10 MB.")
        with right:
            mm_video = st.file_uploader("🎬 Add a video (optional)", type=VIDEO_TYPES, key="multi_video")
            if mm_video:
                st.video(mm_video)
                if mm_video.size > MAX_VIDEO_BYTES:
                    st.error("Video must be 50 MB or smaller.")
        st.info("Provide at least one input. Adding multiple formats allows the model to assess cross-modal consistency.")
        if st.button("✦ Run multimodal analysis", type="primary", use_container_width=True):
            if not mm_text.strip() and mm_image is None and mm_video is None:
                st.warning("Please provide text, an image, or a video.")
            elif mm_image is not None and mm_image.size > MAX_IMAGE_BYTES:
                st.error("Image must be smaller than 10 MB.")
            elif mm_video is not None and mm_video.size > MAX_VIDEO_BYTES:
                st.error("Video must be 50 MB or smaller.")
            else:
                try:
                    with st.spinner("Comparing the submitted modalities and generating insights..."):
                        payload = call_multimodal_api(mm_text.strip(), mm_image, mm_video)
                    meta = {"modalities": [n for n, present in [("text", bool(mm_text.strip())), ("image", mm_image is not None), ("video", mm_video is not None)] if present], "image_name": mm_image.name if mm_image else None, "video_name": mm_video.name if mm_video else None}
                    save_result(payload["result"], "multimodal", mm_text.strip() or "Multimodal news analysis", payload)
                    st.session_state.latest_result["multimodal_meta"] = meta
                    st.success("Multimodal assessment completed.")
                except (requests.RequestException, RuntimeError) as exc:
                    st.error(f"Multimodal analysis failed: {exc}")
    display_latest("multimodal")

elif page == "Analysis History":
    page_intro("YOUR RECENT WORK", "Analysis history", "Review assessments created during this Streamlit session.", "🗂️")
    if st.session_state.history:
        if st.button("🗑️ Clear session history"):
            st.session_state.history = []
            st.session_state.latest_result = None
            st.rerun()
        for idx, item in enumerate(st.session_state.history):
            title = f"{item.get('content_type','analysis').title()}  ·  {item.get('classification','Uncertain')}  ·  Trust {item.get('trust_score',0)}/100"
            with st.expander(title):
                st.caption(item.get("analyzed_at", ""))
                if item.get("news_text"):
                    st.write(item["news_text"])
                render_result(item, item.get("multimodal_meta"))
                show_downloads(item)
                if st.button("Set as latest result", key=f"history_select_{idx}"):
                    st.session_state.latest_result = item
                    st.success("Selected as the latest result. Open Overview to view it.")
    else:
        st.markdown('<div class="surface" style="text-align:center;padding:2.5rem"><div style="font-size:2.3rem">🗂️</div><h3 style="color:#243858">Your history is empty</h3><p class="small-muted">Run an analysis and your recent results will appear here.</p></div>', unsafe_allow_html=True)

elif page == "About Project":
    page_intro("PROJECT INFORMATION", "About TrustLens AI", "A multi-modal explainable framework for assessing the credibility of news content.", "ℹ️")
    st.markdown('<div class="surface"><h3 style="color:#1d355b">What is TrustLens AI?</h3><p class="small-muted">TrustLens AI is an MCA research project that explores AI-assisted credibility assessment across text, images, and videos. It presents a classification, confidence estimate, trust score, explanation, key concerns, and recommendation to help users examine suspicious content.</p></div>', unsafe_allow_html=True)
    st.markdown("### Technology stack")
    tech = st.columns(4)
    for col, icon, name, desc in zip(tech, ["🐍", "⚡", "✨", "🔌"], ["Python", "FastAPI", "Gemini API", "Streamlit"], ["Core application logic", "Backend REST services", "AI-powered assessment", "Interactive user interface"]):
        with col:
            st.markdown(f'<div class="info-tile"><div style="font-size:1.5rem">{icon}</div><h4>{name}</h4><p>{desc}</p></div>', unsafe_allow_html=True)
    st.markdown("### Responsible use")
    st.warning("AI-generated classifications and trust scores are indicative assessments, not guaranteed factual verification or proof that media is authentic or manipulated. Models can make mistakes. Verify important claims using reliable primary sources and independent evidence.")

st.markdown('<div class="footer">TRUSTLENS AI · MULTI-MODAL NEWS CREDIBILITY ASSESSMENT · MCA RESEARCH PROJECT</div>', unsafe_allow_html=True)
