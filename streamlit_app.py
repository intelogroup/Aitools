import streamlit as st
import random
from anthropic import Anthropic

# Icons dictionary to represent attributes
ICONS = {
    "marketing_automation": "💼",
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
}

def get_icon(attribute):
    return ICONS.get(attribute, "")

def format_tool_section(tool, is_best_match):
    tool_icon = get_icon(tool.get('category', 'unknown'))
    budget_icon = "💰"
    business_size_icons = " ".join([get_icon(size) for size in tool.get('businessSize', [])])
    complexity_icon = get_icon(tool.get('complexity', 'unknown'))

    return f"""
    <div style="border: 2px solid {'#4CAF50' if is_best_match else '#e0e0e0'}; border-radius: 10px; padding: 15px; margin-bottom: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
        <h3 style="font-size: 22px; font-weight: bold;">{tool_icon} {tool.get('name', 'Unknown Tool')} <span style="background-color:#8B0000;color:white;border-radius:50%;padding:4px 8px;font-weight:bold;">{tool.get('score', 0)}%</span></h3>
        <p><strong>{budget_icon} Budget Range:</strong> ${tool.get('minBudget', 0)} - ${tool.get('maxBudget', 0)}</p>
        <p><strong>🏢 Business Size:</strong> {business_size_icons}</p>
        <p><strong>{complexity_icon} Complexity:</strong> {tool.get('complexity', 'Unknown').capitalize()}</p>
        <p><strong>🛠️ Features:</strong> {', '.join(tool.get('features', ['No features available']))}</p>
    </div>
    """

def get_claude_recommendations(client, form_data):
    prompt = f"""Based on the following business requirements, recommend 3 AI tools:
    - Business Size: {form_data['businessSize']}
    - Monthly Budget: ${form_data['budget']}
    - Tool Category: {form_data['category']}
    - Complexity Level: {form_data['complexity']}
    - Specific Requirements: {form_data['requirements']}

    Provide recommendations in the following format:
    # Tool Name
    ## Match Score (0-100%)
    ## Budget Range (USD)
    ## Business Size (small, medium, large)
    ## Complexity Level
    ## Key Features
    """

    try:
        with st.spinner("🔍 Analyzing your requirements..."):
            response = client.beta.messages.create(
                model="claude-3-opus-20240229",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )
            
            if hasattr(response, 'content'):
                recommendations = []
                for block in response.content:
                    if block.type == 'text':
                        tool_sections = block.text.split('\n')
                        if len(tool_sections) >= 6:
                            try:
                                tool = {
                                    'name': tool_sections[0].strip('# '),
                                    'score': int(tool_sections[1].strip('## Match Score (0-100%): ')) if tool_sections[1].strip('## Match Score (0-100%): ').isdigit() else 0,
                                    'minBudget': int(tool_sections[2].strip('## Budget Range (USD): ').split(' - ')[0]) if tool_sections[2].strip('## Budget Range (USD): ').split(' - ')[0].isdigit() else 0,
                                    'maxBudget': int(tool_sections[2].strip('## Budget Range (USD): ').split(' - ')[1]) if len(tool_sections[2].strip('## Budget Range (USD): ').split(' - ')) > 1 and tool_sections[2].strip('## Budget Range (USD): ').split(' - ')[1].isdigit() else 0,
                                    'businessSize': [size.strip() for size in tool_sections[3].strip('## Business Size (small, medium, large): ').split(', ')],
                                    'complexity': tool_sections[4].strip('## Complexity Level: '),
                                    'features': [feature.strip() for feature in tool_sections[5].strip('## Key Features: ').split(', ')]
                                }
                                recommendations.append(tool)
                            except (IndexError, ValueError):
                                st.warning(f"Skipping recommendation due to invalid format: {tool_sections[0]}")
                                continue
                return recommendations
    except Exception as e:
        st.error(f"Error fetching recommendations: {str(e)}")
        return None

def main():
    st.title("🤖 AI Tool Recommender")

    if 'api_key' not in st.session_state:
        st.session_state.api_key = ''
    
    with st.sidebar:
        api_key = st.text_input("🔑 API Key", type="password", value=st.session_state.api_key)
    
    if api_key:
        st.session_state.api_key = api_key
        client = Anthropic(api_key=api_key)
        
        with st.form("tool_recommendation_form"):
            st.write("### 📋 Fill out the form to get personalized AI tool recommendations")
            
            business_size = st.selectbox("🏢 Business Size", ["small", "medium", "large"])
            budget = st.number_input("💵 Monthly Budget (USD)", min_value=0, value=100)
            category = st.selectbox("📊 Tool Category", ["marketing_automation", "content_creation", "analytics", "crm"])
            complexity = st.selectbox("⚙️ Complexity", ["easy", "moderate", "complex"])
            requirements = st.text_area("📝 Specific Requirements", placeholder="Describe your needs...")

            submitted = st.form_submit_button("🔍 Get Recommendations")

        if submitted:
            form_data = {
                'businessSize': business_size,
                'budget': budget,
                'category': category,
                'complexity': complexity,
                'requirements': requirements
            }

            recommendations = get_claude_recommendations(client, form_data)

            if recommendations:
                st.write("## 🎯 Recommended Tools for You")
                for idx, tool in enumerate(recommendations):
                    st.markdown(format_tool_section(tool, idx == 0), unsafe_allow_html=True)

    else:
        st.warning("⚠️ Please enter your API key")

if __name__ == "__main__":
    main()
