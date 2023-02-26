import requests
import json
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
import nltk
from nltk.corpus import words


# Step 1: scrape the index page 
url = 'http://www.cfcunderwriting.com'
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

external_resources = []
privacy_tag = None

# Step 2: loop through tags to find external resources
for tag in soup.find_all():
    for attr_name, attr_value in tag.attrs.items():

        # If a tag has a src attribute or a href attribute
        # compare with the base url to check if its a external resource
        if attr_name == 'src' or attr_name == 'href':
            parsed_url = urlparse(attr_value)
            if parsed_url.netloc and parsed_url.netloc not in url:
                external_resources.append(str(tag))

            # Step 3: locate the privacy policy url
            if 'privacy' in tag.text.lower() or 'privacy' in tag.get('href', '').lower():
                privacy_tag = tag

# Save results to json file
with open('external_resources.json', 'w') as f:
    json.dump(external_resources, f)

# Download a set of words for the frequency count
nltk.download('words')
set_of_words = set(words.words())
frequency_count = {}
if privacy_tag is not None:

    # Step 4: Go to privacy policy page and scrape contents
    privacy_url = url + privacy_tag['href']
    response = requests.get(privacy_url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Loop through all tags in page
    for tag in soup.find_all():

        # If a tag name is script or style it is not visible text.
        if tag.name != 'script' or tag.name != 'style':
            # Create regex to only have alphabetic characters
            regex = re.compile('[^a-zA-Z]')
            text = tag.text.strip().lower()
            words = text.split()
            # Loop through words and append to frequency dictionary
            for word in words:
                word = regex.sub('', word)
                # Only append to dictionary if the string is a valid word
                if word in set_of_words:
                    try:
                        frequency_count[word] += 1
                    except:
                        frequency_count[word] = 1

with open('frequency.json', 'w') as f:
    json.dump(frequency_count, f)
