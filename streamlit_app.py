import streamlit as st
import random
from anthropic import Anthropic

# Set page layout and title
st.set_page_config(page_title="AI Tool Recommender", layout="wide")

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
    ## Pros and Cons
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
                return ''.join([block.text for block in response.content]) if isinstance(response.content, list) else response.content
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
                tools = recommendations.split("# ")[1:]

                st.write("## 🎯 Recommended Tools for You")
                for tool_text in tools:
                    tool_sections = tool_text.split('##')
                    tool_name = tool_sections[0].strip()
                    tool_score = int(tool_sections[1].strip().split(" ")[0])
                    tool_budget = tool_sections[2].strip().split(" ")[2:]
                    tool_business_size = tool_sections[3].strip().split(" ")[2:]
                    tool_complexity = tool_sections[4].strip().split(" ")[1]
                    tool_features = [feature.strip() for feature in tool_sections[5].strip().split(":")[1].split(",")]

                    tool = {
                        'name': tool_name,
                        'score': tool_score,
                        'minBudget': int(tool_budget[0]),
                        'maxBudget': int(tool_budget[2]),
                        'businessSize': tool_business_size,
                        'complexity': tool_complexity,
                        'features': tool_features
                    }

                    st.markdown(format_tool_section(tool, False), unsafe_allow_html=True)

    else:
        st.warning("⚠️ Please enter your API key")

if __name__ == "__main__":
    main()
