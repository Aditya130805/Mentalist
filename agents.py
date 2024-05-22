from crewai import Agent
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()

class QuestionAnswerAgents:

    def research_agent(self, question, url):
        return Agent(
            role='Novice researcher',
            backstory=f"""You are a junior intern at the company, who is keen on doing research.""",
            goal=f"Try different search queries regarding {question}, and obtain results ONLY from {url} and its"
                  "subdirectories",
            tools = [search_tool, scrape_tool],
            allow_delegation=False,
            memory=True,
            verbose=True
        )

    def information_extracting_agent(self, question, url):
        return Agent(
            role='Analysis Expert',
            backstory=f"""You are a top analyzer with a great attention to detail. Given ample information, you can 
                         provide answers to even the toughest questions one could formulate. You pride yourself in 
                         being completely accurate in your responses, and not spreading any misinformation 
                         whatsoever.""",
            goal=f"Extract factual, accurate and precise answer for {question} given context.",
            allow_delegation=False,
            verbose=True
        )

    def response_agent(self, question, url):
        return Agent(
            role='Professional Writer',
            backstory=f"""You are one of the best editors in the world working with {url} company. Given just
                         crucial bits of information, you can edit it in such a way as to convey that information
                         masterfully to answer whatever question it is that was posed. You remain to the point, and
                         use facts as your superpower.""",
            goal=f"Masterfully craft a perfect response to {question} given its answer in a crude form.",
            allow_delegation=False,
            verbose=True
        )