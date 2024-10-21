import streamlit as st
from anthropic import Anthropic
import time
import random
import pandas as pd
from datetime import datetime

def analyze_with_claude(client, data, max_retries=3):
   prompt = f"""Based on these requirements, recommend 3 AI tools:
Business Size: {data['business_size']}
Budget: ${data['budget']}
Category: {data['category']}
Complexity: {data['complexity']}
Requirements: {data['requirements']}

Return recommendations in markdown format with:
# [Tool Name] (Match Score: X%)
## Description
[Description]
## Pricing & Budget
[Pricing details]
## Best For
[Target users]
## Key Features
- Feature 1
- Feature 2
## Pros & Cons
✓ [Pro 1]
✓ [Pro 2]
× [Con 1]
× [Con 2]"""

   for attempt in range(max_retries):
       try:
           with st.status("Analyzing requirements...") as status:
               status.update(label="Querying AI...", expanded=True)
               response = client.beta.messages.create(
                   model="claude-3-opus-20240229",
                   messages=[{"role": "user", "content": prompt}],
                   temperature=0.7,
                   max_tokens=2000
               )
               
               if hasattr(response, 'content'):
                   analysis = ''.join([block.text for block in response.content]) if isinstance(response.content, list) else response.content
                   status.update(label="Processing results...", state="running")
                   
                   # Store recommendations in session state
                   if 'recommendations' not in st.session_state:
                       st.session_state.recommendations = []
                   
                   # Parse and store recommendations
                   tools = []
                   for rec in analysis.split('# ')[1:]:
                       tool = parse_recommendation(rec)
                       if tool:
                           tools.append(tool)
                   
                   st.session_state.recommendations = tools
                   status.update(label="✅ Analysis complete!", state="complete")
                   
                   display_recommendations(tools)
                   return True

       except Exception as e:
           handle_error(e, attempt, max_retries)
   return False

def parse_recommendation(rec_text):
   try:
       lines = rec_text.split('\n')
       name = lines[0].split('(Match Score:')[0].strip()
       score = int(lines[0].split('Match Score:')[1].strip('%) '))
       
       sections = {'description': '', 'pricing': '', 'best_for': '', 
                  'features': [], 'pros': [], 'cons': []}
       
       current_section = None
       for line in lines[1:]:
           if line.startswith('## '):
               current_section = line[3:].lower().strip()
           elif line.strip() and current_section:
               if line.startswith('- '):
                   sections['features'].append(line[2:])
               elif line.startswith('✓ '):
                   sections['pros'].append(line[2:])
               elif line.startswith('× '):
                   sections['cons'].append(line[2:])
               else:
                   sections[current_section] = line.strip()
       
       return {
           'name': name,
           'score': score,
           **sections
       }
   except:
       return None

def display_recommendations(tools, sort_by='score'):
   if not tools:
       return
   
   # Sorting options
   sort_options = {
       'score': 'Match Score',
       'name': 'Name',
       'pricing': 'Pricing'
   }
   
   col1, col2, col3 = st.columns([2,2,1])
   with col1:
       sort_by = st.selectbox('Sort by:', list(sort_options.values()))
   with col2:
       price_filter = st.slider('Price Range ($)', 0, 1000, (0, 1000))
   with col3:
       st.download_button(
           "Export Results",
           export_recommendations(tools),
           "ai_tools.csv",
           "text/csv"
       )

   # Create comparison view
   if st.toggle('Compare Tools'):
       show_comparison_view(tools)
   
   # Display individual cards
   for tool in sorted(tools, key=lambda x: x['score'], reverse=True):
       with st.container():
           create_tool_card(tool)

def create_tool_card(tool):
   with st.container():
       col1, col2 = st.columns([3,1])
       
       with col1:
           st.markdown(f"""
           <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px;'>
               <h3>{tool['name']}</h3>
               <p>{tool['description']}</p>
           </div>
           """, unsafe_allow_html=True)
           
       with col2:
           st.metric("Match Score", f"{tool['score']}%")
       
       with st.expander("Details"):
           tcol1, tcol2 = st.columns(2)
           
           with tcol1:
               st.write("**Key Features**")
               for f in tool['features']:
                   st.markdown(f"• {f}")
                   
               st.write("**Best For**")
               st.write(tool['best_for'])
               
           with tcol2:
               st.write("**Pros**")
               for p in tool['pros']:
                   st.markdown(f"✓ {p}")
                   
               st.write("**Cons**")
               for c in tool['cons']:
                   st.markdown(f"× {c}")

def show_comparison_view(tools):
   comparison_df = pd.DataFrame([{
       'Tool': t['name'],
       'Score': t['score'],
       'Pricing': t['pricing'],
       'Features': len(t['features']),
       'Pros': len(t['pros']),
       'Cons': len(t['cons'])
   } for t in tools])
   
   st.dataframe(
       comparison_df.set_index('Tool'),
       use_container_width=True,
       hide_index=False
   )

def export_recommendations(tools):
   df = pd.DataFrame(tools)
   return df.to_csv(index=False)

def handle_error(error, attempt, max_retries):
   if "overloaded" in str(error).lower():
       if attempt < max_retries - 1:
           wait_time = (attempt + 1) * 3 + random.uniform(1, 3)
           st.warning(f"Service busy. Retrying in {wait_time:.1f} seconds...")
           time.sleep(wait_time)
       else:
           st.error("Service temporarily unavailable. Please try again later.")
   else:
       st.error(f"Error: {str(error)}")

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
                   ["Startup (1-10)", "Small (11-50)", "Medium (51-500)", "Large (500+)"]
               )
               
               budget = st.number_input(
                   "Monthly Budget (USD)",
                   min_value=0,
                   max_value=10000,
                   step=50,
                   value=100
               )
           
           with col2:
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
       st.warning("Please enter your API key in the sidebar to continue")

if __name__ == "__main__":
   main()
