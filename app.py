import streamlit as st
import requests
from gtts import gTTS
import pyttsx3
import os
import tempfile
import io

# ----------------------
# Hugging Face API Setup
# ----------------------
HF_API_KEY = "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"
HF_API_URL = "https://api-inference.huggingface.co/models/gpt2"
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

# ----------------------
# Voice Configuration (CORRECTED FOR ACTUAL GENDER DIFFERENCES)
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
# Function: Rewrite Text with Tone (NO PREFIXES)
# ----------------------
def rewrite_text(input_text, tone):
    if tone == "Neutral":
        prompt = f"Rewrite this text in a clear, professional way: {input_text}\n\nClear version:"
    elif tone == "Suspenseful":
        prompt = f"Rewrite this text to build suspense and mystery: {input_text}\n\nSuspenseful version:"
    elif tone == "Inspiring":
        prompt = f"Rewrite this text to be motivating and uplifting: {input_text}\n\nInspiring version:"
    else:
        prompt = f"Rewrite this text: {input_text}\n\nRewritten:"
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 150,
            "temperature": 0.8,
            "do_sample": True,
            "return_full_text": False
        }
    }
    
    try:
        response = requests.post(HF_API_URL, headers=HEADERS, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
                result = data["generated_text"].strip()
                if result:
                    return result
        
        # Fallback: Return original text WITHOUT any prefixes
        return input_text
        
    except Exception as e:
        # Fallback: Return original text WITHOUT any prefixes
        return input_text

# ----------------------
# Function: Text to Speech with ACTUAL Gender Differences
# ----------------------
def text_to_speech_gtts(text, voice_config, filename):
    """Generate speech using Google TTS (Female voices only)"""
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
    """Generate speech using system TTS with proper male/female selection"""
    try:
        engine = pyttsx3.init()
        
        # Get available voices
        voices = engine.getProperty('voices')
        
        if not voices:
            st.error("No system voices available")
            return None
        
        # Find the best matching voice based on gender
        selected_voice = None
        target_gender = voice_config["gender"]
        
        # Search for voices by gender
        male_voices = []
        female_voices = []
        
        for voice in voices:
            voice_name = voice.name.lower()
            voice_id = voice.id.lower()
            
            # Check for male indicators
            if any(keyword in voice_name or keyword in voice_id for keyword in 
                   ['male', 'man', 'david', 'alex', 'tom', 'mike', 'john', 'james', 'mark']):
                male_voices.append(voice)
            # Check for female indicators  
            elif any(keyword in voice_name or keyword in voice_id for keyword in 
                     ['female', 'woman', 'zira', 'hazel', 'susan', 'anna', 'emma', 'lisa']):
                female_voices.append(voice)
            # If voice contains 'female' or 'male' in ID/name
            elif 'female' in voice_id or 'female' in voice_name:
                female_voices.append(voice)
            elif 'male' in voice_id or 'male' in voice_name:
                male_voices.append(voice)
            else:
                # Default assignment based on common patterns
                # Typically, voice index 0 is male, 1 is female on Windows
                if len(male_voices) == 0:
                    male_voices.append(voice)
                else:
                    female_voices.append(voice)
        
        # Select voice based on requested gender
        if target_gender == "male" and male_voices:
            selected_voice = male_voices[0]
        elif target_gender == "female" and female_voices:
            selected_voice = female_voices[0]
        else:
            # Fallback to any available voice
            selected_voice = voices[0]
        
        # Set the selected voice
        engine.setProperty('voice', selected_voice.id)
        
        # Adjust speech properties based on gender
        if target_gender == "male":
            engine.setProperty('rate', voice_config["rate"] - 20)  # Slower for male
            engine.setProperty('volume', 0.95)
        else:
            engine.setProperty('rate', voice_config["rate"])  # Normal for female
            engine.setProperty('volume', 0.9)
        
        # Save to file
        engine.save_to_file(str(text), filename)
        engine.runAndWait()
        
        return filename if os.path.exists(filename) else None
        
    except Exception as e:
        st.error(f"pyttsx3 Error: {e}")
        return None

def generate_speech(text, voice_name, filename="audiobook.mp3"):
    """Main function to generate speech with selected voice"""
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
# Streamlit UI
# ----------------------
st.set_page_config(page_title="EchoVerse Pro", layout="centered", page_icon="🎙️")

# Header
st.title("🎙️ EchoVerse Pro")
st.markdown("*AI-Powered Audiobook Creator with Multiple Voices*")

# Sidebar for voice selection
with st.sidebar:
    st.header("🎵 Voice Settings")
    
    selected_voice = st.selectbox(
        "Choose Voice:",
        options=list(VOICE_OPTIONS.keys()),
        format_func=lambda x: f"{x} ({VOICE_OPTIONS[x]['description']})"
    )
    
    st.info(f"**Selected Voice:** {selected_voice}\n\n**Type:** {VOICE_OPTIONS[selected_voice]['description']}")
    
    # Voice preview
    if st.button("🔊 Test Voice"):
        test_text = "Hello! This is how I sound. I'm ready to create your audiobook."
        with st.spinner("Generating voice sample..."):
            test_file = generate_speech(test_text, selected_voice, "voice_test.mp3")
            if test_file and os.path.exists(test_file):
                with open(test_file, "rb") as f:
                    st.audio(f.read(), format="audio/mp3")
    
    # Voice info
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

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 Text Input")
    
    # File upload
    uploaded_file = st.file_uploader("Upload a .txt file", type="txt")
    input_text = ""
    
    if uploaded_file is not None:
        input_text = uploaded_file.read().decode("utf-8")
        st.success(f"✅ File uploaded: {uploaded_file.name}")
    
    # Text area (always visible)
    input_text = st.text_area(
        "Or paste your text here:", 
        value=input_text, 
        height=200,
        placeholder="Enter the text you want to convert to an audiobook..."
    )

with col2:
    st.subheader("⚙️ Settings")
    
    # Tone selection
    tone = st.selectbox(
        "Select Tone:",
        ["Neutral", "Suspenseful", "Inspiring"],
        help="Choose how you want the text to be rewritten"
    )
    
    # Character count
    if input_text:
        char_count = len(input_text)
        st.metric("Characters", char_count)
        
        # Estimate audio duration (roughly 1000 characters = 1 minute)
        estimated_duration = max(1, char_count // 1000)
        st.metric("Est. Audio Duration", f"~{estimated_duration} min")

# Generate button
st.markdown("---")

if st.button("🚀 Generate Audiobook", type="primary", use_container_width=True):
    if not input_text.strip():
        st.error("⚠️ Please enter some text or upload a file!")
    else:
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Rewrite text
        status_text.text("🔄 Rewriting text with AI...")
        progress_bar.progress(20)
        
        rewritten_text = rewrite_text(input_text, tone)
        
        # Step 2: Display results
        progress_bar.progress(40)
        status_text.text("📝 Displaying results...")
        
        # Results in columns
        result_col1, result_col2 = st.columns(2)
        
        with result_col1:
            st.subheader("📄 Original Text")
            st.text_area("Original", value=input_text, height=200, disabled=True)
        
        with result_col2:
            st.subheader(f"✨ Rewritten ({tone})")
            st.text_area("Rewritten", value=rewritten_text, height=200, disabled=True)
        
        # Step 3: Generate audio
        progress_bar.progress(60)
        status_text.text(f"🎵 Generating audio with {selected_voice} voice...")
        
        filename = f"audiobook_{tone.lower()}_{selected_voice.lower()}.mp3"
        output_file = generate_speech(rewritten_text, selected_voice, filename)
        
        if output_file and os.path.exists(output_file):
            progress_bar.progress(100)
            status_text.text("✅ Audiobook generated successfully!")
            
            # Audio player
            st.subheader("🎧 Your Audiobook")
            
            with open(output_file, "rb") as f:
                audio_bytes = f.read()
            
            # Audio controls
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
                file_size = len(audio_bytes) / 1024  # KB
                st.metric("File Size", f"{file_size:.1f} KB")
            
            # Success message
            st.success(f"🎉 Audiobook created with **{selected_voice}** voice in **{tone}** tone!")
            
        else:
            st.error("❌ Failed to generate audio. Please try again.")
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()