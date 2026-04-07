import re
import sys

def count_words(text):
    # Strip blockquotes (lines starting with >)
    text = re.sub(r'^>.*$', '', text, flags=re.MULTILINE)
    # Strip parenthetical references (e.g., (Jonah 1:1))
    text = re.sub(r'\([A-Za-z0-9 :;,.-]+\)', '', text)
    # Strip markdown headers
    text = re.sub(r'^#+ .*$', '', text, flags=re.MULTILINE)
    # Strip frontmatter
    text = re.sub(r'^---.*?---', '', text, flags=re.DOTALL)
    # Find words
    words = re.findall(r'\b\w+\b', text)
    return len(words)

def check_title_case(title):
    short_preps = {'in', 'on', 'at', 'to', 'by', 'of', 'up'}
    conjunctions = {'and', 'but', 'for', 'or', 'not', 'so', 'yet'}
    articles = {'a', 'an', 'the'}
    exceptions = short_preps | conjunctions | articles

    words = title.split()
    for i, word in enumerate(words):
        clean_word = re.sub(r'[^a-zA-Z]', '', word).lower()
        if i == 0 or (i > 0 and clean_word not in exceptions):
            if word[0].islower():
                return False
        elif i > 0 and clean_word in exceptions:
            if word[0].isupper() and word.lower() != 'i': # I is always upper
                # Check if it follows a colon
                if words[i-1].endswith(':'):
                    if word[0].islower():
                        return False
                else:
                    # should be lower
                    pass
    return True

def verify_article(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # 1. H1 Title
    h1_match = re.search(r'^# (.*)$', content, re.MULTILINE)
    if not h1_match:
        print("Error: No H1 title found.")
    else:
        title = h1_match.group(1)
        # Check title case (manual check preferred for complex rules, but let's try)
        print(f"H1 Title: {title}")

    # 2. Section Limits
    sections = [
        ("Introduction", r'^# .*?\n\n(.*?)\n\n##', 50),
        ("Problem", r'## The Problem of a Cruel Empire\n(.*?)\n\n##', 200),
        ("Condition", r'## Jonah\'s Status as Prophet\n(.*?)\n\n##', 100),
        ("Sacrifice", r'## The Necessary Sacrifice\n(.*?)\n\n##', 100),
        ("Initial Response", r'## Running from God\n(.*?)\n\n##', 100),
        ("Reaction", r'## Preaching in the Enemy City\n(.*?)\n\n##', 400),
        ("Miracle", r'## The Divine Miracle\n(.*?)\n\n##', 200),
        ("Result", r'## A City Spared\n(.*?)\n\n##', 200),
        ("Conclusion", r'## Conclusion\n(.*)', 150),
    ]

    for name, pattern, limit in sections:
        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
        if match:
            text = match.group(1)
            count = count_words(text)
            print(f"{name}: {count} words (Limit: {limit})")
            if count > limit:
                print(f"  FAILED: Over limit!")
        else:
            print(f"Error: Section '{name}' not found or pattern mismatch.")

    # 3. Stylistic checks
    # Em dashes in narrative
    narrative_text = re.sub(r'^>.*$', '', content, flags=re.MULTILINE)
    narrative_text = re.sub(r'^---.*?---', '', narrative_text, flags=re.DOTALL)
    if '—' in narrative_text or '–' in narrative_text:
         # Check if it's in frontmatter
         pass # handled by sub above
         # Find lines with em/en dashes
         lines = narrative_text.split('\n')
         for line in lines:
             if '—' in line or '–' in line:
                 print(f"Warning: Found dash in narrative: {line.strip()}")

    # Curly quotes
    if re.search(r'[\u201c\u201d\u2018\u2019]', content):
        print("Error: Found curly quotes.")

    # "the Lord" in OT
    if re.search(r'\bthe Lord\b', content):
        print("Warning: Found 'the Lord' (should be 'the LORD' for OT).")

if __name__ == "__main__":
    verify_article(sys.argv[1])
