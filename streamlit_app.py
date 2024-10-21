import streamlit as st
from anthropic import Anthropic
import time
import random

def analyze_with_claude(client, data, max_retries=3):
    prompt = f"""Based on these requirements, recommend 3 AI tools:

Business Size: {data['business_size']}
Budget: ${data['budget']}
Category: {data['category']}
Complexity: {data['complexity']}
Requirements: {data['requirements']}

For each tool provide:
1. Name and description
2. Pricing
3. Best suited for
4. Key features (3-4 bullet points)
5. Pros (2-3 points)
6. Cons (2-3 points) 
7. Match score (0-100%)
8. Website URL

Format as a clear markdown list with headers."""

    for attempt in range(max_retries):
        try:
            st.info(f"Analyzing requirements (Attempt {attempt + 1}/{max_retries})...")
            response = client.beta.messages.create(
                model="claude-3-opus-20240229",
                messages=[{
                    "role": "user", 
                    "content": prompt
                }],
                temperature=0.7,
                max_tokens=2000
            )
            return response.content
                
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
    st.title("AI Tool Recommender")
    
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ''
    
    api_key = st.text_input("Enter Anthropic API Key:", 
                           value=st.session_state.api_key,
                           type="password")
                           
    if api_key:
        st.session_state.api_key = api_key
        client = Anthropic(api_key=api_key)
        
        with st.form("recommendation_form"):
            business_size = st.selectbox(
                "Business Size",
                ["Startup (1-10)", "Small (11-50)", "Medium (51-500)", "Large (500+)"]
            )
            
            budget = st.number_input(
                "Monthly Budget (USD)",
                min_value=0,
                max_value=10000,
                step=50,
                value=100
            )
            
            category = st.selectbox(
                "Tool Category",
                ["Marketing Automation", "Content Creation", "Analytics", "CRM", 
                 "Project Management", "Customer Service", "Sales", "Other"]
            )
            
            complexity = st.select_slider(
                "Technical Complexity",
                options=["Beginner", "Intermediate", "Advanced"]
            )
            
            requirements = st.text_area(
                "Specific Requirements",
                placeholder="Describe your needs..."
            )
            
            submitted = st.form_submit_button("Get Recommendations")
            
            if submitted:
                with st.spinner("Finding the best AI tools for you..."):
                    recommendations = analyze_with_claude(client, {
                        "business_size": business_size,
                        "budget": budget,
                        "category": category,
                        "complexity": complexity,
                        "requirements": requirements
                    })
                    
                    if recommendations:
                        st.markdown(recommendations)

    else:
        st.warning("Please enter your Anthropic API key to continue")

if __name__ == "__main__":
    main()
