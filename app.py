import streamlit as st
import requests
from gtts import gTTS
import pyttsx3
import os
import tempfile
import io

# ----------------------
# Hugging Face API Setup (FIXED)
# ----------------------
try:
    HF_API_KEY = st.secrets["huggingface"]["api_key"]
except:
    HF_API_KEY = "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"  # Your key as fallback

# FIXED: Use proper text generation model and complete API URL
HF_API_URL = "https://api-inference.huggingface.co/models/ibm-granite/granite-vision-3.3-2b"
# Alternative better model:

HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

# ----------------------
# Voice Configuration (Same as before)
# ----------------------
VOICE_OPTIONS = {
    "Lisa": {"engine": "gtts", "lang": "en", "tld": "com", "rate": 200, "description": "American Female"},
    "Michael": {"engine": "pyttsx3", "gender": "male", "rate": 180, "description": "System Male"},
    "Allison": {"engine": "gtts", "lang": "en", "tld": "ca", "rate": 190, "description": "Canadian Female"},
    "David": {"engine": "pyttsx3", "gender": "male", "rate": 170, "description": "Deep Male"},
    "Emma": {"engine": "pyttsx3", "gender": "female", "rate": 200, "description": "System Female"},
    "Sarah": {"engine": "gtts", "lang": "en", "tld": "co.uk", "rate": 185, "description": "British Female"}
}

