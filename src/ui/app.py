"""
Voicebook - Text-to-Speech Audiobook Generator
Main Streamlit application
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.openai_tts import OpenAITTS
from cache.audio_cache import AudioCache
from processors.document_parser import DocumentParser
from processors.text_cleaner import TextCleaner
from utils.cost_calculator import CostCalculator, get_cost_warning_message
from utils.validators import FileValidator, TextValidator, APIKeyValidator

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Voicebook - TTS Audiobook Generator",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .cost-display {
        font-size: 1.5rem;
        font-weight: bold;
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'generated_audio' not in st.session_state:
        st.session_state.generated_audio = None
    if 'extracted_text' not in st.session_state:
        st.session_state.extracted_text = None
    if 'last_cost' not in st.session_state:
        st.session_state.last_cost = 0
    if 'cache_used' not in st.session_state:
        st.session_state.cache_used = False


def validate_api_key():
    """Validate OpenAI API key."""
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        st.error("❌ OpenAI API key not found!")
        st.markdown("""
        ### How to set up your API key:

        1. Create a `.env` file in the project root
        2. Add your API key: `OPENAI_API_KEY=sk-your-key-here`
        3. Restart the application

        Get your API key from: https://platform.openai.com/api-keys
        """)
        return False

    is_valid, error = APIKeyValidator.validate_openai_key(api_key)
    if not is_valid:
        st.error(f"❌ Invalid API key: {error}")
        return False

    return True


def render_sidebar():
    """Render sidebar with settings and info."""
    with st.sidebar:
        st.markdown("### ⚙️ Settings")

        # Voice selection
        voice = st.selectbox(
            "Voice",
            options=OpenAITTS.VOICES,
            index=OpenAITTS.VOICES.index(os.getenv("DEFAULT_VOICE", "nova")),
            help="Select the voice for audio generation"
        )

        # Show voice description
        st.caption(OpenAITTS.get_voice_description(voice))

        # Speed control
        speed = st.slider(
            "Speed",
            min_value=0.25,
            max_value=4.0,
            value=float(os.getenv("DEFAULT_SPEED", "1.0")),
            step=0.25,
            help="Playback speed (1.0 = normal)"
        )

        # Quality selection
        quality = st.radio(
            "Quality",
            options=["standard", "hd"],
            index=0 if os.getenv("DEFAULT_QUALITY", "standard") == "standard" else 1,
            help="Standard: $15/1M chars | HD: $30/1M chars (2x cost)"
        )

        st.markdown("---")

        # Cache management
        st.markdown("### 💾 Cache")
        cache = AudioCache()
        stats = cache.get_stats()

        st.metric("Cached Files", stats["total_files"])
        st.metric("Cache Size", f"{stats['total_size_mb']} MB")
        st.metric("Cache Hits", stats["cache_hits"])

        if st.button("Clear Cache", type="secondary"):
            deleted = cache.clear()
            st.success(f"Deleted {deleted} cached files")
            st.rerun()

        st.markdown("---")

        # Pricing info
        st.markdown("### 💰 Pricing")
        st.caption("**Standard (tts-1):** $15.00 per 1M characters")
        st.caption("**HD (tts-1-hd):** $30.00 per 1M characters")

        chars_per_dollar = CostCalculator.characters_per_dollar(quality)
        st.caption(f"≈ {chars_per_dollar:,} characters per $1")

        return voice, speed, quality


def process_uploaded_file(uploaded_file):
    """Process uploaded file and extract text."""
    if uploaded_file is None:
        return None, "No file uploaded"

    # Validate file
    is_valid = FileValidator.validate_extension(uploaded_file.name)
    if not is_valid:
        return None, f"Unsupported file type. Supported: .txt, .pdf, .docx"

    # Save temporary file
    temp_dir = Path("uploads")
    temp_dir.mkdir(exist_ok=True)

    temp_path = temp_dir / uploaded_file.name

    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Parse document
    text, error = DocumentParser.parse_file(str(temp_path))

    # Clean up temp file
    try:
        temp_path.unlink()
    except:
        pass

    if error:
        return None, error

    # Clean text
    text = TextCleaner.clean_document_text(text)

    return text, None


def generate_audio(text, voice, speed, quality):
    """Generate audio from text with caching."""
    try:
        # Initialize cache
        cache = AudioCache()

        # Generate cache key
        cache_key = cache.generate_cache_key(text, voice, speed, quality)

        # Check cache
        cached_path = cache.get(cache_key)

        if cached_path:
            st.session_state.cache_used = True
            st.session_state.last_cost = 0
            return cached_path, None

        # Generate new audio
        with st.spinner("🎙️ Generating audio..."):
            tts = OpenAITTS()
            audio_data = tts.generate_speech(text, voice, speed, quality)

            # Calculate cost
            cost = CostCalculator.estimate_cost(text, quality)
            st.session_state.last_cost = cost
            st.session_state.cache_used = False

            # Cache the audio
            cache_metadata = {
                "voice": voice,
                "speed": speed,
                "quality": quality,
                "char_count": len(text),
                "cost": cost
            }

            cached_path = cache.put(cache_key, audio_data, cache_metadata)

            return cached_path, None

    except Exception as e:
        return None, str(e)


def render_main_content():
    """Render main content area."""
    # Header
    st.markdown('<div class="main-header">📖 Voicebook</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Transform documents into audiobooks</div>', unsafe_allow_html=True)

    # Get settings from sidebar
    voice, speed, quality = render_sidebar()

    # Input method selection
    input_method = st.radio(
        "Input Method",
        options=["Upload Document", "Paste Text"],
        horizontal=True
    )

    text = None

    if input_method == "Upload Document":
        # File upload
        uploaded_file = st.file_uploader(
            "Choose a document",
            type=["txt", "pdf", "docx"],
            help="Upload a TXT, PDF, or DOCX file"
        )

        if uploaded_file:
            with st.spinner("📄 Extracting text..."):
                text, error = process_uploaded_file(uploaded_file)

                if error:
                    st.error(f"❌ Error: {error}")
                    return
                else:
                    st.success(f"✅ Extracted {len(text):,} characters from {uploaded_file.name}")
                    st.session_state.extracted_text = text

    else:
        # Text input
        text = st.text_area(
            "Paste your text here",
            height=300,
            placeholder="Enter or paste the text you want to convert to speech..."
        )

        if text:
            st.session_state.extracted_text = text

    # Display text preview and statistics
    if st.session_state.extracted_text:
        text = st.session_state.extracted_text

        # Text statistics
        stats = TextCleaner.get_text_stats(text)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Characters", f"{stats['characters']:,}")
        with col2:
            st.metric("Words", f"{stats['words']:,}")
        with col3:
            st.metric("Sentences", stats['sentences'])
        with col4:
            st.metric("Paragraphs", stats['paragraphs'])

        # Validate text
        is_valid, validation_msg = TextValidator.validate_text(text)

        if not is_valid:
            st.error(f"❌ {validation_msg}")
            return

        if validation_msg:
            st.warning(validation_msg)

        # Cost estimation
        estimated_cost = CostCalculator.estimate_cost(text, quality)

        st.markdown("---")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### 💰 Cost Estimate")
            st.markdown(f'<div class="cost-display">{CostCalculator.format_cost(estimated_cost)}</div>', unsafe_allow_html=True)

            # Check cache
            cache = AudioCache()
            cache_key = cache.generate_cache_key(text, voice, speed, quality)

            if cache.exists(cache_key):
                st.markdown('<div class="success-box">✅ This exact audio is already cached - generation will be FREE!</div>', unsafe_allow_html=True)

            # Cost warning
            warning = get_cost_warning_message(estimated_cost, float(os.getenv("WARN_COST_THRESHOLD", "2.00")))
            if warning:
                st.markdown(f'<div class="warning-box">{warning}</div>', unsafe_allow_html=True)

        with col2:
            st.markdown("### 🎬 Actions")

            # Generate button with confirmation for high cost
            if estimated_cost >= float(os.getenv("WARN_COST_THRESHOLD", "2.00")) and not cache.exists(cache_key):
                st.warning("⚠️ High cost - confirm below")
                confirm = st.checkbox("I understand the cost")

                if st.button("🎙️ Generate Audio", type="primary", disabled=not confirm):
                    audio_path, error = generate_audio(text, voice, speed, quality)

                    if error:
                        st.error(f"❌ Error: {error}")
                    else:
                        st.session_state.generated_audio = audio_path
                        st.rerun()
            else:
                if st.button("🎙️ Generate Audio", type="primary"):
                    audio_path, error = generate_audio(text, voice, speed, quality)

                    if error:
                        st.error(f"❌ Error: {error}")
                    else:
                        st.session_state.generated_audio = audio_path
                        st.rerun()

        # Text preview
        with st.expander("📖 Preview Text", expanded=False):
            preview = TextCleaner.preview_text(text, 1000)
            st.text_area("Text Preview", preview, height=200, disabled=True)

    # Display generated audio
    if st.session_state.generated_audio:
        st.markdown("---")
        st.markdown("### 🎵 Generated Audio")

        audio_path = st.session_state.generated_audio

        # Display cost info
        if st.session_state.cache_used:
            st.markdown('<div class="success-box">✅ Used cached audio - Cost: $0.00</div>', unsafe_allow_html=True)
        else:
            cost_display = CostCalculator.format_cost(st.session_state.last_cost)
            st.markdown(f'<div class="success-box">✅ Audio generated - Cost: {cost_display}</div>', unsafe_allow_html=True)

        # Audio player
        with open(audio_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format="audio/mp3")

        # Download button
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"voicebook_{voice}_{timestamp}.mp3"

        st.download_button(
            label="⬇️ Download Audio",
            data=audio_bytes,
            file_name=filename,
            mime="audio/mp3"
        )


def main():
    """Main application entry point."""
    initialize_session_state()

    # Validate API key
    if not validate_api_key():
        st.stop()

    # Render main content
    render_main_content()

    # Footer
    st.markdown("---")
    st.caption("Built with Streamlit & OpenAI TTS | Optimized for cost-effective audiobook generation")


if __name__ == "__main__":
    main()
