import json

with open('official_clsc_mmu_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

    # currently the json has nested fields, but for the nested fields they are treated as  

    # testing just the first entry

    for item in data: 
        # if the scraped content is a carousel, consisting of more than one image in a singular post
        if item['type'] == 'Sidecar':
            caption = item['caption']
            images = [link for link in item['images']]
            
        elif item['type'] == 'Image':
            caption = item['caption']
            image = item['images']
            