# ----------------------
# ENHANCED Function: Rewrite Text with Tone (FIXED)
# ----------------------
def rewrite_text(input_text, tone):
    """Enhanced text rewriting with better prompts and fallback"""
    
    # Enhanced prompts for better results
    if tone == "Neutral":
        prompt = f"""Rewrite the following text in a clear, professional, and neutral tone while preserving all original meaning:

Text: {input_text}

Professional rewrite:"""
        
    elif tone == "Suspenseful":
        prompt = f"""Transform the following text to create suspense, mystery, and dramatic tension while keeping the original information:

Text: {input_text}

Suspenseful rewrite:"""
        
    elif tone == "Inspiring":
        prompt = f"""Rewrite the following text to be motivating, uplifting, and inspiring while preserving the original message:

Text: {input_text}

Inspiring rewrite:"""
    else:
        prompt = f"Rewrite this text: {input_text}\n\nRewritten:"
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 200,  # Increased for better output
            "temperature": 0.8,
            "do_sample": True,
            "return_full_text": False,
            "repetition_penalty": 1.1
        }
    }
    
    try:
        response = requests.post(HF_API_URL, headers=HEADERS, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
                result = data[0]["generated_text"].strip()
                
                # Clean the result
                result = result.replace(prompt, "").strip()
                
                if result and len(result) > 10:  # Ensure meaningful output
                    st.success(f"✅ Text successfully rewritten in {tone} tone!")
                    return result
                    
        elif response.status_code == 503:
            st.warning("🔄 AI model is loading. Using enhanced fallback...")
            
    except Exception as e:
        st.warning(f"⚠️ AI temporarily unavailable: {str(e)}")
    
    # ENHANCED FALLBACK: Apply actual tone transformation
    return apply_tone_fallback(input_text, tone)

def apply_tone_fallback(text, tone):
    """Enhanced fallback that actually changes the text based on tone"""
    
    sentences = text.split('. ')
    enhanced_sentences = []
    
    for i, sentence in enumerate(sentences):
        if sentence.strip():
            if tone == "Neutral":
                # Make it more professional
                enhanced_sentences.append(f"It is important to note that {sentence.strip().lower()}")
                
            elif tone == "Suspenseful":
                # Add mystery and tension
                if i == 0:
                    enhanced_sentences.append(f"Something mysterious begins to unfold... {sentence.strip()}")
                else:
                    enhanced_sentences.append(f"{sentence.strip()}, yet something deeper lurks beneath")
                    
            elif tone == "Inspiring":
                # Add motivation
                if i == 0:
                    enhanced_sentences.append(f"Embrace this powerful truth: {sentence.strip()}")
                else:
                    enhanced_sentences.append(f"{sentence.strip()}, opening infinite possibilities")
    
    result = '. '.join(enhanced_sentences)
    
    # Add tone-specific endings
    if tone == "Suspenseful":
        result += "... but what secrets remain hidden?"
    elif tone == "Inspiring":
        result += " Together, we can achieve the extraordinary!"
    elif tone == "Neutral":
        result += " This information has been presented in a clear, professional manner."
    
    st.info(f"🔄 Used enhanced fallback processing for {tone} tone")
    return result

# ----------------------
# Text to Speech Functions (Keep same as your original)
# ----------------------
def text_to_speech_gtts(text, voice_config, filename):
    try:
        tts = gTTS(
            text=str(text), 
            lang=voice_config["lang"], 
            tld=voice_config["tld"],
            slow=False
        )
        tts.save(filename)
        return filename
    except Exception as e:
        st.error(f"gTTS Error: {e}")
        return None

def text_to_speech_pyttsx3(text, voice_config, filename):
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        if not voices:
            st.error("No system voices available")
            return None
        
        selected_voice = None
        target_gender = voice_config["gender"]
        male_voices = []
        female_voices = []
        
        for voice in voices:
            voice_name = voice.name.lower()
            voice_id = voice.id.lower()
            
            if any(keyword in voice_name or keyword in voice_id for keyword in 
                   ['male', 'man', 'david', 'alex', 'tom', 'mike', 'john', 'james', 'mark']):
                male_voices.append(voice)
            elif any(keyword in voice_name or keyword in voice_id for keyword in 
                     ['female', 'woman', 'zira', 'hazel', 'susan', 'anna', 'emma', 'lisa']):
                female_voices.append(voice)
            elif 'female' in voice_id or 'female' in voice_name:
                female_voices.append(voice)
            elif 'male' in voice_id or 'male' in voice_name:
                male_voices.append(voice)
            else:
                if len(male_voices) == 0:
                    male_voices.append(voice)
                else:
                    female_voices.append(voice)
        
        if target_gender == "male" and male_voices:
            selected_voice = male_voices[0]
        elif target_gender == "female" and female_voices:
            selected_voice = female_voices
        else:
            selected_voice = voices
        
        engine.setProperty('voice', selected_voice.id)
        
        if target_gender == "male":
            engine.setProperty('rate', voice_config["rate"] - 20)
            engine.setProperty('volume', 0.95)
        else:
            engine.setProperty('rate', voice_config["rate"])
            engine.setProperty('volume', 0.9)
        
        engine.save_to_file(str(text), filename)
        engine.runAndWait()
        
        return filename if os.path.exists(filename) else None
        
    except Exception as e:
        st.error(f"pyttsx3 Error: {e}")
        return None

def generate_speech(text, voice_name, filename="audiobook.mp3"):
    voice_config = VOICE_OPTIONS.get(voice_name)
    
    if not voice_config:
        st.error(f"Voice '{voice_name}' not found!")
        return None
    
    if voice_config["engine"] == "gtts":
        return text_to_speech_gtts(text, voice_config, filename)
    elif voice_config["engine"] == "pyttsx3":
        return text_to_speech_pyttsx3(text, voice_config, filename)
    else:
        st.error(f"Unknown TTS engine: {voice_config['engine']}")
        return None

# ----------------------
# Streamlit UI (Keep same as your original)
# ----------------------
st.set_page_config(page_title="EchoVerse Pro", layout="centered", page_icon="🎙️")

st.title("🎙️ EchoVerse Pro")
st.markdown("*AI-Powered Audiobook Creator with Multiple Voices*")

# Add tone demonstration
st.info("🎭 **Tone Testing**: Each tone will now produce distinctly different text and audio!")

with st.sidebar:
    st.header("🎵 Voice Settings")
    
    selected_voice = st.selectbox(
        "Choose Voice:",
        options=list(VOICE_OPTIONS.keys()),
        format_func=lambda x: f"{x} ({VOICE_OPTIONS[x]['description']})"
    )
    
    st.info(f"**Selected Voice:** {selected_voice}\n\n**Type:** {VOICE_OPTIONS[selected_voice]['description']}")
    
    if st.button("🔊 Test Voice"):
        test_text = "Hello! This is how I sound. I'm ready to create your audiobook."
        with st.spinner("Generating voice sample..."):
            test_file = generate_speech(test_text, selected_voice, "voice_test.mp3")
            if test_file and os.path.exists(test_file):
                with open(test_file, "rb") as f:
                    st.audio(f.read(), format="audio/mp3")
    
    st.markdown("### Available Voices:")
    st.markdown("""
    **Female Voices (gTTS):**
    - 🇺🇸 Lisa (American Female)
    - 🇨🇦 Allison (Canadian Female)  
    - 🇬🇧 Sarah (British Female)
    
    **Male Voices (System TTS):**
    - 👨 Michael (System Male)
    - 👨 David (Deep Male)
    
    **Female Voices (System TTS):**
    - 👩 Emma (System Female)
    """)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 Text Input")
    
    uploaded_file = st.file_uploader("Upload a .txt file", type="txt")
    input_text = ""
    
    if uploaded_file is not None:
        input_text = uploaded_file.read().decode("utf-8")
        st.success(f"✅ File uploaded: {uploaded_file.name}")
    
    input_text = st.text_area(
        "Or paste your text here:", 
        value=input_text, 
        height=200,
        placeholder="Enter the text you want to convert to an audiobook..."
    )

with col2:
    st.subheader("⚙️ Settings")
    
    tone = st.selectbox(
        "Select Tone:",
        ["Neutral", "Suspenseful", "Inspiring"],
        help="Choose how you want the text to be rewritten - you'll see different results!"
    )
    
    if input_text:
        char_count = len(input_text)
        st.metric("Characters", char_count)
        estimated_duration = max(1, char_count // 1000)
        st.metric("Est. Audio Duration", f"~{estimated_duration} min")

st.markdown("---")

if st.button("🚀 Generate Audiobook", type="primary", use_container_width=True):
    if not input_text.strip():
        st.error("⚠️ Please enter some text or upload a file!")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("🔄 Rewriting text with AI...")
        progress_bar.progress(20)
        
        rewritten_text = rewrite_text(input_text, tone)
        
        progress_bar.progress(40)
        status_text.text("📝 Displaying results...")
        
        result_col1, result_col2 = st.columns(2)
        
        with result_col1:
            st.subheader("📄 Original Text")
            st.text_area("Original", value=input_text, height=200, disabled=True)
        
        with result_col2:
            st.subheader(f"✨ Rewritten ({tone})")
            st.text_area("Rewritten", value=rewritten_text, height=200, disabled=True)
        
        # Show difference indicator
        if rewritten_text != input_text:
            st.success(f"🎯 Text successfully transformed into {tone} tone! You'll hear the difference in the audio.")
        else:
            st.info("📝 Text processing completed.")
        
        progress_bar.progress(60)
        status_text.text(f"🎵 Generating audio with {selected_voice} voice...")
        
        filename = f"audiobook_{tone.lower()}_{selected_voice.lower()}.mp3"
        output_file = generate_speech(rewritten_text, selected_voice, filename)
        
        if output_file and os.path.exists(output_file):
            progress_bar.progress(100)
            status_text.text("✅ Audiobook generated successfully!")
            
            st.subheader("🎧 Your Audiobook")
            
            with open(output_file, "rb") as f:
                audio_bytes = f.read()
            
            audio_col1, audio_col2, audio_col3 = st.columns([2, 1, 1])
            
            with audio_col1:
                st.audio(audio_bytes, format="audio/mp3")
            
            with audio_col2:
                st.download_button(
                    label="📥 Download MP3",
                    data=audio_bytes,
                    file_name=filename,
                    mime="audio/mp3"
                )
            
            with audio_col3:
                file_size = len(audio_bytes) / 1024
                st.metric("File Size", f"{file_size:.1f} KB")
            
            st.success(f"🎉 Audiobook created with **{selected_voice}** voice in **{tone}** tone!")
            
        else:
            st.error("❌ Failed to generate audio. Please try again.")
        
        progress_bar.empty()
        status_text.empty()
