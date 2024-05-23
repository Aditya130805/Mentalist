import requests
from bs4 import BeautifulSoup, Comment
from urllib.parse import urljoin, urlparse
import re
import time
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)


def normalize_url(url):
    return url.rstrip('/')


def is_valid_url(base_url, url):
    parsed_url = urlparse(url)
    return (
            parsed_url.scheme in ('http', 'https') and
            parsed_url.netloc == urlparse(base_url).netloc and
            not parsed_url.path.startswith('//') and
            len(re.findall(r'\b' + re.escape('http') + r'\b', url, flags=re.IGNORECASE)) == 0 and
            '#' not in url and
            (url != (normalize_url(base_url)) + '/index.html')
    )


def is_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def get_links(base_url, initial_question):
    if not base_url.startswith('http'):
        base_url = 'https://' + base_url
    visited_urls = set()
    urls_to_visit = [base_url]
    # overall_content = ''

    while urls_to_visit:
        current_url = urls_to_visit.pop(0)
        normalized_url = normalize_url(current_url)
        if normalized_url in visited_urls:
            continue
        if not is_valid_url(base_url, normalized_url):
            continue

        try:
            response = requests.get(current_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            anchor_tags = soup.find_all('a')
            for tag in anchor_tags:
                href = tag.get('href')
                if href:
                    full_url = urljoin(current_url, href)
                    normalized_full_url = normalize_url(full_url)
                    if is_valid_url(base_url, normalized_full_url) and normalized_full_url not in visited_urls:
                        urls_to_visit.append(normalized_full_url)
            visited_urls.add(normalized_url)

            """
            # Scraping data from the URL
            text_elements = soup.find_all(string=True) # Gets all the text inside <p>, <div>, <span>, <h1>, <h2>, etc.
            visible_texts = filter(is_visible, text_elements)
            text_content = ' '.join(t.strip() for t in visible_texts)
            text_content = re.sub(r'\s+', ' ', text_content)
            overall_content += '\n' + text_content
            """

        except Exception as e:
            print(f"Error fetching {normalized_url}: {e}")

    # Determining the best URL
    gptResponse = client.chat.completions.create(
        messages=[
            {"role": "user",
             "content": f"""{visited_urls}\n\nWhich link do you think is the most relevant from the given list 
                                      for the question: {initial_question}\n\nDo not say anything else. 
                                      JUST THE LINK. NOTHING ELSE"""}
        ],
        model="gpt-3.5-turbo",
        max_tokens=50,
        temperature=0.0
    )
    print(gptResponse)
    best_url = gptResponse.choices[0].message.content
    print(best_url)

    # Scraping the best url
    raw_content = requests.get(best_url)
    soup = BeautifulSoup(raw_content.content, 'html.parser')
    text_elements = soup.find_all(string=True)  # Gets all the text inside <p>, <div>, <span>, <h1>, <h2>, etc.
    visible_texts = filter(is_visible, text_elements)
    processed_content = ' '.join(t.strip() for t in visible_texts)
    processed_content = re.sub(r'\s+', ' ', processed_content)

    print(processed_content)
    return processed_content


if __name__ == '__main__':
    BASE_URL = 'https://pulsops.gitbook.io/docs'
    initial_question = 'how many different types of components are available in pulsops reports?'
    start_time = time.time()
    data = get_links(BASE_URL, initial_question)
    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds")
