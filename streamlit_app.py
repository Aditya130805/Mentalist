import streamlit as st
import time as t
import os
from dotenv import load_dotenv
from crewai import Crew
from tasks import QuestionAnswerTasks
from agents import QuestionAnswerAgents

__import__('pysqlite3')
import sys

sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SERPER_API_KEY = os.getenv('SERPER_API_KEY')
os.environ['OPENAI_MODEL_NAME'] = 'gpt-3.5-turbo'

# Initialize tasks and agents
tasks = QuestionAnswerTasks()
agents = QuestionAnswerAgents()

# Streamlit app
st.set_page_config(page_title="Mentalist", layout="centered")
st.write("""# Mentalist""")
st.markdown("""### Welcome to the mentalist!""")
st.write("""I can help you find answers to your questions by leveraging the best-in-class AI agents. 
            Don't shy away from prompting me a few times if my psychic skills are running a bit weak.""")

st.sidebar.header("User Input")
question = st.sidebar.text_area("What would you like to know?", "", height=150)
url = st.sidebar.text_input("Provide a link for the official website where we might find your answer:", "")

if st.sidebar.button("Submit"):
    if not question or not url:
        st.sidebar.error("Please provide both a question and a URL.")
    else:
        start_time = t.time()

        # Create Agents
        researcher_agent = agents.research_agent(question, url)
        information_extracting_agent = agents.information_extracting_agent(question, url)
        response_agent = agents.response_agent(question, url)

        # Create Tasks
        research = tasks.research_task(researcher_agent, question, url)
        rough_answer = tasks.information_extracting_task(information_extracting_agent, question, url)
        response = tasks.response_task(response_agent, question, url)

        rough_answer.context = [research]
        response.context = [rough_answer]

        crew = Crew(
            agents=[researcher_agent, information_extracting_agent, response_agent],
            tasks=[research, rough_answer, response]
        )

        # Execute tasks
        with st.spinner('Finding the answer...'):
            result = crew.kickoff()

        end_time = t.time()

        st.success("Here is the result")
        st.markdown(f"{result}")

        st.info(f"Time taken: {end_time - start_time} seconds")
