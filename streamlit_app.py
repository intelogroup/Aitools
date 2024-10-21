import streamlit as st
from anthropic import Anthropic
import time
import random
import pandas as pd

def analyze_with_claude(client, data, max_retries=3):
    prompt = f"""Based on these requirements, recommend 3 AI tools:
Business Size: {data['business_size']}
Budget: ${data['budget']}
Category: {data['category']}
Complexity: {data['complexity']}
Requirements: {data['requirements']}

Return recommendations in markdown format with:
# [Tool Name] (Match Score: X%)
## Description
[Description]
## Pricing & Budget
[Pricing details]
## Best For
[Target users]
## Key Features
- Feature 1
- Feature 2
## Pros & Cons
✓ [Pro 1]
✓ [Pro 2]
× [Con 1]
× [Con 2]"""

    for attempt in range(max_retries):
        try:
            with st.spinner("Analyzing requirements..."):
                response = client.beta.messages.create(
                    model="claude-3-opus-20240229",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=2000
                )
                
                if hasattr(response, 'content'):
                    analysis = ''.join([block.text for block in response.content]) if isinstance(response.content, list) else response.content
                    st.markdown(analysis)
                    return True
                    
        except Exception as e:
            if "overloaded" in str(e).lower():
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 3 + random.uniform(1, 3)
                    st.warning(f"Service busy. Retrying in {wait_time:.1f} seconds...")
                    time.sleep(wait_time)
                    continue
                st.error("Service temporarily unavailable. Please try again later.")
            else:
                st.error(f"Error: {str(e)}")
            return None

def main():
    st.set_page_config(page_title="AI Tool Recommender", layout="wide")
    
    st.title("🤖 AI Tool Recommender")
    
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ''
    
    with st.sidebar:
        api_key = st.text_input("Enter Anthropic API Key:", 
                               value=st.session_state.api_key,
                               type="password")
                               
    if api_key:
        st.session_state.api_key = api_key
        client = Anthropic(api_key=api_key)
        
        with st.form("recommendation_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                business_size = st.selectbox(
                    "Business Size",
                    ["Startup (1-10)", "Small (11-50)", "Medium (51-500)", "Large (500+)"],
                    key="business_size_select"
                )
                
                budget = st.number_input(
                    "Monthly Budget (USD)",
                    min_value=0,
                    max_value=10000,
                    step=50,
                    value=100,
                    key="budget_input"
                )
            
            with col2:
                category = st.selectbox(
                    "Tool Category",
                    ["Marketing Automation", "Content Creation", "Analytics", "CRM", 
                     "Project Management", "Customer Service", "Sales", "Other"],
                    key="category_select"
                )
                
                complexity = st.select_slider(
                    "Technical Complexity",
                    options=["Beginner", "Intermediate", "Advanced"],
                    key="complexity_slider"
                )
            
            requirements = st.text_area(
                "Specific Requirements",
                placeholder="Describe your needs...",
                key="requirements_area"
            )
            
            submitted = st.form_submit_button("Get Recommendations")
            
            if submitted:
                with st.spinner("Analyzing your requirements..."):
                    analyze_with_claude(client, {
                        "business_size": business_size,
                        "budget": budget,
                        "category": category,
                        "complexity": complexity,
                        "requirements": requirements
                    })

    else:
        st.warning("Please enter your API key in the sidebar to continue")

if __name__ == "__main__":
    main()
