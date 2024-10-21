import streamlit as st
from anthropic import Anthropic
from datetime import datetime

class ScienceAnalysisAgent:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        
    def analyze_date(self):
        date = datetime.now().strftime('%B %d')  # Get current date in readable format
        prompt = f"""Analyze 5 significant scientific discoveries on {date}. 
        Format using markdown:

        ## Discovery 1
        **Year:** [year]
        **Event:** [discovery name]
        **Simple Explanation:** [child-friendly explanation]
        **Current Use:** [current applications]
        **Future:** [future prospects]

        (Repeat format for all 5 discoveries)"""
        
        response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Access the 'content' attribute, which contains a list of TextBlocks, and extract the 'text' from each
        if isinstance(response, dict):
            # Handle the case where the response is a dictionary (could happen depending on Claude's API structure)
            return response.get('completion', response['content'][0].text)  # If response is a dictionary
        elif hasattr(response, 'content'):
            # Handle the TextBlock extraction from the 'content' attribute
            text_blocks = response.content
            full_text = ''.join([block.text for block in text_blocks])  # Concatenate all TextBlock texts
            return full_text
        else:
            return "Unexpected response format."

st.set_page_config(page_title="Daily Science Analysis", layout="centered")

st.title("🧬 Daily Science Analysis")
st.subheader(f"Discoveries from {datetime.now().strftime('%B %d')}")

api_key = st.text_input("Enter your Claude API key:", type="password")

if st.button("Analyze", type="primary"):
    if api_key:
        try:
            with st.spinner("Analyzing..."):
                agent = ScienceAnalysisAgent(api_key)
                analysis = agent.analyze_date()

                # Display the markdown-formatted response
                if analysis:
                    st.markdown(analysis, unsafe_allow_html=True)  # Render the markdown
                else:
                    st.error("No response returned")

        except Exception as e:
            st.error(f"Error occurred: {str(e)}")
    else:
        st.error("Please enter your API key.")
