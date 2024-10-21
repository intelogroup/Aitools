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

                # Check if response has content
                if hasattr(response, 'content'):
                    return response.content

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

def display_recommendations(recommendations, form_data):
    """Displays the recommendations received from Claude AI."""
    if recommendations:
        tools = recommendations.split("# ")  # Split by the tool separator
        st.write("## 🎯 Recommended Tools for You")

        for tool_text in tools[1:]:  # Ignore the first split element, as it's empty
            tool_sections = tool_text.split('##')

            # Parse the sections based on Claude's response format
            tool_name = tool_sections[0].strip()
            match_score = tool_sections[1].strip().split(":")[-1].strip() if len(tool_sections) > 1 else "Not available"
            budget_range = tool_sections[2].strip() if len(tool_sections) > 2 else "Not available"
            business_size = tool_sections[3].strip() if len(tool_sections) > 3 else "Not available"
            complexity_level = tool_sections[4].strip() if len(tool_sections) > 4 else "Not available"
            features = tool_sections[5].strip().split(", ") if len(tool_sections) > 5 else ["No features available"]
            pros = ["No pros available"]
            cons = ["No cons available"]

            # Construct tool dictionary to display
            tool = {
                'name': tool_name,
                'score': match_score,
                'minBudget': random.randint(0, 100),  # Mock-up value
                'maxBudget': random.randint(100, 1000),  # Mock-up value
                'businessSize': ["small", "medium", "large"],  # Simplified
                'features': features,
                'pros': pros,
                'cons': cons,
                'complexity': complexity_level
            }

            # Display the tool in a block
            st.markdown(format_tool_card(tool), unsafe_allow_html=True)

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
            if recommendations:
                display_recommendations(recommendations, form_data)

    else:
        st.warning("⚠️ Please enter your API key")

if __name__ == "__main__":
    main()
