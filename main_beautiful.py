import streamlit as st
import google.generativeai as genai
import json
from datetime import datetime
import time
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================
# CONFIGURATION SECTION
# ============================================

class AppConfig:
    """Application configuration and settings"""
    
    # API Configuration - Load from environment variables
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    
    # Application Settings
    APP_TITLE = "Fake News Verifier"
    APP_SUBTITLE = "AI-Powered Fake News Detection • Advanced AI Technology"
    VERSION = "2.0"
    
    # UI Theme Colors
    COLORS = {
        # New theme colors (teal / dark slate) - feel free to change these
        'primary': '#0d9488',    # teal
        'secondary': '#0f172a',  # dark slate
        'success': '#16a34a',
        'warning': '#f59e0b',
        'danger': '#dc2626',
        'info': '#2563eb'
    }
    
    # Indian News Sources
    TRUSTED_SOURCES = [
        "📺 Times of India - https://timesofindia.indiatimes.com",
        "📺 NDTV - https://www.ndtv.com", 
        "📺 The Hindu - https://www.thehindu.com",
        "📺 Indian Express - https://indianexpress.com",
        "📺 India Today - https://www.indiatoday.in",
        "📺 Anandabazar Patrika - https://www.anandabazar.com",
        "📺 The Statesman - https://www.thestatesman.com",
        "📺 The Telegraph - https://www.telegraphindia.com",
        "📺 Alt News (Fact-checker) - https://www.altnews.in",
        "🔍 Boom Live (Fact-checker) - https://www.boomlive.in",
        "🔍 The Quint WebQoof - https://www.thequint.com/news/webqoof"
    ]

# ============================================
# CORE VERIFICATION ENGINE
# ============================================

