import streamlit as st
import json
from anthropic import Anthropic

st.set_page_config(page_title="AI Tool Recommender", layout="wide")

def get_recommendations(client, data):
   try:
       prompt = f"""Analyze these requirements and suggest AI tools:
Business Size: {data['business_size']}
Budget: ${data['budget']}
Category: {data['category']}
Complexity: {data['complexity']}
Requirements: {data['requirements']}

Provide 3 recommendations in JSON with:
- name
- description 
- pricing
- bestFor
- keyFeatures (list)
- pros (list) 
- cons (list)
- matchScore (0-100)
- websiteUrl"""

       response = client.beta.messages.create(
           model="claude-3-opus-20240229",
           max_tokens=2000,
           messages=[{"role": "user", "content": prompt}],
           temperature=0.7
       )
       return json.loads(response.content)
   except Exception as e:
       st.error(f"Error: {str(e)}")
       return None

def display_tool(tool):
   col1, col2 = st.columns([3, 1])
   with col1:
       st.subheader(tool['name'])
       st.write(tool['description'])
       with st.expander("Features & Details"):
           st.write("**Key Features:**")
           for feature in tool['keyFeatures']:
               st.write(f"• {feature}")
           
           cols = st.columns(2)
           with cols[0]:
               st.write("**Pros:**")
               for pro in tool['pros']:
                   st.write(f"✓ {pro}")
           with cols[1]:
               st.write("**Cons:**")
               for con in tool['cons']:
                   st.write(f"× {con}")
   
   with col2:
       st.metric("Match Score", f"{tool['matchScore']}%")
       st.write(f"**Pricing:** {tool['pricing']}")
       if 'websiteUrl' in tool:
           st.link_button("Visit Website", tool['websiteUrl'])
   st.divider()

def main():
   st.title("AI Tool Recommender")
   
   api_key = st.text_input("Enter your Anthropic API Key:", type="password")
   if not api_key:
       st.warning("Please enter your Anthropic API key to continue")
       st.stop()
       
   try:
       client = Anthropic(api_key=api_key)
   except Exception as e:
       st.error("Invalid API key")
       st.stop()

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
           with st.spinner("Analyzing requirements..."):
               data = {
                   "business_size": business_size,
                   "budget": budget,
                   "category": category,
                   "complexity": complexity,
                   "requirements": requirements
               }
               
               results = get_recommendations(client, data)
               if results and 'recommendations' in results:
                   for tool in results['recommendations']:
                       display_tool(tool)

if __name__ == "__main__":
   main()
