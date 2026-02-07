from serpapi import GoogleSearch

query="give a list (first and last name or artist group names) of 100 musicial artists, don't separate the two"

params = {
  "engine": "google_ai_mode",
  "q": query,
  "api_key": "c6e3b141e2b90d584f1f3c9405064e06e037852ccfd045fa1dd5f6aefb95d90b"
}

search = GoogleSearch(params)
results = search.get_dict()
text_blocks = results["text_blocks"]

with open('./Data/generated_people.csv', 'w') as f:
    f.write('Artist_Name\n')
    for block in text_blocks:
        if block.get('type') == 'list' and 'list' in block:
            for item in block['list']:
                if 'snippet' in item:
                    f.write(f"{item['snippet']}\n")
    