import streamlit as st
import json
from anthropic import Anthropic
import time
import random

def analyze_with_claude(client, data, max_retries=3):
   prompt = f"""For educational purposes, I need help analyzing and recommending AI tools based on these requirements:

Business Size: {data['business_size']}
Budget: ${data['budget']}
Category: {data['category']}
Complexity: {data['complexity']}
Requirements: {data['requirements']}

Please provide 3 AI tool recommendations. Give detailed, educational explanations about each tool to help users learn about available options.

Return your response in this exact JSON format:
{{
 "recommendations": [
   {{
     "name": "Tool Name",
     "description": "Detailed educational description",
     "pricing": "Detailed pricing information",
     "bestFor": "Who this tool is best suited for",
     "keyFeatures": ["feature1", "feature2", "feature3"],
     "pros": ["pro1", "pro2", "pro3"],
     "cons": ["con1", "con2"],
     "matchScore": 95,
     "websiteUrl": "https://example.com"
   }}
 ]
}}

Please ensure your response:
1. Is in valid JSON format
2. Includes exactly 3 recommendations
3. Has all the fields specified above
4. Contains educational details that help users understand each tool
5. Focuses on tools appropriate for learning and education

Remember this is for educational purposes to help users learn about AI tools."""

   for attempt in range(max_retries):
       try:
           st.info(f"Attempt {attempt + 1} of {max_retries}...")
           response = client.beta.messages.create(
               model="claude-3-opus-20240229",
               messages=[{
                   "role": "user", 
                   "content": prompt
               }],
               temperature=0.7,
               max_tokens=2000
           )
           
           try:
               # Extract content and parse JSON
               content = response.content
               if isinstance(content, str):
                   # Find JSON object in response if it exists
                   try:
                       json_start = content.find('{')
                       json_end = content.rfind('}') + 1
                       if json_start >= 0 and json_end > 0:
                           json_str = content[json_start:json_end]
                           return json.loads(json_str)
                   except:
                       st.error("Could not find valid JSON in response")
                       return None
               else:
                   st.error("Invalid response format")
                   return None
                   
           except Exception as e:
               st.error(f"Error parsing response: {str(e)}")
               if attempt < max_retries - 1:
                   continue
               return None
               
       except Exception as e:
           if "overloaded" in str(e).lower():
               if attempt < max_retries - 1:
                   wait_time = (attempt + 1) * 3 + random.uniform(1, 3)
                   st.warning(f"Server busy. Waiting {wait_time:.1f} seconds...")
                   time.sleep(wait_time)
                   continue
               else:
                   st.error("Server overloaded. Please try again later.")
           else:
               st.error(f"Error: {str(e)}")
           return None

def main():
   st.title("AI Tool Recommender (Educational)")
   st.markdown("""
   This tool helps you learn about and discover AI tools based on your requirements.
   Enter your details below to get educational recommendations.
   """)
   
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
               placeholder="Describe what you're looking to learn and achieve..."
           )
           
           submitted = st.form_submit_button("Get Educational Recommendations")
           
           if submitted:
               with st.spinner("Analyzing your requirements and preparing educational recommendations..."):
                   results = analyze_with_claude(client, {
                       "business_size": business_size,
                       "budget": budget,
                       "category": category,
                       "complexity": complexity,
                       "requirements": requirements
                   })
                   
                   if results and 'recommendations' in results:
                       st.success("Here are your personalized educational recommendations!")
                       
                       for tool in results['recommendations']:
                           with st.container():
                               col1, col2 = st.columns([3, 1])
                               
                               with col1:
                                   st.subheader(tool['name'])
                                   st.write(tool['description'])
                                   st.write(f"**Best For:** {tool['bestFor']}")
                                   
                                   with st.expander("Educational Details"):
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
                                   st.link_button("Learn More", tool['websiteUrl'])
                                   
                               st.divider()
   else:
       st.warning("Please enter your Anthropic API key to continue")

if __name__ == "__main__":
   main()
