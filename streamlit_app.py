import streamlit as st
from anthropic import Anthropic
import time
import random

st.set_page_config(page_title="AI Tool Recommender", layout="wide")

# Enhanced styling
st.markdown("""
   <style>
       /* Main container */
       .main {
           padding: 20px;
       }
       
       /* Cards */
       .tool-card {
           background-color: #ffffff;
           border-radius: 15px;
           padding: 25px;
           box-shadow: 0 4px 8px rgba(0,0,0,0.1);
           margin: 20px 0;
           border-left: 5px solid #4CAF50;
       }
       
       /* Headers */
       .tool-name {
           color: #2c3e50;
           font-size: 24px;
           font-weight: bold;
           margin-bottom: 15px;
           display: flex;
           align-items: center;
       }
       
       /* Score section */
       .score-section {
           background-color: #f8f9fa;
           padding: 15px;
           border-radius: 10px;
           margin: 10px 0;
       }
       
       .score-bar {
           height: 12px;
           background-color: #e0e0e0;
           border-radius: 6px;
           margin: 8px 0;
       }
       
       .score-fill {
           height: 100%;
           border-radius: 6px;
           background: linear-gradient(90deg, #4CAF50, #45a049);
           transition: width 0.5s ease-in-out;
       }
       
       /* Features section */
       .features-list {
           background-color: #f1f8ff;
           padding: 15px;
           border-radius: 10px;
           margin: 10px 0;
       }
       
       /* Pros and Cons */
       .pros-cons {
           display: grid;
           grid-template-columns: 1fr 1fr;
           gap: 20px;
           margin: 15px 0;
       }
       
       .pros {
           color: #2ecc71;
       }
       
       .cons {
           color: #e74c3c;
       }
       
       /* Pricing section */
       .pricing {
           background-color: #fff3e0;
           padding: 15px;
           border-radius: 10px;
           margin: 10px 0;
       }
       
       /* Categories */
       .category-badge {
           background-color: #3498db;
           color: white;
           padding: 5px 10px;
           border-radius: 15px;
           font-size: 14px;
           margin-left: 10px;
       }
   </style>
""", unsafe_allow_html=True)

def get_icon(category):
   return {
       "Marketing Automation": "🎯",
       "Content Creation": "✍️",
       "Analytics": "📊",
       "CRM": "👥",
       "Project Management": "📋",
       "Customer Service": "💬",
       "Sales": "💰"
   }.get(category, "🔧")

def format_tool_section(section_text):
   """Format each section of the tool recommendation with enhanced styling"""
   if '## Match Score' in section_text:
       score = int(section_text.split('%')[0].split()[-1])
       return f"""
       <div class="score-section">
           <strong>Match Score:</strong> {score}%
           <div class="score-bar">
               <div class="score-fill" style="width: {score}%;"></div>
           </div>
       </div>
       """
   elif '## Features' in section_text:
       features = section_text.split('\n- ')[1:]
       feature_list = ''.join([f"<li>{f.strip()}</li>" for f in features])
       return f"""
       <div class="features-list">
           <strong>Key Features:</strong>
           <ul>{feature_list}</ul>
       </div>
       """
   elif '## Pros/Cons' in section_text:
       lines = section_text.split('\n')
       pros = [l[2:] for l in lines if l.startswith('✓')]
       cons = [l[2:] for l in lines if l.startswith('×')]
       return f"""
       <div class="pros-cons">
           <div>
               <strong class="pros">Pros:</strong>
               <ul>{''.join([f'<li class="pros">{p}</li>' for p in pros])}</ul>
           </div>
           <div>
               <strong class="cons">Cons:</strong>
               <ul>{''.join([f'<li class="cons">{c}</li>' for c in cons])}</ul>
           </div>
       </div>
       """
   elif '## Pricing' in section_text:
       pricing = section_text.replace('## Pricing\n', '')
       return f"""
       <div class="pricing">
           <strong>💰 Pricing:</strong><br>
           {pricing}
       </div>
       """
   else:
       return f"<p>{section_text.split('\n', 1)[1]}</p>"

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
                   
                   # Create styled card for each tool
                   st.markdown(f"""
                       <div class="tool-card">
                           <div class="tool-name">
                               {get_icon(data['category'])} {tool_name}
                               <span class="category-badge">{data['category']}</span>
                           </div>
                           {''.join([format_tool_section(section) for section in sections[1:]])}
                       </div>
                   """, unsafe_allow_html=True)
               
               return True
               
   except Exception as e:
       st.error(f"Error: {str(e)}")
       return False

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
               size = st.selectbox("Business Size", 
                   ["Startup (1-10)", "Small (11-50)", "Medium (51-500)", "Large (500+)"],
                   key="size")
               budget = st.number_input("Budget (USD)", min_value=0, value=100, step=50, key="budget")
           
           with c2:
               category = st.selectbox("Category",
                   ["Marketing Automation", "Content Creation", "Analytics", "CRM", 
                    "Project Management", "Customer Service", "Sales", "Other"],
                   key="category")
               complexity = st.select_slider("Complexity",
                   ["Beginner", "Intermediate", "Advanced"], key="complexity")
           
           requirements = st.text_area("Requirements", key="reqs", 
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
