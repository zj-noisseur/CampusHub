import urllib.request
from bs4 import BeautifulSoup
import sys

try:
    urllib.request.urlopen('http://127.0.0.1:8000/club/1/event/create/')
except Exception as e:
    html = e.read().decode('utf-8')
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        print("TITLE:", soup.title.string)
        traceback = soup.find('div', id='traceback_area')
        if traceback:
            print("TRACEBACK:")
            print(traceback.text[:1000])
        else:
            print("Traceback area not found. Dumping raw text:")
            print(soup.text[:2000])
    except Exception as inner_e:
        print("BeautifulSoup failed:", inner_e)
        import re
        match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        if match: print("Title:", match.group(1).strip())
        print("Fallback print first 1000 chars:")
        print(html[:1000])
