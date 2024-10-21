import streamlit as st
import random
from anthropic import Anthropic

# Set page layout and title
st.set_page_config(page_title="AI Tool Recommender", layout="wide")

# Mock database of AI tools for recommendation (just like in the React example)
ai_tools = [
    {
        'name': 'ActiveCampaign',
        'category': 'marketing_automation',
        'minBudget': 29,
        'maxBudget': 500,
        'features': ['Email Automation', 'CRM', 'Lead Scoring'],
        'businessSize': ['small', 'medium'],
        'complexity': 'moderate'
    },
    {
        'name': 'Mailchimp',
        'category': 'marketing_automation',
        'minBudget': 0,
        'maxBudget': 300,
        'features': ['Email Automation', 'Landing Pages', 'Social Media'],
        'businessSize': ['small'],
        'complexity': 'easy'
    },
    {
        'name': 'Marketo',
        'category': 'marketing_automation',
        'minBudget': 1195,
        'maxBudget': 5000,
        'features': ['Email Automation', 'CRM', 'Lead Scoring', 'Advanced Analytics'],
        'businessSize': ['large', 'enterprise'],
        'complexity': 'complex'
    },
]

# Icons dictionary to represent attributes
def get_icon(attribute):
    return {
        "marketing_automation": "🎯",
        "content_creation": "✍️",
        "analytics": "📊",
        "crm": "👥",
        "email_automation": "✉️",
        "social_media": "📱",
        "moderate": "⚙️",
        "complex": "⚙️",
        "easy": "✅",
        "small": "🏢",
        "medium": "🏢🏢",
        "large": "🏢🏢🏢"
    }.get(attribute, "🔧")

# Calculate tool match score based on form data
def calculate_tool_score(tool, form_data):
    score = 0
    budget = int(form_data['budget'])

    if tool['minBudget'] <= budget <= tool['maxBudget']:
        score += 30
    if form_data['businessSize'] in tool['businessSize']:
        score += 25
    if form_data['category'] == tool['category']:
        score += 25
    if form_data['complexity'] == tool['complexity']:
        score += 20

    return score

# Main function
def main():
    st.title("🤖 AI Tool Recommender")

    with st.sidebar:
        api_key = st.text_input("🔑 API Key", type="password")
    
    # Input form
    with st.form("tool_recommendation_form"):
        st.write("### 📋 Fill out the form to get personalized AI tool recommendations")
        
        business_size = st.selectbox("🏢 Business Size", ["small", "medium", "large"])
        budget = st.number_input("💵 Monthly Budget (USD)", min_value=0, value=100)
        category = st.selectbox("📊 Tool Category", ["marketing_automation", "content_creation", "analytics", "crm"])
        complexity = st.selectbox("⚙️ Complexity", ["easy", "moderate", "complex"])
        
        submitted = st.form_submit_button("🔍 Get Recommendations")
    
    if submitted:
        # Simulate response data
        form_data = {
            'businessSize': business_size,
            'budget': budget,
            'category': category,
            'complexity': complexity
        }

        # Calculate match score for each tool
        recommendations = [
            {**tool, 'score': calculate_tool_score(tool, form_data)}
            for tool in ai_tools
        ]

        # Sort tools based on score
        recommendations = sorted(recommendations, key=lambda x: x['score'], reverse=True)

        # Display recommendations
        st.write("## 🎯 Recommended Tools for You")

        for idx, tool in enumerate(recommendations):
            # Highlight the top tool
            is_best_match = idx == 0
            tool_icon = get_icon(tool['category'])
            budget_icon = "💰"
            business_size_icons = " ".join([get_icon(size) for size in tool['businessSize']])
            complexity_icon = get_icon(tool['complexity'])
            
            st.markdown(f"""
            <div style="border: 2px solid {'#4CAF50' if is_best_match else '#e0e0e0'}; border-radius: 10px; padding: 15px; margin-bottom: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                <h3 style="font-size: 22px; font-weight: bold;">{tool_icon} {tool['name']}</h3>
                <p><strong>{budget_icon} Budget Range:</strong> ${tool['minBudget']} - ${tool['maxBudget']}</p>
                <p><strong>🏢 Business Size:</strong> {business_size_icons}</p>
                <p><strong>{complexity_icon} Complexity:</strong> {tool['complexity'].capitalize()}</p>
                <p><strong>🛠️ Features:</strong> {', '.join(tool['features'])}</p>
                <p style="color: {'#4CAF50' if is_best_match else '#000'}; font-weight: bold;">Match Score: {tool['score']}%</p>
            </div>
            """, unsafe_allow_html=True)
        
if __name__ == "__main__":
    main()
