import requests
from bs4 import BeautifulSoup
import openai
import streamlit as st
import pandas as pd
import re
import os
# Global list to store analysis results
analysis_results = []
# Function to extract text from a URL
def extract_text_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            paragraphs = soup.find_all('p')
            text = ' '.join([p.get_text() for p in paragraphs])
            return text
        else:
            print(f"Failed to retrieve {url}")
            return None
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None
#openAI API key
OPENAI_API_KEY = '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'
# Function to analyze CEFR level and lexical complexity using OpenAI
def analyze_text_with_openai(text, openai_api_key):
    try:
        openai.api_key = openai_api_key
        # Request for lexical complexity score
        prompt_lexical = f"Provide a lexical complexity score on a scale from 0 to 100 for the following text:\n{text}"
        response_lexical = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt_lexical,
            max_tokens=60,
            temperature=0
        )
        lexical_matches = re.findall(r'\b\d+\b', response_lexical.choices[0].text.strip())
        lexical_score = lexical_matches[0] if lexical_matches else "N/A"
        # Request for CEFR level
        prompt_cefr = f"Assess the CEFR level (A1, A2, B1, B2, C1, C2) of the following text, can you format the score as just the CEFR level, nothing else please:\n{text}"
        response_cefr = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt_cefr,
            max_tokens=60,
            temperature=0
        )
        cefr_matches = re.findall(r'\b(A1|A2|B1|B2|C1|C2)\b', response_cefr.choices[0].text.strip())
        cefr_score = cefr_matches[0] if cefr_matches else "N/A"
        return lexical_score, cefr_score
    except Exception as e:
        error_message = f"An error occurred with OpenAI: {type(e).__name__}, {str(e)}"
        print(error_message)
        return "Error", "Error"
if 'analysis_results' not in st.session_state:
    st.session_state['analysis_results'] = []
st.title('AI Lexical Complexity and CEFR Analyzer')
st.subheader('Enter the URL of an article to analyze its lexical complexity and CEFR level')
user_url = st.text_input("Article URL:")
if st.button("Analyze"):
    article_text = extract_text_from_url(user_url)
    if article_text:
        lexical_complexity_score, cefr_score = analyze_text_with_openai(article_text, OPENAI_API_KEY)
        # Removed the isdigit() check for cefr_score as it's now a string like "A1", "B2", etc.
        if lexical_complexity_score.isdigit():
            article_title = BeautifulSoup(requests.get(user_url).content, 'html.parser').title.string
            st.session_state['analysis_results'].append({
                "Article Title": article_title,
                "Article URL": user_url,
                "Lexical Complexity Score": lexical_complexity_score,
                "CEFR Score": cefr_score  # CEFR score is now a string like "A1", "B2", etc.
            })
        else:
            st.error(f"Failed to analyze text. Reason: {lexical_complexity_score}, {cefr_score}")
    else:
        st.error("Failed to retrieve article.")
# Display the entire list of results
if st.session_state['analysis_results']:
    st.subheader("All Analysis Results")
    st.table(pd.DataFrame(st.session_state['analysis_results']))