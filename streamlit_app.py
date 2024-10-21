import streamlit as st
import json
from anthropic import Anthropic
import time
import random

def get_recommendations_with_retry(client, data, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = client.beta.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=2000,
                messages=[{
                    "role": "user", 
                    "content": f"""Analyze these requirements and suggest AI tools:
Business Size: {data['business_size']}
Budget: ${data['budget']}
Category: {data['category']}
Complexity: {data['complexity']}
Requirements: {data['requirements']}

Provide 3 recommendations in JSON with:
- name
- description 
- pricing
- bestFor
- keyFeatures (list)
- pros (list) 
- cons (list)
- matchScore (0-100)
- websiteUrl"""
                }],
                temperature=0.7
            )
            return json.loads(response.content)
        except Exception as e:
            if attempt == max_retries - 1:
                st.error(f"Failed after {max_retries} attempts: {str(e)}")
                return None
            wait_time = (attempt + 1) * 2 + random.uniform(0, 1)
            st.warning(f"Attempt {attempt + 1} failed. Retrying in {wait_time:.1f} seconds...")
            time.sleep(wait_time)

def main():
    st.title("AI Tool Recommender")
    
    api_key = st.text_input("Enter your Anthropic API Key:", type="password")
    if not api_key:
        st.warning("Please enter your Anthropic API key to continue")
        st.stop()
    
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
            step=50
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
            data = {
                "business_size": business_size,
                "budget": budget,
                "category": category,
                "complexity": complexity,
                "requirements": requirements
            }
            
            with st.spinner("Analyzing requirements..."):
                results = get_recommendations_with_retry(client, data)
                
                if results and 'recommendations' in results:
                    for tool in results['recommendations']:
                        with st.container():
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.subheader(tool['name'])
                                st.write(tool['description'])
                                with st.expander("Features & Details"):
                                    st.write("**Key Features:**")
                                    for feature in tool['keyFeatures']:
                                        st.write(f"• {feature}")
                                    
                                    cols = st.columns(2)
                                    with cols[0]:
                                        st.write("**Pros:**")
                                        for pro in tool['pros']:
                                            st.write(f"✓ {pro}")
                                    with cols[1]:
                                        st.write("**Cons:**")
                                        for con in tool['cons']:
                                            st.write(f"× {con}")
                            
                            with col2:
                                st.metric("Match Score", f"{tool['matchScore']}%")
                                st.write(f"**Pricing:** {tool['pricing']}")
                                if 'websiteUrl' in tool:
                                    st.link_button("Visit Website", tool['websiteUrl'])
                            st.divider()

if __name__ == "__main__":
    main()
