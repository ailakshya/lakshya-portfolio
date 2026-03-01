from duckduckgo_search import DDGS

def scrape():
    keyword = "AI Research Intern"
    results = DDGS().text(f'site:greenhouse.io OR site:lever.co "{keyword}" "Remote"', max_results=5)
    for r in results:
        print(r)
scrape()
