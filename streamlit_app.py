import streamlit as st
import random
from anthropic import Anthropic

# Set page layout and title
st.set_page_config(page_title="AI Tool Recommender", layout="wide")

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

# Format tool section for display
def format_tool_section(tool, is_best_match):
    # Safely access dictionary keys using get() with default values
    tool_icon = get_icon(tool.get('category', 'unknown'))
    budget_icon = "💰"
    business_size_icons = " ".join([get_icon(size) for size in tool.get('businessSize', [])])
    complexity_icon = get_icon(tool.get('complexity', 'unknown'))
    
    return f"""
    <div style="border: 2px solid {'#4CAF50' if is_best_match else '#e0e0e0'}; border-radius: 10px; padding: 15px; margin-bottom: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
        <h3 style="font-size: 22px; font-weight: bold;">{tool_icon} {tool.get('name', 'Unknown Tool')}</h3>
        <p><strong>{budget_icon} Budget Range:</strong> ${tool.get('minBudget', 0)} - ${tool.get('maxBudget', 0)}</p>
        <p><strong>🏢 Business Size:</strong> {business_size_icons}</p>
        <p><strong>{complexity_icon} Complexity:</strong> {tool.get('complexity', 'Unknown').capitalize()}</p>
        <p><strong>🛠️ Features:</strong> {', '.join(tool.get('features', ['No features available']))}</p>
        <p style="color: {'#4CAF50' if is_best_match else '#000'}; font-weight: bold;">Match Score: {tool.get('score', 0)}%</p>
    </div>
    """

# Communicate with Claude AI to get recommendations
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
            
            # Parse the response content
            if hasattr(response, 'content'):
                return ''.join([block.text for block in response.content]) if isinstance(response.content, list) else response.content
    except Exception as e:
        st.error(f"Error fetching recommendations: {str(e)}")
        return None

# Main function to render the app
def main():
    st.title("🤖 AI Tool Recommender")

    if 'api_key' not in st.session_state:
        st.session_state.api_key = ''
    
    with st.sidebar:
        api_key = st.text_input("🔑 API Key", type="password", value=st.session_state.api_key)
    
    if api_key:
        st.session_state.api_key = api_key
        client = Anthropic(api_key=api_key)
        
        # Input form
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

            # Get recommendations from Claude AI
            recommendations = get_claude_recommendations(client, form_data)

            if recommendations:
                # Split recommendations based on Claude response format
                tools = recommendations.split("# ")[1:]

                st.write("## 🎯 Recommended Tools for You")
                for idx, tool_text in enumerate(tools):
                    tool_sections = tool_text.split('##')
                    tool_name = tool_sections[0].strip()
                    is_best_match = idx == 0

                    # Example mock-up, split tool response sections as needed
                    tool = {
                        'name': tool_name,
                        'score': random.randint(80, 100),  # Mocked match score
                        'minBudget': random.randint(0, 100),
                        'maxBudget': random.randint(100, 1000),
                        'businessSize': ["small", "medium", "large"],
                        'features': ["Email Automation", "CRM", "Advanced Analytics"],
                        'complexity': form_data['complexity']
                    }

                    st.markdown(format_tool_section(tool, is_best_match), unsafe_allow_html=True)

    else:
        st.warning("⚠️ Please enter your API key")

if __name__ == "__main__":
    main()

