import streamlit as st
from anthropic import Anthropic
import random
import time

# Set page layout and title
st.set_page_config(page_title="AI Tool Recommender", layout="wide")

# Icons dictionary to represent attributes
ICON_MAP = {
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
}

def get_icon(attribute):
    """Returns the icon corresponding to the provided attribute."""
    return ICON_MAP.get(attribute, "🔧")

def format_tool_card(tool):
    """Formats a single tool's details into a single card/block for display."""
    tool_icon = get_icon(tool.get('category', 'unknown'))
    budget_icon = "💰"
    business_size_icons = " ".join([get_icon(size) for size in tool.get('businessSize', [])])
    complexity_icon = get_icon(tool.get('complexity', 'unknown'))

    return f"""
    <div style="border: 2px solid #e0e0e0; border-radius: 10px; padding: 15px; margin-bottom: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
        <h3 style="font-size: 22px; font-weight: bold;">{tool_icon} {tool.get('name', 'Unknown Tool')}</h3>
        <p><strong>{budget_icon} Budget Range:</strong> ${tool.get('minBudget', 0)} - ${tool.get('maxBudget', 0)}</p>
        <p><strong>🏢 Business Size:</strong> {business_size_icons}</p>
        <p><strong>{complexity_icon} Complexity:</strong> {tool.get('complexity', 'Unknown').capitalize()}</p>
        <p><strong>🛠️ Features:</strong> {', '.join(tool.get('features', ['No features available']))}</p>
        <p><strong>👍 Pros:</strong> {', '.join(tool.get('pros', ['No pros available']))}</p>
        <p><strong>👎 Cons:</strong> {', '.join(tool.get('cons', ['No cons available']))}</p>
        <p style="color: #000; font-weight: bold;">Match Score: {tool.get('score', 0)}%</p>
    </div>
    """

def analyze_with_claude(client, form_data, max_retries=3, delay=5):
    """Fetches recommendations from Claude AI, with retry logic for handling overload errors."""
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

    for attempt in range(max_retries):
        try:
            with st.spinner("🔍 Analyzing your requirements..."):
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

def main():
    st.title("🤖 AI Tool Recommender")

    # Secure API key input
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ''

    with st.sidebar:
        api_key = st.text_input("🔑 API Key", type="password", value=st.session_state.api_key)

    if api_key:
        st.session_state.api_key = api_key
        client = Anthropic(api_key=api_key)

        # Render form and fetch input data
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
            analyze_with_claude(client, form_data)

    else:
        st.warning("⚠️ Please enter your API key")

if __name__ == "__main__":
    main()