class IndianNewsVerifier:
    """
    Advanced Indian News Verification Engine
    Uses Advanced AI for intelligent fact-checking with Indian context
    """
    
    def __init__(self):
        """Initialize the verification engine"""
        self.model = None
        self.is_ready = False
        self._setup_gemini_ai()
    
    def _setup_gemini_ai(self):
        """Private method to setup Advanced AI with error handling"""
        try:
            if not AppConfig.GEMINI_API_KEY:
                st.error("🚫 No API key found! Please add GEMINI_API_KEY to your .env file")
                st.info("💡 Create a .env file with: GEMINI_API_KEY=your_api_key_here")
                return
            
            # Configure AI API
            genai.configure(api_key=AppConfig.GEMINI_API_KEY)
            
            # Try multiple model versions for reliability
            model_options = [
                'gemini-2.5-flash',
                'gemini-flash-latest',
                'models/gemini-2.5-flash',
                'models/gemini-flash-latest'
            ]
            
            for model_name in model_options:
                try:
                    self.model = genai.GenerativeModel(model_name)
                    
                    # Test the model
                    test_response = self.model.generate_content("Test")
                    
                    if test_response and test_response.text:
                        self.is_ready = True
                        break
                        
                except Exception:
                    continue
            
            if not self.is_ready:
                st.error("❌ Could not initialize AI engine")
                
        except Exception as e:
            st.error(f"🚫 Setup Error: {str(e)}")
    
    def verify_news(self, news_claim):
        """
        Main verification method
        Returns comprehensive analysis of the news claim
        """
        if not self.is_ready:
            return self._create_error_response("AI engine not ready")
        
        try:
            # Create comprehensive analysis prompt
            analysis_prompt = self._create_analysis_prompt(news_claim)
            
            # Get AI response
            response = self.model.generate_content(analysis_prompt)
            
            if not response or not response.text:
                return self._create_error_response("No response from AI")
            
            # Parse and structure the response
            return self._parse_ai_response(response.text)
            
        except Exception as e:
            return self._create_error_response(f"Analysis failed: {str(e)}")
    
    def _create_analysis_prompt(self, news_claim):
        """Create a comprehensive prompt for Indian news analysis"""
        return f"""
        🇮🇳 INDIAN NEWS FACT-CHECK ANALYSIS
        =====================================
        
        You are an expert Indian news fact-checker with deep knowledge of:
        - Indian politics, government, and current affairs
        - Indian media landscape and reliable sources
        - Indian cultural and social context
        - Common misinformation patterns in India
        
        NEWS CLAIM TO ANALYZE:
        "{news_claim}"
        
        Please provide analysis in this EXACT format:
        
        VERIFICATION_STATUS: [TRUE/FALSE/PARTIALLY_TRUE/UNVERIFIED]
        CONFIDENCE_SCORE: [0-100]
        
        DETAILED_ANALYSIS:
        [Provide thorough explanation of why this claim is true/false]
        
        INDIAN_CONTEXT:
        [Explain relevance to Indian politics, society, current events]
        
        EVIDENCE_CHECK:
        [What evidence supports or contradicts this claim]
        
        RECOMMENDED_SOURCES:
        [List specific Indian news sources to verify this claim]
        
        RED_FLAGS:
        [Any warning signs or suspicious elements in this claim]
        
        CONCLUSION:
        [Final assessment with reasoning]
        """
    
    def _parse_ai_response(self, ai_text):
        """Parse AI response into structured format"""
        try:
            # Extract verification status
            status = "UNVERIFIED"
            confidence = 50
            
            # Look for status in AI response
            if "VERIFICATION_STATUS: TRUE" in ai_text:
                status = "TRUE"
                confidence = 85
            elif "VERIFICATION_STATUS: FALSE" in ai_text:
                status = "FALSE" 
                confidence = 90
            elif "VERIFICATION_STATUS: PARTIALLY_TRUE" in ai_text:
                status = "PARTIALLY_TRUE"
                confidence = 70
            elif "VERIFICATION_STATUS: UNVERIFIED" in ai_text:
                status = "UNVERIFIED"
                confidence = 30
            
            # Try to extract confidence score from AI response
            import re
            conf_match = re.search(r'CONFIDENCE_SCORE:\s*(\d+)', ai_text)
            if conf_match:
                extracted_confidence = int(conf_match.group(1))
                # Only use extracted confidence if it makes sense with the status
                if status == "UNVERIFIED" and extracted_confidence > 50:
                    confidence = min(extracted_confidence, 50)  # Cap at 50% for unverified
                elif status in ["TRUE", "FALSE", "PARTIALLY_TRUE"]:
                    confidence = extracted_confidence
            
            # Ensure logical confidence ranges
            if status == "UNVERIFIED" and confidence > 50:
                confidence = 30
            elif status == "TRUE" and confidence < 60:
                confidence = 75
            elif status == "FALSE" and confidence < 70:
                confidence = 80
            elif status == "PARTIALLY_TRUE" and confidence < 50:
                confidence = 65
            
            return {
                'status': status,
                'confidence': confidence,
                'analysis': ai_text,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'sources': AppConfig.TRUSTED_SOURCES[:4],  # Top 4 sources
                'success': True
            }
            
        except Exception as e:
            return self._create_error_response(f"Parse error: {str(e)}")
    
    def _create_error_response(self, error_message):
        """Create standardized error response"""
        return {
            'status': 'ERROR',
            'confidence': 0,
            'analysis': f"❌ {error_message}",
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'sources': [],
            'success': False
        }

# ============================================
# USER INTERFACE COMPONENTS
# ============================================

