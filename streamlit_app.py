import streamlit as st
import json
from anthropic import Anthropic
import time
import random

def analyze_with_claude(client, data, max_retries=3):
   prompt = f"""Based on these requirements:
Business Size: {data['business_size']}
Budget: ${data['budget']}
Category: {data['category']}
Complexity: {data['complexity']}
Requirements: {data['requirements']}

Provide 3 most relevant AI tool recommendations. For each tool include:
1. Name
2. Brief description
3. Pricing 
4. Target users
5. 3-4 key features
6. 2-3 pros
7. 2-3 cons 
8. Match score (0-100)
9. Website URL

Format as JSON with this structure:
{{"recommendations": [
 {{
   "name": "",
   "description": "",
   "pricing": "",
   "bestFor": "",
   "keyFeatures": [],
   "pros": [],
   "cons": [],
   "matchScore": 0,
   "websiteUrl": ""
 }}
]}}"""

   for attempt in range(max_retries):
       try:
           st.info(f"Attempt {attempt + 1} of {max_retries}...")
           response = client.beta.messages.create(
               model="claude-3-opus-20240229",
               messages=[{"role": "user", "content": prompt}],
               temperature=0.7,
               max_tokens=2000
           )
           try:
               return json.loads(response.content)
           except json.JSONDecodeError:
               st.error("Error parsing Claude's response. Retrying...")
               continue
               
       except Exception as e:
           if "overloaded" in str(e).lower():
               if attempt < max_retries - 1:
                   wait_time = (attempt + 1) * 3 + random.uniform(1, 3)
                   st.warning(f"Server busy. Waiting {wait_time:.1f} seconds before retry...")
                   time.sleep(wait_time)
                   continue
               else:
                   st.error("Server overloaded. Please try again in a few minutes.")
           else:
               st.error(f"Error: {str(e)}")
           return None
           
def display_recommendations(results):
   if not results or 'recommendations' not in results:
       st.error("No recommendations available")
       return
       
   for tool in results['recommendations']:
       with st.container():
           col1, col2 = st.columns([3, 1])
           
           with col1:
               st.subheader(tool['name'])
               st.write(tool['description'])
               st.write(f"**Best For:** {tool['bestFor']}")
               
               with st.expander("Details"):
                   st.write("**Key Features:**")
                   for feature in tool['keyFeatures']:
                       st.write(f"- {feature}")
                   
                   col3, col4 = st.columns(2)
                   with col3:
                       st.write("**Pros:**")
                       for pro in tool['pros']:
                           st.write(f"+ {pro}")
                   with col4:
                       st.write("**Cons:**")
                       for con in tool['cons']:
                           st.write(f"- {con}")
           
           with col2:
               st.metric("Match Score", f"{tool['matchScore']}%")
               st.write(f"**Pricing:** {tool['pricing']}")
               st.link_button("Visit Website", tool['websiteUrl'])
               
           st.divider()

def main():
   st.title("AI Tool Recommender")
   
   # Persistent API key using session state
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
               step=50
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
               data = {
                   "business_size": business_size,
                   "budget": budget,
                   "category": category,
                   "complexity": complexity,
                   "requirements": requirements
               }
               
               with st.spinner("Analyzing your requirements..."):
                   results = analyze_with_claude(client, data)
                   if results:
                       display_recommendations(results)
   else:
       st.warning("Please enter your Anthropic API key to continue")

if __name__ == "__main__":
   main()
