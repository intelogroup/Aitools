# app.py
import streamlit as st
import pandas as pd
import anthropic

# Configure page
st.set_page_config(page_title="AI Tool Recommender", layout="wide")

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

# Form inputs
def create_recommendation_form():
    with st.form("recommendation_form"):
        st.title("AI Tool Recommender")
        
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
        return submitted, {
            "business_size": business_size,
            "budget": budget,
            "category": category,
            "complexity": complexity,
            "requirements": requirements
        }

def get_recommendations(data):
    prompt = f"""Analyze these business requirements and suggest suitable AI tools:
    Business Size: {data['business_size']}
    Budget: ${data['budget']}
    Category: {data['category']}
    Complexity: {data['complexity']}
    Requirements: {data['requirements']}
    
    Provide a JSON response with 3-5 recommended tools:
    {{"recommendations": [
        {{
            "name": "Tool Name",
            "description": "Brief description",
            "pricing": "Pricing details",
            "bestFor": "Ideal use cases",
            "keyFeatures": ["feature1", "feature2"],
            "pros": ["pro1", "pro2"],
            "cons": ["con1", "con2"],
            "matchScore": 95,
            "websiteUrl": "url"
        }}
    ]}}"""

    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=2000,
        temperature=0.7,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content

def display_recommendations(recommendations):
    for idx, tool in enumerate(recommendations):
        with st.container():
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader(f"{tool['name']}")
                st.write(tool['description'])
                
                with st.expander("Key Features"):
                    for feature in tool['keyFeatures']:
                        st.write(f"• {feature}")
            
            with col2:
                st.metric("Match Score", f"{tool['matchScore']}%")
                st.write(f"**Pricing:** {tool['pricing']}")
                
            col3, col4 = st.columns(2)
            with col3:
                st.write("**Pros:**")
                for pro in tool['pros']:
                    st.write(f"✓ {pro}")
            
            with col4:
                st.write("**Cons:**")
                for con in tool['cons']:
                    st.write(f"× {con}")
            
            st.markdown(f"[Visit Website]({tool['websiteUrl']})")
            st.divider()

def main():
    submitted, form_data = create_recommendation_form()
    
    if submitted:
        with st.spinner("Analyzing your requirements..."):
            try:
                recommendations = get_recommendations(form_data)
                display_recommendations(recommendations['recommendations'])
            except Exception as e:
                st.error(f"Error getting recommendations: {str(e)}")

if __name__ == "__main__":
    main()
