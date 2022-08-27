import re
from bs4 import BeautifulSoup


def save_to_file(s: str, name:str):
    with open(name, "w", encoding='utf-8') as f:
        f.write(s)
        f.close()

def get_saml(text: str, elt_name):
    soup = BeautifulSoup(text, 'html.parser')
    elt = soup.find("input", {"name":elt_name})
    SAMLRequest = elt['value']
    return SAMLRequest


#    <input id="ICStateNum" name="ICStateNum" type="hidden" value="5"/>
def get_statenum(text: str, parser='html.parser'):
    # raises indexerror if not found
    soup = BeautifulSoup(text, parser)
    elt = soup.find('input', {'id':'ICStateNum'})
    if elt == None:
        pattern = re.compile(r"input type='hidden' name='ICStateNum' id='ICStateNum' value='(\d*)")
        statenum = pattern.search(text).group(1)
    else:
        statenum = elt['value']
    return statenum

def get_classes(response: str):
    pattern = re.compile(r'P_CLASS_NAME\$(\d+)')
    soup = BeautifulSoup(response, 'html.parser')
    elts = soup.find_all('a', {"id": pattern})
    pattern = re.compile(r'\((\d+)\)')
    di = {}
    for i, elt in enumerate(elts):
        di[str(pattern.search(elt.text).group(1))] = i
    return di

