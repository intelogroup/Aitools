import streamlit as st
from anthropic import Anthropic
import time
import random
from markdown2 import Markdown

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
           
           # Split the response into individual tool recommendations
           recommendations = response.content.split("\n# ")[1:]  # Split by tool headers
           
           for idx, rec in enumerate(recommendations, 1):
               with st.container():
                   # Create expandable section for each tool
                   with st.expander(f"Tool Recommendation #{idx}", expanded=True):
                       # Parse sections
                       sections = rec.split("\n## ")
                       tool_name = sections[0].strip()
                       
                       # Create two columns
                       col1, col2 = st.columns([2,1])
                       
                       with col1:
                           st.subheader(tool_name)
                           
                           # Process each section
                           for section in sections[1:]:
                               if section.startswith("Description"):
                                   st.write(section.replace("Description\n", ""))
                               elif section.startswith("Best suited for"):
                                   st.write("**Best For:**", section.replace("Best suited for\n", ""))
                               elif section.startswith("Key features"):
                                   st.write("**Key Features:**")
                                   features = section.replace("Key features\n", "").split("- ")[1:]
                                   for feature in features:
                                       st.write(f"• {feature.strip()}")
                       
                       with col2:
                           # Extract match score
                           for section in sections:
                               if section.startswith("Match score"):
                                   score = section.replace("Match score\n", "").strip()
                                   st.metric("Match Score", score)
                               elif section.startswith("Pricing"):
                                   st.write("**Pricing:**")
                                   st.write(section.replace("Pricing\n", ""))
                           
                       # Create two columns for pros and cons
                       col3, col4 = st.columns(2)
                       
                       with col3:
                           st.write("**Pros:**")
                           for section in sections:
                               if section.startswith("Pros"):
                                   pros = section.replace("Pros\n", "").split("- ")[1:]
                                   for pro in pros:
                                       st.write(f"✓ {pro.strip()}")
                                       
                       with col4:
                           st.write("**Cons:**")
                           for section in sections:
                               if section.startswith("Cons"):
                                   cons = section.replace("Cons\n", "").split("- ")[1:]
                                   for con in cons:
                                       st.write(f"✗ {con.strip()}")
                       
                       # Website URL at the bottom
                       for section in sections:
                           if section.startswith("Website URL"):
                               url = section.replace("Website URL\n", "").strip()
                               st.link_button("Visit Website", url)
                   
                   st.divider()
           
           return True
               
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
   st.title("AI Tool Recommender")
   
   if 'api_key' not in st.session_state:
       st.session_state.api_key = ''
   
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
               analyze_with_claude(client, {
                   "business_size": business_size,
                   "budget": budget,
                   "category": category,
                   "complexity": complexity,
                   "requirements": requirements
               })

   else:
       st.warning("Please enter your Anthropic API key to continue")

if __name__ == "__main__":
   main()
