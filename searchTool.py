from langchain.tools import tool
from openai import OpenAI
from dotenv import load_dotenv
import os
import http.client
import json
from crewai_tools import ScrapeWebsiteTool

load_dotenv()


class SearchTools:

    @tool("Always use first for search")
    def full_search(self, initial_question, website_url):
        """
            Perform a full search using OpenAI API and Serper API.

            Args:
                initial_question (str): The initial question to generate search queries from.
                website_url (str): The website URL to constrain the search within.

            Returns:
                list: A list of scraped results from the top search results.
        """

        OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        SERPER_API_KEY = os.getenv('SERPER_API_KEY')
        SERPER_BASE_URL = 'https://serper.com/search'
        client = OpenAI(api_key=OPENAI_API_KEY)

        def generate_queries(question):
            # Use OpenAI API to generate three different search queries based on the initial question
            response = client.chat.completions.create(
                messages=[
                    {"role": "user",
                     "content": f"Generate three search queries based on the initial question, making them just a bit more generalized each time: {question}"}
                ],
                model="gpt-3.5-turbo",
                max_tokens=50,
                temperature=0.0
            )
            response = response.choices[0].message.content.split('\n')
            try:
                return [item.split('. ', 1)[1] for item in response]
            except Exception as e:
                return response

        def search_with_serper(queries, url):
            top_results = []
            for query in queries:
                modified_query = f"{query} site:{url}"
                conn = http.client.HTTPSConnection("google.serper.dev")
                payload = json.dumps({
                    "q": modified_query
                })
                headers = {
                    'X-API-KEY': SERPER_API_KEY,
                    'Content-Type': 'application/json'
                }
                conn.request("POST", "/search", payload, headers)
                res = conn.getresponse()
                data = res.read()
                response = data.decode("utf-8")
                response_dict = json.loads(response)
                top_results.append(response_dict["organic"][:10])

            top_3_results = []
            count = 0
            for result_list in top_results:
                for item in result_list:
                    top_3_results.append(item)
                    count += 1
                    if count >= 3:
                        return top_3_results
            return top_3_results

        def scrape_specific_links(urls):
            num_characters = 0
            results = []
            scrape_tool = ScrapeWebsiteTool()
            for url in urls:
                scrape_tool = ScrapeWebsiteTool(website_url=url)
                result = scrape_tool.run()
                num_characters += len(result)
                results.append(result)
                if num_characters >= 4096 * 4:
                    results.pop()
                    break
            return results

        search_queries = generate_queries(initial_question)
        print(search_queries)
        cumulative_results = search_with_serper(search_queries, website_url)
        print(cumulative_results)
