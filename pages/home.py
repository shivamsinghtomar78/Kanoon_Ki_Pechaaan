import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv
import os
import time
from datetime import datetime
import re
import json
import http.client
import urllib.parse

# Load environment variables
load_dotenv()

# Streamlit page configuration
st.set_page_config(
    page_title="Kanoon ki Pehchaan",
    page_icon="⚖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for animations and styling
def local_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&family=Orbitron:wght@400;700&display=swap');
        body {
            font-family: 'Montserrat', sans-serif;
            background: linear-gradient(135deg, #0A0A0A 0%, #1A1A1A 100%);
            color: #FFFFFF;
        }
        h1, h2, h3 { font-family: 'Orbitron', sans-serif; }
        .main-header {
            position: fixed;
            top: 0;
            width: 100%;
            text-align: center;
            padding: 1.5rem;
            background: rgba(0, 0, 0, 0.8);
            border-bottom: 2px solid #00FFFF;
            box-shadow: 0 0 15px #00FFFF;
            animation: slideInLeft 0.5s ease-in;
            z-index: 1000;
        }
        .flag-stripe {
            height: 6px;
            background: linear-gradient(90deg, #FF00FF 33%, #00FFFF 66%, #00FF00 100%);
            animation: slideInLeft 0.5s ease-in;
        }
        .stTextInput > div > input {
            border-radius: 20px;
            padding: 0.8rem 2rem;
            background: rgba(0, 0, 0, 0.7);
            border: 2px solid #00FFFF;
            color: #FFFFFF;
            transition: all 0.3s ease;
        }
        .stTextInput > div > input:focus {
            border-color: #FF00FF;
            box-shadow: 0 0 15px #FF00FF;
        }
        .stButton > button {
            border-radius: 20px;
            padding: 0.6rem 1.5rem;
            background: linear-gradient(135deg, #00FFFF, #FF00FF);
            color: #000000;
            border: none;
            font-weight: bold;
            text-transform: uppercase;
            box-shadow: 0 0 10px #00FFFF;
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            transform: scale(1.05);
            box-shadow: 0 0 20px #FF00FF;
        }
        .card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            border: 1px solid rgba(0, 255, 255, 0.3);
            padding: 1.5rem;
            margin: 1rem 0;
            transition: all 0.3s ease;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 0 20px #FF00FF;
        }
        .footer {
            position: fixed;
            bottom: 0;
            width: 100%;
            background: rgba(0, 0, 0, 0.9);
            padding: 1rem;
            text-align: center;
            border-top: 2px solid #00FFFF;
            animation: fadeIn 0.5s ease-in;
        }
        .sidebar-content {
            padding: 1rem;
            background: rgba(0, 0, 0, 0.9);
            border-right: 2px solid #00FFFF;
            animation: slideInLeft 0.5s ease-in;
        }
        .sidebar-content .stButton > button {
            width: 100%;
            margin-bottom: 1rem;
        }
        .assistant-message {
            background: rgba(0, 0, 0, 0.7);
            border-radius: 15px;
            border: 1px solid rgba(0, 255, 255, 0.3);
            padding: 1rem;
            margin: 1rem 0;
            animation: slideInRight 0.5s ease-in;
        }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes slideInLeft { from { transform: translateX(-100%); } to { transform: translateX(0); } }
        @keyframes slideInRight { from { transform: translateX(100%); } to { transform: translateX(0); } }
    </style>
    """, unsafe_allow_html=True)

# Apply custom CSS
local_css()

# Pydantic models for structured output
class LegalReference(BaseModel):
    title: str = Field(description="Title of the legal document or case")
    source: str = Field(description="Source of the document (court, statute, etc.)")
    relevance: str = Field(description="Explanation of how this reference relates to the query")
    key_points: List[str] = Field(description="Main legal points from this reference")
    citation: Optional[str] = Field(None, description="Formal legal citation if available")

class LegalAnalysis(BaseModel):
    query_summary: str = Field(description="Concise summary of the legal question")
    applicable_laws: List[str] = Field(description="List of applicable laws and sections")
    key_principles: List[str] = Field(description="Key legal principles relevant to the query")
    practical_implications: str = Field(description="Practical implications for the person asking")
    references: List[LegalReference] = Field(description="Detailed references to relevant cases and statutes")

# Initialize session state
def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "You are Kanoon ki Pehchaan, an AI assistant specialized in Indian law."}
        ]
    if "response_time" not in st.session_state:
        st.session_state.response_time = 0
    if "chat_started" not in st.session_state:
        st.session_state.chat_started = False
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = True

# Initialize the model
@st.cache_resource
def get_model():
    try:
        return ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.2)
    except Exception as e:
        st.error(f"Failed to initialize model: {e}")
        return None

# Setup structured chain
def setup_structured_chain():
    parser = PydanticOutputParser(pydantic_object=LegalAnalysis)
    template = """
    You are Kanoon ki Pehchaan, an AI legal expert specializing in Indian law.
    
    USER QUERY: {query}
    
    INDIAN KANOON DATA:
    {kanoon_data}
    
    Your task is to analyze this query and the provided legal references from Indian Kanoon.
    Provide a comprehensive legal analysis following the structured format below.
    
    {format_instructions}
    
    Make sure to properly cite any legal references and maintain a professional legal tone.
    Include only factual information supported by the provided Indian Kanoon data or well-established legal principles.
    """
    prompt = ChatPromptTemplate.from_template(template).partial(
        format_instructions=parser.get_format_instructions()
    )
    model = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.2, max_output_tokens=4096)
    chain = prompt | model | parser
    return chain

# Check if query is related to Indian law
def is_indian_law_related(query):
    if not query or not isinstance(query, str):
        return False
    query = query.lower()
    indian_legal_keywords = ["indian", "india", "ipc", "crpc", "constitution", "section", "act", "law", "case", "statute", "article", "court"]
    for keyword in indian_legal_keywords:
        if keyword in query:
            return True
    patterns = [r"section \d+", r"article \d+", r"ipc \d+"]
    for pattern in patterns:
        if re.search(pattern, query, re.IGNORECASE):
            return True
    return False

# Indian Kanoon API wrapper
class IKApi:
    def __init__(self, token):
        self.headers = {'Authorization': f'Token {token}', 'Accept': 'application/json'}
        self.basehost = 'api.indiankanoon.org'

    def call_api(self, url):
        connection = http.client.HTTPSConnection(self.basehost)
        connection.request('GET', url, headers=self.headers)
        response = connection.getresponse()
        results = response.read().decode('utf8')
        return results

    def search(self, query, pagenum=0, maxpages=1):
        query = urllib.parse.quote_plus(query.encode('utf8'))
        url = f'/search/?formInput={query}&pagenum={pagenum}&maxpages={maxpages}'
        return self.call_api(url)
    
    def get_document(self, doc_id):
        url = f'/doc/{doc_id}/'
        return self.call_api(url)

# Fetch data from Indian Kanoon
def fetch_indian_kanoon_data(query):
    api_key = os.getenv("INDIAN_KANOON_API_KEY")
    if not api_key:
        st.error("Indian Kanoon API key not found.")
        return None
    ikapi = IKApi(api_key)
    try:
        search_results = ikapi.search(query)
        results_json = json.loads(search_results)
        if results_json.get("docs"):
            for i, doc in enumerate(results_json["docs"][:3]):  
                if doc.get("tid"):
                    try:
                        doc_content = ikapi.get_document(doc["tid"])
                        if doc_content:
                            results_json["docs"][i]["content"] = doc_content
                    except Exception as e:
                        results_json["docs"][i]["content"] = f"Error fetching content: {str(e)}"
        return results_json
    except Exception as e:
        st.error(f"Failed to fetch data from Indian Kanoon: {e}")
        return None

# Process legal query
def process_legal_query(query, kanoon_data):
    start_time = time.time()
    try:
        formatted_kanoon_data = "No data found from Indian Kanoon."
        if kanoon_data and kanoon_data.get("found", 0) > 0:
            formatted_kanoon_data = f"Found {kanoon_data.get('found', 0)} results. Here are the top matches:\n\n"
            for i, doc in enumerate(kanoon_data.get("docs", [])[:3]):
                formatted_kanoon_data += f"DOCUMENT {i+1}:\n"
                formatted_kanoon_data += f"Title: {doc.get('title', 'No title')}\n"
                formatted_kanoon_data += f"Source: {doc.get('docsource', 'Unknown')}\n"
                formatted_kanoon_data += f"Date: {doc.get('docdate', 'Unknown')}\n"
                formatted_kanoon_data += f"Link: https://api.indiankanoon.org/doc/{doc.get('tid', '')}/\n"
                if doc.get("content"):
                    content_sample = doc["content"][:1000] + "..." if len(doc["content"]) > 1000 else doc["content"]
                    formatted_kanoon_data += f"Excerpt: {content_sample}\n"
                formatted_kanoon_data += "\n"
        chain = setup_structured_chain()
        result = chain.invoke({"query": query, "kanoon_data": formatted_kanoon_data})
        process_time = time.time() - start_time
        return result, process_time
    except Exception as e:
        process_time = time.time() - start_time
        st.error(f"Error processing with Gemini: {str(e)}")
        fallback_response = LegalAnalysis(
            query_summary=query,
            applicable_laws=["Could not parse detailed laws"],
            key_principles=["Error in legal analysis"],
            practical_implications=f"Error occurred during analysis: {str(e)}",
            references=[]
        )
        return fallback_response, process_time

# Format response for display
def format_response_for_display(legal_analysis):
    formatted_response = f"""
### Query Summary
{legal_analysis.query_summary}

### Applicable Laws
"""
    for law in legal_analysis.applicable_laws:
        formatted_response += f"- {law}\n"
    formatted_response += f"""
### Key Legal Principles
"""
    for principle in legal_analysis.key_principles:
        formatted_response += f"- {principle}\n"
    formatted_response += f"""
### Practical Implications
{legal_analysis.practical_implications}

### Legal References
"""
    for ref in legal_analysis.references:
        formatted_response += f"""
**{ref.title}** _(Source: {ref.source})_
- Relevance: {ref.relevance}
- Key Points:
"""
        for point in ref.key_points:
            formatted_response += f"  - {point}\n"
        if ref.citation:
            formatted_response += f"- Citation: {ref.citation}\n"
    return formatted_response

# Display messages with animations
def display_messages():
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(f"""
                <div style="background: rgba(227, 242, 253, 0.2); padding: 12px; border-radius: 15px; border: 1px solid rgba(187, 222, 251, 0.3); margin-bottom: 8px; color: #ffffff;">
                    {message["content"]}
                </div>
                <div style="font-size: 0.8em; color: #bbdefb; text-align: right; margin-top: 4px;">
                    {message.get("timestamp", datetime.now().strftime("%H:%M"))}
                </div>
                """, unsafe_allow_html=True)
        elif message["role"] == "assistant":
            with st.chat_message("assistant", avatar="⚖"):
                st.markdown(f"""
                <div class="assistant-message">
                    {message["content"]}
                    <div style="font-size: 0.8em; color: #e9ecef; text-align: right; margin-top: 4px;">
                        {message.get("timestamp", datetime.now().strftime("%H:%M"))} | ⏱ {message.get("response_time", 0.0):.1f}s
                    </div>
                </div>
                """, unsafe_allow_html=True)

# Process user input
def process_user_input(user_input):
    timestamp = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({"role": "user", "content": user_input, "timestamp": timestamp})
    is_legal_query = is_indian_law_related(user_input)
    if not is_legal_query:
        response = "I can only answer questions related to Indian law. Please rephrase your query to focus on Indian legal matters."
        response_time = 0.0
    else:
        kanoon_data = fetch_indian_kanoon_data(user_input)
        if kanoon_data:
            legal_analysis, response_time = process_legal_query(user_input, kanoon_data)
            response = format_response_for_display(legal_analysis)
        else:
            response = "Sorry, I couldn't find relevant legal information for your query. Please try rephrasing your question with more specific legal terms or references."
            response_time = 0.0
    st.session_state.messages.append({
        "role": "assistant", 
        "content": response, 
        "timestamp": datetime.now().strftime("%H:%M"),
        "response_time": response_time
    })
    st.session_state.response_time = response_time

 
def main():
    init_session_state()
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        if st.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.switch_page("account.py")
        st.markdown("""
        ### About Kanoon ki Pehchaan
        *Kanoon ki Pehchaan* is an AI-powered legal assistant for Indian law.
        ### Key Features
        - Real-time legal assistance
        - Comprehensive Indian law database
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    if not st.session_state.chat_started:
        st.info("🙏 Namaste! Welcome to Kanoon ki Pehchaan!")
        st.session_state.chat_started = True
    display_messages()
    user_input = st.chat_input("Ask about Indian laws...")
    if user_input:
        process_user_input(user_input)
        st.rerun()
    st.markdown('<div class="footer">Powered by Gemini 1.5 Pro</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()