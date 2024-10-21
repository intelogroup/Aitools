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

# Function to get icons for categories
def get_icon(attribute):
    """Returns the icon corresponding to the provided attribute."""
    return ICON_MAP.get(attribute, "🔧")

# Function to format each tool into a card/block
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
        <p><strong>🔗 Website URL:</strong> {tool.get('url', 'No URL available')}</p>
    </div>
    """

# Function to fetch recommendations from Claude AI
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
            
            # Handle the response content
            if hasattr(response, 'content'):
                if isinstance(response.content, list):
                    analysis = ''.join([block.text for block in response.content])
                else:
                    analysis = response.content
                
                return analysis
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

# Function to display the recommendations in the desired format
def display_recommendations(recommendations):
    """Displays the recommendations based on the structured format."""
    if recommendations:
        tools = recommendations.split("# ")
        st.write("## 🎯 Recommended Tools for You")

        for tool_text in tools[1:]:
            tool_sections = tool_text.split("##")

            tool_name = tool_sections[0].strip()
            description = tool_sections[1].strip() if len(tool_sections) > 1 else "No description available"
            pricing = tool_sections[2].strip() if len(tool_sections) > 2 else "Pricing not available"
            target_users = tool_sections[3].strip() if len(tool_sections) > 3 else "Target users not available"
            features = tool_sections[4].strip().split(", ") if len(tool_sections) > 4 else ["No features available"]
            pros = tool_sections[5].strip().split(", ") if len(tool_sections) > 5 else ["No pros available"]
            cons = tool_sections[6].strip().split(", ") if len(tool_sections) > 6 else ["No cons available"]
            match_score = tool_sections[7].strip().split(":")[-1].strip() if len(tool_sections) > 7 else "0"
            url = tool_sections[8].strip() if len(tool_sections) > 8 else "No URL available"

            # Create the tool dictionary
            tool = {
                'name': tool_name,
                'description': description,
                'minBudget': random.randint(10, 100),
                'maxBudget': random.randint(100, 500),
                'businessSize': ["small", "medium", "large"],
                'features': features,
                'pros': pros,
                'cons': cons,
                'score': match_score,
                'url': url,
                'complexity': "easy"  # Example
            }

            # Render each tool in a single card
            st.markdown(format_tool_card(tool), unsafe_allow_html=True)
    else:
        st.warning("No recommendations available.")

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
                recommendations = analyze_with_claude(client, {
                    "business_size": business_size,
                    "budget": budget,
                    "category": category,
                    "complexity": complexity,
                    "requirements": requirements
                })

                # Display the recommendations
                display_recommendations(recommendations)

    else:
        st.warning("Please enter your Anthropic API key to continue")

# Run the app
if __name__ == "__main__":
    main()
