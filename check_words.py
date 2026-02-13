import re

def count_words(text):
    text = re.sub(r'\((?:\d\s)?[A-Z][a-z]+\s\d+(?::\d+(?:-\d+)?(?:,\s?\d+(?:-\d+)?)*)?(?:;\s(?:\d\s)?[A-Z][a-z]+\s\d+(?::\d+(?:-\d+)?(?:,\s?\d+(?:-\d+)?)*)?)*\)', '', text)
    words = text.split()
    return len(words)

with open('calling/hezekiah.md', 'r') as f:
    content = f.read()

sections = re.split(r'\n##\s+', content)
intro_part = sections[0].split('\n# ')[1].split('\n', 1)[1]
print(f"Intro: {count_words(intro_part)}")

for i, section in enumerate(sections[1:], 1):
    header = section.split('\n', 1)[0]
    body = section.split('\n', 1)[1]
    print(f"Section {i}: {count_words(body)}")
