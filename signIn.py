import json
import re
from bs4 import BeautifulSoup
import yaml
import requests

# read private info
with open("privateInfo.yml", 'r') as stream:
    info = yaml.safe_load(stream)['info']

Email = info['email']
Password = info['password']

client = requests.Session()

HOMEPAGE_URL = 'https://www.linkedin.com'

# find the url using form tag in html: 'https://www.linkedin.com/uas/login-submit'
LOGIN_URL = " "

html = client.get(HOMEPAGE_URL).content
doc = BeautifulSoup(html, "html.parser")

# This dictionary will be the json that we send to server to login
dictionary = {}


def matchRequiredWithInformation(scrapList, input_tag):
    global dictionary
    global Email
    global Password
    scrapList.append(input_tag.get('name'))
    scrapList.append(input_tag.get('autocomplete'))
    scrapList.append(input_tag.get('placeholder'))

    for usernameOrPass in scrapList:
        # Search possible places that inform user to get thire email or username or phone number-Email always works.
        if re.search(r'([Ee]mail)|([uU]sername)|([pP]hone)', usernameOrPass) is not None:
            dictionary[input_tag.get('name')] = Email

        # Search for password to set
        elif re.search(r'([Pp]assword)|([Pp]ass)', usernameOrPass) is not None:
            dictionary[input_tag.get('name')] = Password


# placeholder label require
tag = doc.find('form')

if tag.get('method') == 'post':
    LOGIN_URL = tag.get('action')

for input_tag in tag.find_all('input'):
    # only fill out the required information
    if input_tag.get("required") == 'false':
        continue
    #
    if (input_tag.get('type') == 'text') or (input_tag.get('type') == 'password'):
        scrapList = []
        for label in input_tag.parent.find_all('label'):
            if label.string is not None:
                scrapList.append(label.string)

        matchRequiredWithInformation(scrapList, input_tag)

    elif input_tag.get('type') == 'hidden':
        dictionary[input_tag.get('name')] = input_tag.get('value')

login_information = json.dumps(dictionary, indent=4)
print(login_information)
response = client.post(LOGIN_URL, data=login_information)

print(response)
# The json most be sth like this:
'''
login_information = {
    'session_key': Email,
    'session_password': Password,
    'loginCsrfParam': csrf,
    'trk': 'guest_homepage-basic_sign-in-submit'
}
'''
