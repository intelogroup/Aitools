import streamlit as st
from anthropic import Anthropic
import time
import random

st.set_page_config(page_title="AI Tool Recommender", layout="wide")

# Enhanced styling using Streamlit native components
def get_icon(category):
    return {
        "Marketing Automation": "🎯",
        "Content Creation": "✍️",
        "Analytics": "📊",
        "CRM": "👥",
        "Project Management": "📋",
        "Customer Service": "💬",
        "Sales": "💰",
        "Other": "🔧"
    }.get(category, "🛠️")

# Formatting each section of the tool recommendation
def format_tool_section(section_text, section_title, icon):
    section_content = section_text.split('\n', 1)[1].strip()
    if section_title == "Match Score":
        score = int(section_content.split('%')[0].strip())
        return f"**{icon} {section_title}:** {score}%"
    elif section_title == "Features":
        features = section_content.split('- ')[1:]
        return f"**{icon} {section_title}:**\n- " + '\n- '.join(features)
    elif section_title == "Pros/Cons":
        pros = [line.strip() for line in section_content.splitlines() if line.startswith("✓")]
        cons = [line.strip() for line in section_content.splitlines() if line.startswith("×")]
        pros_list = "\n- ".join(pros)
        cons_list = "\n- ".join(cons)
        return f"**{icon} Pros:**\n- {pros_list}\n\n**{icon} Cons:**\n- {cons_list}"
    else:
        return f"**{icon} {section_title}:** {section_content}"

# Analyzing tools and rendering cards
def analyze_tools(client, data):
    prompt = f"""Recommend 3 AI tools based on:
- Business: {data['business_size']}
- Budget: ${data['budget']}
- Category: {data['category']}
- Complexity: {data['complexity']}
- Needs: {data['requirements']}

Format as:
# Tool Name
## Match Score
[0-100]%
## Description
[text]
## Pricing
[details]
## Features
- [feature]
## Pros/Cons
✓ [pro]
× [con]"""

    try:
        with st.spinner("🔍 Analyzing your requirements..."):
            response = client.beta.messages.create(
                model="claude-3-opus-20240229",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )
            
            if hasattr(response, 'content'):
                content = ''.join([block.text for block in response.content]) if isinstance(response.content, list) else response.content
                
                # Split content into individual tools
                tools = content.split('# ')[1:]
                
                for tool in tools:
                    sections = tool.split('##')
                    tool_name = sections[0].strip()

                    # Display the tool information with icons and better formatting
                    st.markdown(f"### {get_icon(data['category'])} {tool_name}")
                    for section in sections[1:]:
                        section_title = section.split('\n', 1)[0].strip()
                        icon = {
                            "Match Score": "🏅",
                            "Description": "📝",
                            "Pricing": "💵",
                            "Features": "🔧",
                            "Pros/Cons": "👍/👎"
                        }.get(section_title, "ℹ️")
                        st.markdown(format_tool_section(section, section_title, icon))
                    st.markdown("---")  # Divider between tools

                return True
                
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return False

# Main function with improved form and icons
def main():
    st.title("🤖 AI Tool Recommender")
    
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ''
    
    with st.sidebar:
        api_key = st.text_input("API Key:", type="password", value=st.session_state.api_key)
    
    if api_key:
        st.session_state.api_key = api_key
        client = Anthropic(api_key=api_key)
        
        with st.form("recommend_form"):
            c1, c2 = st.columns(2)
            with c1:
                size = st.selectbox("📈 Business Size", 
                    ["Startup (1-10)", "Small (11-50)", "Medium (51-500)", "Large (500+)"],
                    key="size")
                budget = st.number_input("💵 Budget (USD)", min_value=0, value=100, step=50, key="budget")
            
            with c2:
                category = st.selectbox("📊 Category",
                    ["Marketing Automation", "Content Creation", "Analytics", "CRM", 
                     "Project Management", "Customer Service", "Sales", "Other"],
                    key="category")
                complexity = st.select_slider("⚙️ Complexity",
                    ["Beginner", "Intermediate", "Advanced"], key="complexity")
            
            requirements = st.text_area("📝 Requirements", key="reqs", 
                placeholder="Describe your needs...")

            if st.form_submit_button("🔍 Get Recommendations"):
                analyze_tools(client, {
                    "business_size": size,
                    "budget": budget,
                    "category": category,
                    "complexity": complexity,
                    "requirements": requirements
                })
    else:
        st.warning("⚠️ Please enter your API key")

if __name__ == "__main__":
    main()
