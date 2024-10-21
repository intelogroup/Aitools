import streamlit as st
import random
import time
from anthropic import Anthropic

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

def format_full_tool_card(tool_text, is_best_match):
    """Formats the full recommendation from Claude AI into a single card."""
    return f"""
    <div style="border: 2px solid {'#4CAF50' if is_best_match else '#e0e0e0'}; border-radius: 10px; padding: 15px; margin-bottom: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
        <p style="white-space: pre-wrap; font-size: 18px;">{tool_text}</p>
    </div>
    """

def get_claude_recommendations(client, form_data, max_retries=3, delay=5):
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

                if hasattr(response, 'content'):
                    return ''.join([block.text for block in response.content]) if isinstance(response.content, list) else response.content

        except Exception as e:
            if 'overloaded' in str(e).lower() and attempt < max_retries - 1:
                st.warning(f"Server overloaded, retrying in {delay} seconds... ({attempt+1}/{max_retries})")
                time.sleep(delay)
            else:
                st.error(f"Error fetching recommendations: {str(e)}")
                return None

def render_form():
    """Renders the form for user input and returns the filled data."""
    with st.form("tool_recommendation_form"):
        st.write("### 📋 Fill out the form to get personalized AI tool recommendations")

        business_size = st.selectbox("🏢 Business Size", ["small", "medium", "large"])
        budget = st.number_input("💵 Monthly Budget (USD)", min_value=0, value=100)
        category = st.selectbox("📊 Tool Category", ["marketing_automation", "content_creation", "analytics", "crm"])
        complexity = st.selectbox("⚙️ Complexity", ["easy", "moderate", "complex"])
        requirements = st.text_area("📝 Specific Requirements", placeholder="Describe your needs...")

        submitted = st.form_submit_button("🔍 Get Recommendations")

    if submitted:
        return {
            'businessSize': business_size,
            'budget': budget,
            'category': category,
            'complexity': complexity,
            'requirements': requirements
        }
    return None

def display_recommendations(recommendations):
    """Displays the recommendations received from Claude AI in a single card per tool."""
    if recommendations:
        tools = recommendations.split("# ")[1:]  # Each recommendation starts with "# "
        st.write("## 🎯 Recommended Tools for You")

        for idx, tool_text in enumerate(tools):
            is_best_match = idx == 0  # Highlight the first recommendation as the best match

            # Display the full recommendation as one card
            st.markdown(format_full_tool_card(tool_text, is_best_match), unsafe_allow_html=True)

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
        form_data = render_form()

        if form_data:
            # Get recommendations from Claude AI
            recommendations = get_claude_recommendations(client, form_data)

            # Display recommendations
            display_recommendations(recommendations)

    else:
        st.warning("⚠️ Please enter your API key")

if __name__ == "__main__":
    main()
