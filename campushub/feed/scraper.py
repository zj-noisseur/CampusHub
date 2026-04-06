"""
This script is used to read the JSON output of the Apify Agent and testing out the general manipulation of the data to be presented in the Django application.
"""

import json
import re

# num determines the number of entries to be processed, if not specified will read the entire JSON file
def read(num=None):
    with open('ITSociety.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    if num is not None and num < len(data):
        return data[:num]
    return data


def extract_link(text):
    url_pattern = r'https?://[^\s<>"\']+'
    links = re.findall(url_pattern, text)
    # not all posts are guaranteed to have links, should use a dictionary to store the post and its associated links
    return links if links else None

output = read(10)

posts_links = {}
for posts in output:
    url = posts['url']
    caption = posts['caption']
    print(caption)

    try:
        links = extract_link(caption)
        posts_links[url] = links
    except Exception as e:
        posts_links[url] = None

print(posts_links)
    
        
