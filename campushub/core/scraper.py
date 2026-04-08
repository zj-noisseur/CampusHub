"""
This script is used to read the JSON output of the Apify Agent and testing out the general manipulation of the data to be presented in the Django application.
"""

import json
import re
import requests

# Updated read function to fetch data from Apify API
def read(num=None, api_url=None, api_key=None):
    if not api_url or not api_key:
        raise ValueError("API URL and API Key must be provided")

    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(api_url, headers=headers)


    # should an error happen, immediately return the information of the error
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data: {response.status_code} - {response.text}")

    data = response.json()

    if num is not None and num < len(data):
        return data[:num]
    return data


def extract_link(text):
    url_pattern = r'https?://[^\s<>"\']+'
    links = re.findall(url_pattern, text)
    # not all posts are guaranteed to have links, should use a dictionary to store the post and its associated links
    return links if links else None

# Example usage
if __name__ == "__main__":
    API_URL = "https://api.apify.com/v2/actor-runs"  # Replace with the actual endpoint
    API_KEY = "your_api_key_here"  # Replace with your actual API key

    try:
        output = read(10, api_url=API_URL, api_key=API_KEY)

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
    except Exception as e:
        print(f"Error: {e}")