class BeautifulUI:
    """Beautiful and responsive user interface components"""
    
    @staticmethod
    def setup_page_config():
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="Fake News Detector",
            page_icon="🕵️‍♂️",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Apply light theme
        theme = BeautifulUI._get_light_theme()
        st.markdown(theme, unsafe_allow_html=True)
    
    @staticmethod
    def _get_light_theme():
        """Light theme - Warm Human-Made Theme"""
        return """
        <style>
        /* Import Google Fonts - Warm, friendly, human fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Lora:wght@400;500;600;700&family=Open+Sans:wght@400;500;600;700&display=swap');
        
        /* Hide Streamlit default elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {display:none;}
        div[data-testid="stToolbar"] {visibility: hidden;}
        .stActionButton {display:none;}
        
        /* MAIN BACKGROUND - Warm paper texture feel
           Soft cream background like quality paper
        */
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(180deg, 
                #f7f3e9 0%,      /* Warm cream */
                #faf8f3 50%,     /* Light paper white */
                #f5f1e8 100%     /* Soft beige */
            );
            background-attachment: fixed;
        }
        
        /* Soft container - organic feel */
        .main .block-container {
            background: rgba(255, 255, 255, 0.6) !important;
            border-radius: 15px !important;
            padding: 2rem !important;
            box-shadow: 0 2px 15px rgba(0, 0, 0, 0.08) !important;
        }
        
        /* TITLE - Warm, handwritten feel
           Human, approachable, trustworthy
        */
        h1 {
            color: #2c3e50 !important;
            font-family: 'Lora', 'Georgia', serif !important;
            font-weight: 700 !important;
            font-size: 2rem !important;
            text-align: center !important;
            letter-spacing: 0.5px !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Subheadings - Friendly section titles */
        h2 {
            color: #34495e !important;
            font-family: 'Inter', 'Open Sans', sans-serif !important;
            font-weight: 600 !important;
            font-size: 1.2rem !important;
        }
        
        h3 {
            color: #546e7a !important;
            font-family: 'Inter', 'Open Sans', sans-serif !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
        }
        
        /* Body Text - Natural, readable */
        p, div, label, span, li {
            color: #3d3d3d !important;
            font-family: 'Open Sans', 'Inter', sans-serif !important;
            font-weight: 400 !important;
            font-size: 0.85rem !important;
            line-height: 1.5 !important;
        }
        
        /* Strong/Bold text emphasis */
        strong {
            color: #2c3e50 !important;
            font-weight: 600 !important;
        }
        
        /* SIDEBAR - Warm wooden panel feel
           Natural, inviting, trustworthy
        */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, 
                #e8dcc5 0%,      /* Light wood */
                #f5ead6 100%     /* Cream wood */
            ) !important;
            border-right: 3px solid #d4a574 !important;
            box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1) !important;
        }
        
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: #5d4037 !important;
        }
        
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] div,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] li {
            color: #4a4a4a !important;
        }
        
        /* BUTTONS - Soft, inviting buttons
           Hand-crafted feel with soft shadows
        */
        .stButton > button {
            background: #7b93a7 !important;
            color: #FFFFFF !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 500 !important;
            font-size: 0.8rem !important;
            border: 2px solid #6b8299 !important;
            border-radius: 8px !important;
            padding: 0.55rem 1.2rem !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15) !important;
            transition: all 0.2s ease !important;
        }
        
        .stButton > button:hover {
            background: #6b8299 !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
        }
        
        .stButton > button[kind="primary"] {
            background: #81c784 !important;
            border-color: #6bb86f !important;
            box-shadow: 0 2px 8px rgba(129, 199, 132, 0.3) !important;
        }
        
        .stButton > button[kind="primary"]:hover {
            background: #6bb86f !important;
            box-shadow: 0 4px 12px rgba(129, 199, 132, 0.4) !important;
        }
        
        /* CARDS & CONTAINERS - Soft paper cards */
        div[data-testid="stVerticalBlock"] > div:not(:empty) {
            background: rgba(255, 255, 255, 0.8) !important;
            border: 2px solid #e0d5c1 !important;
            border-radius: 12px !important;
            padding: 1.5rem !important;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08) !important;
            position: relative !important;
            z-index: 1 !important;
        }
        
        /* Hide empty vertical blocks */
        div[data-testid="stVerticalBlock"]:empty {
            display: none !important;
        }
        
        div[data-testid="stVerticalBlock"] > div:empty {
            display: none !important;
        }
        
        /* TEXT INPUTS - Natural paper-like forms */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            background: #ffffff !important;
            color: #3d3d3d !important;
            font-family: 'Open Sans', sans-serif !important;
            border: 2px solid #d4c5a9 !important;
            border-radius: 8px !important;
            padding: 0.75rem !important;
            box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1) !important;
            pointer-events: auto !important;
            cursor: text !important;
        }
        
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: #7b93a7 !important;
            box-shadow: 0 0 0 3px rgba(123, 147, 167, 0.1) !important;
            outline: none !important;
        }
        
        .stTextInput > div > div > input::placeholder,
        .stTextArea > div > div > textarea::placeholder {
            color: #999 !important;
        }
        
        /* Ensure input containers are interactive */
        .stTextInput, .stTextArea {
            pointer-events: auto !important;
            z-index: 10 !important;
            position: relative !important;
        }
        
        .stTextInput > div, .stTextArea > div {
            pointer-events: auto !important;
        }
        
        /* RADIO BUTTONS */
        .stRadio > div {
            background: rgba(255, 255, 255, 0.7) !important;
            border-radius: 8px !important;
            padding: 1rem !important;
            border: 2px solid #e0d5c1 !important;
        }
        
        /* METRICS - Warm, human statistics */
        [data-testid="stMetricValue"] {
            color: #5d4037 !important;
            font-family: 'Lora', serif !important;
            font-weight: 600 !important;
            font-size: 1.3rem !important;
        }
        
        [data-testid="stMetricLabel"] {
            color: #6d6d6d !important;
            font-weight: 500 !important;
            font-size: 0.8rem !important;
        }
        
        /* EXPANDER - Soft collapsible sections */
        .streamlit-expanderHeader {
            background: rgba(224, 213, 193, 0.3) !important;
            border: 2px solid #d4c5a9 !important;
            border-radius: 8px !important;
            color: #4a4a4a !important;
            font-weight: 500 !important;
        }
        
        .streamlit-expanderHeader:hover {
            background: rgba(224, 213, 193, 0.5) !important;
        }
        
        /* DOWNLOAD BUTTON */
        .stDownloadButton > button {
            background: #d4a574 !important;
            border-color: #c89563 !important;
            box-shadow: 0 2px 8px rgba(212, 165, 116, 0.3) !important;
        }
        
        .stDownloadButton > button:hover {
            background: #c89563 !important;
            box-shadow: 0 4px 12px rgba(212, 165, 116, 0.4) !important;
        }
        
        /* SPINNER - Natural loading */
        .stSpinner > div {
            border-top-color: #7b93a7 !important;
        }
        
        /* ALERT BOXES - Warm, friendly messages */
        .stSuccess {
            background: rgba(129, 199, 132, 0.15) !important;
            border-left: 4px solid #81c784 !important;
            border-radius: 8px !important;
            color: #2d5016 !important;
        }
        
        .stWarning {
            background: rgba(255, 183, 77, 0.15) !important;
            border-left: 4px solid #ffb74d !important;
            border-radius: 8px !important;
            color: #6d4c00 !important;
        }
        
        .stError {
            background: rgba(229, 115, 115, 0.15) !important;
            border-left: 4px solid #e57373 !important;
            border-radius: 8px !important;
            color: #a31818 !important;
        }
        
        .stInfo {
            background: rgba(123, 147, 167, 0.15) !important;
            border-left: 4px solid #7b93a7 !important;
            border-radius: 8px !important;
            color: #2c3e50 !important;
        }
        
        /* HORIZONTAL RULE - Natural divider */
        hr {
            border: none !important;
            height: 1px !important;
            background: linear-gradient(90deg, 
                transparent, 
                rgba(212, 197, 169, 0.8), 
                transparent
            ) !important;
            margin: 2rem 0 !important;
        }
        
        /* SCROLLBAR - Wood-like styling */
        ::-webkit-scrollbar {
            width: 12px;
            height: 12px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(232, 220, 197, 0.5);
            border-radius: 6px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: rgba(212, 165, 116, 0.7);
            border-radius: 6px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(200, 149, 99, 0.9);
        }
        </style>
        """
    
    @staticmethod
    def render_header():
        """Render beautiful header section"""
        st.markdown("""
        <div style='text-align: center; padding: 1.5rem 0;'>
            <h1 style='color: #2c3e50; font-size: 2rem; margin-bottom: 0.5rem; font-family: Lora, Georgia, serif; font-weight: 700;'>
                🕵️‍♂️ Fake News Detector
            </h1>
            <p style='color: #5d4037; font-size: 0.9rem; margin-top: 0.5rem; font-family: Open Sans, sans-serif; font-weight: 500;'>
                AI-Powered Truth Engine • Made by Debasmita X Manisha X Joita
            </p>
            <hr style='width: 70%; margin: 1.5rem auto; border: none; height: 1px; background: linear-gradient(90deg, transparent, rgba(212, 197, 169, 0.8), transparent);'>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_sidebar():
        """Render enhanced sidebar with info"""
        with st.sidebar:
            st.markdown("""
            <div style='text-align: center; padding: 1rem 0;'>
                <h2 style='color: #5d4037;'>ℹ️ INFO PANEL</h2>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 🛠️ How It Works")
            st.markdown("""
            **1. INPUT** 📝  
            Enter news text or paste a URL
            
            **2. ANALYZE** 🤖  
            AI processes the claim using advanced algorithms
            
            **3. RESULTS** ✅  
            Get verification status with confidence score
            
            **4. CROSS-CHECK** 🔍  
            Review recommended sources
            """)
            
            st.markdown("---")
            
            st.markdown("### 📊 Status Guide")
            st.markdown("""
            🟢 **TRUE** - Verified as accurate  
            🔴 **FALSE** - Identified as fake  
            🟡 **PARTIAL** - Mixed accuracy  
            ⚪ **UNVERIFIED** - Needs more data
            """)
            
            st.markdown("---")
            
            st.markdown("### ⚠️ Important Note")
            st.markdown("""
            This AI tool provides analysis, but:
            - Always cross-reference with trusted sources
            - Check official news outlets
            - Look for multiple confirmations
            - Be skeptical of sensational claims
            """)
            
            st.markdown("---")
            
            st.markdown("### 📰 Trusted Sources")
            st.markdown("""
            - Times of India
            - NDTV
            - The Hindu
            - Indian Express
            - Alt News (Fact-checker)
            - Boom Live (Fact-checker)
            """)
            
            st.markdown("---")
            
            st.markdown(f"""
            <div style='text-align: center; padding: 1rem 0;'>
                <p style='color: #5d4037;'>
                    <strong>Version {AppConfig.VERSION}</strong> 🇮🇳
                </p>
                <p style='color: #6d6d6d; font-size: 0.9rem;'>
                    Powered by Advanced AI
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    @staticmethod
    def render_verification_form():
        """Render news input form"""
        st.markdown("### 📝 Enter News to Verify")
        
        # Input methods
        input_method = st.radio(
            "Choose input method:",
            ["✏️ Type/Paste Text", "🔗 News URL"],
            horizontal=True
        )
        
        news_text = ""
        
        if input_method == "✏️ Type/Paste Text":
            news_text = st.text_area(
                "Enter the news claim:",
                height=150,
                placeholder="Example: PM Modi announced new education policy today...",
                help="Paste the news text you want to verify"
            )
        else:
            url = st.text_input(
                "Enter news article URL:",
                placeholder="https://example.com/news-article"
            )
            if url:
                # Extract text from URL
                try:
                    import requests
                    from bs4 import BeautifulSoup
                    
                    with st.spinner("� Extracting text from URL..."):
                        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Remove script and style elements
                        for script in soup(["script", "style"]):
                            script.decompose()
                        
                        # Extract text from paragraphs
                        paragraphs = soup.find_all('p')
                        extracted_text = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                        
                        if extracted_text:
                            news_text = extracted_text[:1000]  # Limit to 1000 characters
                            st.success("✅ Text extracted successfully!")
                            st.text_area("Extracted text:", value=news_text, height=100, disabled=True)
                        else:
                            st.error("❌ Could not extract text from this URL")
                            news_text = ""
                except Exception as e:
                    st.error(f"❌ Error extracting URL: {str(e)}")
                    news_text = ""
        st.markdown("---")
        
        # Action buttons (full width)
        verify_clicked = st.button("🔍 Verify News", type="primary", use_container_width=True)
        example_clicked = st.button("🧪 Try Example", use_container_width=True)
        clear_clicked = st.button("🔄 Clear", use_container_width=True)
        
        if clear_clicked:
            st.rerun()
        
        # Handle example button
        if example_clicked:
            return "PM Modi is the current Prime Minister of India", verify_clicked, True
        
        return news_text, verify_clicked, False
    
    @staticmethod
    def render_results(result_data):
        """Render verification results beautifully"""
        if not result_data['success']:
            st.error(result_data['analysis'])
            return
        
        # Status indicators with warm, natural colors
        status_config = {
            'TRUE': {
                'icon': '✅',
                'color': '#81c784',
                'bg': 'rgba(129, 199, 132, 0.15)',
                'label': 'VERIFIED TRUE',
                'message': 'This news appears to be accurate based on available information.'
            },
            'FALSE': {
                'icon': '❌',
                'color': '#e57373',
                'bg': 'rgba(229, 115, 115, 0.15)',
                'label': 'FAKE NEWS DETECTED',
                'message': 'This news appears to be false or misleading.'
            },
            'PARTIALLY_TRUE': {
                'icon': '⚠️',
                'color': '#ffb74d',
                'bg': 'rgba(255, 183, 77, 0.15)',
                'label': 'PARTIALLY TRUE',
                'message': 'This news contains some truth but also inaccurate elements.'
            },
            'UNVERIFIED': {
                'icon': '❓',
                'color': '#7b93a7',
                'bg': 'rgba(123, 147, 167, 0.15)',
                'label': 'UNVERIFIED',
                'message': 'Insufficient information to verify this claim.'
            }
        }
        
        config = status_config.get(result_data['status'], status_config['UNVERIFIED'])
        
        # 1. BIG VERDICT BOX
        st.markdown(f"""
        <div style='background: {config["bg"]}; border: 3px solid {config["color"]}; border-radius: 15px; padding: 2rem; text-align: center; margin-bottom: 1.5rem; box-shadow: 0 4px 15px rgba(0,0,0,0.1);'>
            <div style='font-size: 3rem; margin-bottom: 0.5rem;'>{config["icon"]}</div>
            <h2 style='color: {config["color"]}; font-size: 1.8rem; margin: 0.5rem 0; font-weight: 700;'>{config["label"]}</h2>
            <p style='color: #4a4a4a; font-size: 1rem; margin-top: 0.5rem;'>{config["message"]}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 2. CONFIDENCE SCORE - Big and prominent
        confidence = result_data['confidence']
        conf_color = '#81c784' if confidence >= 70 else '#ffb74d' if confidence >= 50 else '#e57373'
        conf_label = 'High Confidence' if confidence >= 70 else 'Moderate Confidence' if confidence >= 50 else 'Low Confidence'
        
        st.markdown(f"""
        <div style='background: rgba(255, 255, 255, 0.9); border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; border: 2px solid #e0d5c1;'>
            <h3 style='color: #5d4037; margin: 0 0 1rem 0; font-size: 1.1rem;'>🎯 AI Confidence Score</h3>
            <div style='display: flex; align-items: center; gap: 1.5rem;'>
                <div style='flex: 0 0 120px;'>
                    <div style='font-size: 3rem; font-weight: 700; color: {conf_color};'>{confidence}%</div>
                    <div style='font-size: 0.9rem; color: #6d6d6d; font-weight: 500;'>{conf_label}</div>
                </div>
                <div style='flex: 1;'>
                    <div style='background: #e0e0e0; height: 25px; border-radius: 12px; overflow: hidden;'>
                        <div style='background: {conf_color}; height: 100%; width: {confidence}%; transition: width 0.5s;'></div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 3. AI ANALYSIS - Clear and readable
        st.markdown("""
        <div style='background: rgba(255, 255, 255, 0.9); border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; border: 2px solid #e0d5c1;'>
            <h3 style='color: #5d4037; margin: 0 0 1rem 0; font-size: 1.1rem;'>🧠 AI Analysis & Evidence</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style='background: #fafafa; border-left: 4px solid {config["color"]}; padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem;'>
            <div style='color: #3d3d3d; font-size: 0.95rem; line-height: 1.8; white-space: pre-wrap;'>{result_data['analysis']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 4. TRUSTED NEWS SOURCES - Prominent display
        st.markdown("""
        <div style='background: rgba(255, 255, 255, 0.9); border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; border: 2px solid #e0d5c1;'>
            <h3 style='color: #5d4037; margin: 0 0 1rem 0; font-size: 1.1rem;'>� Verify from Trusted Sources</h3>
            <p style='color: #6d6d6d; font-size: 0.85rem; margin-bottom: 1rem;'>Cross-check this news with these reliable sources:</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display sources in a grid
        cols = st.columns(2)
        for idx, source in enumerate(AppConfig.TRUSTED_SOURCES):
            with cols[idx % 2]:
                st.markdown(f"""
                <div style='background: #f7f3e9; padding: 0.8rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 3px solid #81c784;'>
                    <div style='color: #5d4037; font-weight: 600; font-size: 0.9rem;'>✓ {source}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # 5. RECOMMENDATION based on confidence
        st.markdown("<br>", unsafe_allow_html=True)
        if confidence <= 50:
            st.warning("⚠️ **Action Required**: Low confidence detected. Please verify this news from multiple trusted sources before believing or sharing.")
        elif confidence <= 70:
            st.info("ℹ️ **Recommendation**: Moderate confidence. Cross-check with at least 2-3 trusted news sources for confirmation.")
        else:
            st.success("✅ **Good Confidence**: The AI analysis is strong, but always verify important news from official sources before taking action.")
        
        # 6. TIMESTAMP
        st.markdown(f"""
        <div style='text-align: center; color: #6d6d6d; font-size: 0.85rem; margin-top: 1.5rem;'>
            ⏰ Analysis performed at: <strong>{result_data['timestamp']}</strong>
        </div>
        """, unsafe_allow_html=True)
        
        # Download report
        st.markdown("<br>", unsafe_allow_html=True)
        BeautifulUI.render_download_section(result_data)
    
    @staticmethod
    def render_download_section(result_data):
        """Render download report section"""
        st.markdown("""
        <div style='background: rgba(255, 255, 255, 0.9); border-radius: 12px; padding: 1.5rem; border: 2px solid #e0d5c1;'>
            <h3 style='color: #5d4037; margin: 0 0 0.5rem 0; font-size: 1.1rem;'>📥 Download Report</h3>
            <p style='color: #6d6d6d; font-size: 0.85rem; margin-bottom: 1rem;'>Save the verification report for your records</p>
        </div>
        """, unsafe_allow_html=True)
        
        report = {
            'verification_report': {
                'news_claim': st.session_state.get('last_query', ''),
                'status': result_data['status'],
                'confidence': f"{result_data['confidence']}%",
                'analysis': result_data['analysis'],
                'timestamp': result_data['timestamp'],
                'recommended_sources': AppConfig.TRUSTED_SOURCES,
                'disclaimer': 'This is an AI-assisted analysis. Always verify with multiple sources.'
            }
        }
        
        filename = f"news_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        st.download_button(
            "📄 Download Detailed Report (JSON)",
            data=json.dumps(report, indent=2, ensure_ascii=False),
            file_name=filename,
            mime="application/json",
            help="Download complete verification report",
            use_container_width=True
        )

# ============================================
# MAIN APPLICATION
# ============================================

def main():
    """Main application entry point"""
    
    # Setup page
    BeautifulUI.setup_page_config()
    
    # Initialize session state
    if 'verifier' not in st.session_state:
        st.session_state.verifier = IndianNewsVerifier()
    
    # Render UI components
    BeautifulUI.render_header()
    BeautifulUI.render_sidebar()
    
    # Three-column layout: Input | Results | Info
    col1, col2, col3 = st.columns([1.2, 1.5, 1])
    
    with col1:
        # Left column: Input form
        st.markdown("""
        <div style='text-align: center;'>
            <h3 style='color: #546e7a;'>📝 INPUT</h3>
        </div>
        """, unsafe_allow_html=True)
        news_text, verify_clicked, is_example = BeautifulUI.render_verification_form()
    
    with col2:
        # Middle column: Results
        st.markdown("""
        <div style='text-align: center;'>
            <h3 style='color: #546e7a;'>📊 ANALYSIS</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if 'last_result' not in st.session_state:
            # Initial state: show placeholder
            st.markdown("""
            <div style='text-align: center; padding: 2.5rem 1rem; background: rgba(255, 255, 255, 0.8); border-radius: 12px; border: 2px solid #e0d5c1; box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);'>
                <h2 style='color: #5d4037; font-size: 1.5rem;'>⚡ Ready to Analyze</h2>
                <p style='color: #4a4a4a; margin-top: 1rem; font-size: 0.95rem;'>
                    Enter news text in the input panel and click <strong style="color: #5d4037;">Verify News</strong> to begin analysis.
                </p>
                <p style='color: #6d6d6d; margin-top: 1.5rem; font-size: 0.9rem;'>
                    💡 Try the example to see the AI in action!
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Display stored results
            BeautifulUI.render_results(st.session_state.last_result)
    
    with col3:
        # Right column: Quick stats and tips
        st.markdown("""
        <div style='text-align: center;'>
            <h3 style='color: #546e7a;'>💡 TIPS</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background: rgba(255, 255, 255, 0.8); padding: 1rem; border-radius: 10px; border: 2px solid #e0d5c1; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);'>
            <h4 style='color: #5d4037; font-size: 1.05rem;'>🎯 Quick Tips</h4>
            <ul style='color: #4a4a4a; font-size: 0.85rem;'>
                <li>Paste full news articles for better accuracy</li>
                <li>Check multiple sources</li>
                <li>Look for official sources</li>
                <li>Be wary of sensational headlines</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background: rgba(255, 255, 255, 0.8); padding: 1rem; border-radius: 10px; border: 2px solid #e0d5c1; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);'>
            <h4 style='color: #5d4037; font-size: 1.05rem;'>📈 Status Guide</h4>
            <p style='color: #4a4a4a; font-size: 0.8rem; margin: 0.5rem 0;'>
                🟢 <strong style="color: #6bb86f;">TRUE</strong><br/>
                Verified information
            </p>
            <p style='color: #4a4a4a; font-size: 0.8rem; margin: 0.5rem 0;'>
                🔴 <strong style="color: #e57373;">FALSE</strong><br/>
                Identified as fake
            </p>
            <p style='color: #4a4a4a; font-size: 0.8rem; margin: 0.5rem 0;'>
                🟡 <strong style="color: #ffb74d;">PARTIAL</strong><br/>
                Mixed information
            </p>
            <p style='color: #4a4a4a; font-size: 0.8rem; margin: 0.5rem 0;'>
                ⚪ <strong style="color: #7b93a7;">UNVERIFIED</strong><br/>
                Insufficient data
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if 'last_result' in st.session_state:
            st.success(f"✅ Last analysis: {st.session_state.last_result['timestamp'].split()[1]}")
        else:
            st.info("⏳ Waiting for input...")
    
    # Process verification
    if (verify_clicked and news_text.strip()) or is_example:
        st.session_state.last_query = news_text
        
        with st.spinner("🤖 AI is analyzing the news claim..."):
            # Add realistic delay for better UX
            time.sleep(1)
            
            # Perform verification
            result = st.session_state.verifier.verify_news(news_text)
            st.session_state.last_result = result
        
        # Rerun to show results in right column
        st.rerun()
    
    elif verify_clicked and not news_text.strip():
        st.warning("⚠️ Please enter some news text to verify!")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #7F8C8D; padding: 2rem 0;'>
        <p><strong>🕵️‍♂️ Fake News Verifier</strong> • Fighting Misinformation with AI</p>
        <p>Built with Streamlit • Powered by Advanced AI • Version 2.0</p>
        <p style='font-family: "Courier New", Courier, monospace;'><em>Made with 📰 by Debasmita X Manisha X Joita</em></p>
        <p><small>Always cross-reference important news with multiple reliable sources</small></p>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# APPLICATION ENTRY POINT
# ============================================

if __name__ == "__main__":
    main()

# ============================================
# END OF FILE
# ============================================
