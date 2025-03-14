import re

def extract_bracketed_text(text):

    return re.findall(r'\[(.*?)\]', text)