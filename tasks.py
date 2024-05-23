from crewai import Task


class QuestionAnswerTasks:

    def research_task(self, agent, question, url):
        return Task(
            description=f"""Conduct comprehensive research on {question} from {url} or its subdirectories. 
                            Search and scrape a lot.""",
            expected_output="An organized and detailed collection of pertinent information scraped from "
                            "relevant websites.",
            async_execution=True,
            agent=agent
        )

    def information_extracting_task(self, agent, question, url):
        return Task(
            description=f"""Given a lot of organized and detailed collection of pertinent information, 
                           formulate a factually correct answer to {question} with no assumptions or 
                           guesses involved at all.""",
            expected_output=f"A concise response to the question: {question} with information only from "
                            "{url} and its subdirectories.",
            async_execution=False,
            agent=agent
        )

    def response_task(self, agent, question, url):
        return Task(
            description=f"""Refine and provide a well-structured response to the question: {question}. 
                            Make the sentences flow. Immerse the readers in your writing. Proofread, check facts, 
                            have a polite tone, and address the issue directly.""",
            expected_output="The final edited and proofread response to be shown to the user.",
            async_execution=False,
            agent=agent
        )
