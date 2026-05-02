import urllib.request
import re

try:
    urllib.request.urlopen('http://127.0.0.1:8000/club/1/event/create/')
except Exception as e:
    html = e.read().decode('utf-8')
    match = re.search(r'<div class="exception_value">(.*?)</div>', html, re.DOTALL)
    if match: 
        print('Exception:', match.group(1).strip())
    else: 
        print('Could not find exception value.')
    
    match2 = re.search(r'<h2>(.*?)</h2>', html, re.DOTALL)
    if match2: 
        print('Title:', match2.group(1).strip())
