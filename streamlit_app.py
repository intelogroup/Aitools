def main():
    st.set_page_config(page_title="AI Tool Recommender", layout="wide")
    
    st.title("🤖 AI Tool Recommender")
    
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ''
    
    with st.sidebar:
        api_key = st.text_input("Enter Anthropic API Key:", 
                               value=st.session_state.api_key,
                               type="password",
                               key="api_key_input")
                               
    if api_key:
        st.session_state.api_key = api_key
        client = Anthropic(api_key=api_key)
        
        # Form for input
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
        
        # Handle form submission and display results outside the form
        if submitted:
            tools = analyze_with_claude(client, {
                "business_size": business_size,
                "budget": budget,
                "category": category,
                "complexity": complexity,
                "requirements": requirements
            })
            
            if tools:
                # Display filtering options
                col1, col2 = st.columns(2)
                with col1:
                    sort_by = st.selectbox(
                        'Sort by:', 
                        ['Match Score', 'Name', 'Pricing'],
                        key='sort_select'
                    )
                with col2:
                    price_filter = st.slider('Price Range ($)', 0, 1000, (0, 1000), key='price_filter')

                # Comparison view
                if st.checkbox('Compare Tools', key='compare_toggle'):
                    show_comparison_view(tools)
                
                # Display recommendations
                for tool in sorted(tools, key=lambda x: x['score'], reverse=True):
                    create_tool_card(tool)

                # Export option
                csv_data = export_recommendations(tools)
                if csv_data:
                    st.download_button(
                        "Export Results",
                        csv_data,
                        "ai_tools.csv",
                        "text/csv",
                        key="download_button"
                    )

    else:
        st.warning("Please enter your API key in the sidebar to continue")
