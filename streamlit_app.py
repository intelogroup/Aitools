import streamlit as st
from anthropic import Anthropic
import time
import random

st.set_page_config(page_title="AI Tool Recommender", layout="wide")

def style_ui():
    st.markdown("""
        <style>
            .tool-card {padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 10px 0;}
            .score-bar {height: 10px; border-radius: 5px; background: #e0e0e0; margin: 5px 0;}
            .score-fill {height: 100%; border-radius: 5px; background: #4CAF50;}
        </style>
    """, unsafe_allow_html=True)

def get_icon(category):
    return {
        "Marketing Automation": "🎯",
        "Content Creation": "✍️",
        "Analytics": "📊",
        "CRM": "👥",
        "Project Management": "📋",
        "Customer Service": "💬",
        "Sales": "💰"
    }.get(category, "🔧")

def analyze_tools(client, data):
    prompt = f"""Recommend 3 AI tools based on:
- Business: {data['business_size']}
- Budget: ${data['budget']}
- Category: {data['category']}
- Complexity: {data['complexity']}
- Needs: {data['requirements']}

Format as:
# Tool Name
## Match Score
[0-100]%
## Description
[text]
## Pricing
[details]
## Features
- [feature]
## Pros/Cons
✓ [pro]
× [con]"""

    try:
        with st.spinner("Analyzing requirements..."):
            response = client.beta.messages.create(
                model="claude-3-opus-20240229",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )
            
            if hasattr(response, 'content'):
                # Handle the response content properly
                if isinstance(response.content, list):
                    content = ''.join([block.text for block in response.content])
                else:
                    content = response.content
                
                # Display with custom styling
                st.markdown(f"""
                    <div class="tool-card">
                        <h3>{get_icon(data['category'])} AI Tool Recommendations</h3>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown(content)
                return True
                
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return False

def main():
    style_ui()
    st.title("🤖 AI Tool Recommender")
    
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ''
    
    with st.sidebar:
        api_key = st.text_input("API Key:", type="password", value=st.session_state.api_key)
        
    if api_key:
        st.session_state.api_key = api_key
        client = Anthropic(api_key=api_key)
        
        with st.form("recommend_form"):
            c1, c2 = st.columns(2)
            with c1:
                size = st.selectbox("Business Size", 
                    ["Startup (1-10)", "Small (11-50)", "Medium (51-500)", "Large (500+)"],
                    key="size")
                budget = st.number_input("Budget (USD)", min_value=0, value=100, step=50, key="budget")
            
            with c2:
                category = st.selectbox("Category",
                    ["Marketing Automation", "Content Creation", "Analytics", "CRM", 
                     "Project Management", "Customer Service", "Sales", "Other"],
                    key="category")
                complexity = st.select_slider("Complexity",
                    ["Beginner", "Intermediate", "Advanced"], key="complexity")
            
            requirements = st.text_area("Requirements", key="reqs", 
                placeholder="Describe your needs...")
            
            if st.form_submit_button("Get Recommendations"):
                analyze_tools(client, {
                    "business_size": size,
                    "budget": budget,
                    "category": category,
                    "complexity": complexity,
                    "requirements": requirements
                })
    else:
        st.warning("Please enter your API key")

if __name__ == "__main__":
    main()
