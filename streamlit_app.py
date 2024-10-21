import streamlit as st
import json
import anthropic

# Page config
st.set_page_config(page_title="AI Tool Recommender", layout="wide")

# Safe API key handling
try:
    api_key = st.secrets["ANTHROPIC_API_KEY"]
    client = anthropic.Anthropic(api_key=api_key)
except Exception as e:
    st.error("API key not found. Please configure ANTHROPIC_API_KEY in your secrets.")
    st.stop()

def get_recommendations(data):
    try:
        prompt = f"""As an AI tool recommendation expert, analyze these requirements and suggest suitable AI tools:

Business Size: {data['business_size']}
Monthly Budget: ${data['budget']}
Category: {data['category']}
Complexity: {data['complexity']}
Requirements: {data['requirements']}

Provide exactly 3 tool recommendations in JSON format."""

        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=2000,
            temperature=0.7,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(response.content)
    except Exception as e:
        st.error(f"Error getting recommendations: {str(e)}")
        return None

def main():
    st.title("AI Tool Recommender")
    
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
            with st.spinner("Analyzing requirements..."):
                data = {
                    "business_size": business_size,
                    "budget": budget,
                    "category": category,
                    "complexity": complexity,
                    "requirements": requirements
                }
                
                results = get_recommendations(data)
                
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
                                    
                                    col3, col4 = st.columns(2)
                                    with col3:
                                        st.write("**Pros:**")
                                        for pro in tool['pros']:
                                            st.write(f"✓ {pro}")
                                    
                                    with col4:
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
