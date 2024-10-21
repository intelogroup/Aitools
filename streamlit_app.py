import streamlit as st
from anthropic import Anthropic
import time
import random

# Add custom CSS
st.markdown("""
<style>
   .tool-card {
       background-color: #ffffff;
       border-radius: 10px;
       padding: 20px;
       box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
       margin-bottom: 20px;
   }
   .match-score {
       font-size: 24px;
       font-weight: bold;
       color: #0066cc;
   }
   .progress-bar {
       height: 10px;
       background-color: #e0e0e0;
       border-radius: 5px;
       margin: 5px 0;
   }
   .progress-fill {
       height: 100%;
       background-color: #4CAF50;
       border-radius: 5px;
       transition: width 0.5s ease-in-out;
   }
   .category-icon {
       font-size: 24px;
       margin-right: 10px;
   }
</style>
""", unsafe_allow_html=True)

def get_category_icon(category):
   icons = {
       "Marketing Automation": "🎯",
       "Content Creation": "✍️",
       "Analytics": "📊",
       "CRM": "👥",
       "Project Management": "📋",
       "Customer Service": "💬",
       "Sales": "💰",
       "Other": "🔧"
   }
   return icons.get(category, "🔧")

def render_progress_bar(score):
   return f"""
       <div class="progress-bar">
           <div class="progress-fill" style="width: {score}%"></div>
       </div>
   """

def analyze_with_claude(client, data, max_retries=3):
   prompt = f"""Based on these requirements, recommend 3 AI tools:
Business Size: {data['business_size']}
Budget: ${data['budget']}
Category: {data['category']}
Complexity: {data['complexity']}
Requirements: {data['requirements']}

Format each recommendation as markdown with:
# Tool Name
## Description
[Description]
## Match Score
[0-100]%
## Pricing
[Price details]
## Best For
[Target users]
## Key Features
- [Feature 1]
- [Feature 2]
## Pros
✓ [Pro 1]
✓ [Pro 2]
## Cons
× [Con 1]
× [Con 2]"""

   for attempt in range(max_retries):
       try:
           with st.spinner("Analyzing requirements..."):
               response = client.beta.messages.create(
                   model="claude-3-opus-20240229",
                   messages=[{"role": "user", "content": prompt}],
                   temperature=0.7,
                   max_tokens=2000
               )
               
               if hasattr(response, 'content'):
                   recommendations = ''.join([block.text for block in response.content]) if isinstance(response.content, list) else response.content
                   
                   # Split into individual recommendations
                   tools = recommendations.split('# ')[1:]
                   
                   # Display each recommendation with styling
                   for tool in tools:
                       sections = tool.split('##')
                       name = sections[0].strip()
                       
                       # Extract match score
                       score = 0
                       for section in sections:
                           if 'Match Score' in section:
                               try:
                                   score = int(section.split('%')[0].strip().split()[-1])
                               except:
                                   pass
                       
                       st.markdown(f"""
                           <div class="tool-card">
                               <h3>
                                   <span class="category-icon">{get_category_icon(data['category'])}</span>
                                   {name}
                               </h3>
                               <div class="match-score">Match Score: {score}%</div>
                               {render_progress_bar(score)}
                           </div>
                       """, unsafe_allow_html=True)
                       
                       # Display remaining content
                       for section in sections[1:]:
                           if 'Match Score' not in section:
                               st.markdown(f"## {section}")
                   
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
   st.set_page_config(page_title="AI Tool Recommender", layout="wide")
   
   st.title("🤖 AI Tool Recommender")
   
   if 'api_key' not in st.session_state:
       st.session_state.api_key = ''
   
   with st.sidebar:
       api_key = st.text_input("Enter Anthropic API Key:", 
                              value=st.session_state.api_key,
                              type="password")
                              
   if api_key:
       st.session_state.api_key = api_key
       client = Anthropic(api_key=api_key)
       
       with st.form("recommendation_form"):
           col1, col2 = st.columns(2)
           
           with col1:
               business_size = st.selectbox(
                   "Business Size",
                   ["Startup (1-10)", "Small (11-50)", "Medium (51-500)", "Large (500+)"],
                   key="business_size_select"
               )
               
               budget = st.number_input(
                   "Monthly Budget (USD)",
                   min_value=0,
                   max_value=10000,
                   step=50,
                   value=100,
                   key="budget_input"
               )
           
           with col2:
               category = st.selectbox(
                   "Tool Category",
                   ["Marketing Automation", "Content Creation", "Analytics", "CRM", 
                    "Project Management", "Customer Service", "Sales", "Other"],
                   key="category_select"
               )
               
               complexity = st.select_slider(
                   "Technical Complexity",
                   options=["Beginner", "Intermediate", "Advanced"],
                   key="complexity_slider"
               )
           
           requirements = st.text_area(
               "Specific Requirements",
               placeholder="Describe your needs...",
               key="requirements_area"
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
       st.warning("Please enter your API key in the sidebar to continue")

if __name__ == "__main__":
   main()
