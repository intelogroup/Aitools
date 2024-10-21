import streamlit as st
import time
import random
from anthropic import Anthropic

# Function to interact with Claude and fetch recommendations
def analyze_with_claude(client, data, max_retries=3):
    prompt = f"""Based on these requirements, recommend 3 AI tools:

Business Size: {data['business_size']}
Budget: ${data['budget']}
Category: {data['category']}
Complexity: {data['complexity']}
Requirements: {data['requirements']}

Structure each recommendation like this:

# 1. [Tool Name]

## Description
[Description text]

## Pricing
[Pricing details]

## Best suited for
[Target users]

## Key features
- [Feature 1]
- [Feature 2]
- [Feature 3]

## Pros
- [Pro 1]
- [Pro 2]
- [Pro 3]

## Cons
- [Con 1]
- [Con 2]

## Match score
[X]%

## Website URL
[URL]

Provide 3 recommendations in this exact format."""

    for attempt in range(max_retries):
        try:
            st.info(f"Finding recommendations (Attempt {attempt + 1}/{max_retries})...")
            response = client.beta.messages.create(
                model="claude-3-opus-20240229",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Handle the response content properly
            if hasattr(response, 'content'):
                # If response.content is a list of TextBlocks, join their text
                if isinstance(response.content, list):
                    analysis = ''.join([block.text for block in response.content])
                else:
                    analysis = response.content
                
                # Display the markdown-formatted response
                st.markdown(analysis, unsafe_allow_html=True)
                return True
            else:
                st.error("Unexpected response format")
                return None
                
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

# Main function to display the form and process the request
def main():
    st.title("AI Tool Recommender")
    
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ''
    
    # Input API Key
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
                analyze_with_claude(client, {
                    "business_size": business_size,
                    "budget": budget,
                    "category": category,
                    "complexity": complexity,
                    "requirements": requirements
                })

    else:
        st.warning("Please enter your Anthropic API key to continue")

# Run the app
if __name__ == "__main__":
    main()
