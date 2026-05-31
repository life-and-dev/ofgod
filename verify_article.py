import re
import sys
import os

def check_title_case(title):
    exceptions = {'a', 'an', 'the', 'and', 'but', 'for', 'or', 'not', 'so', 'yet', 'in', 'on', 'at', 'to', 'by', 'of', 'up'}
    words = title.split()
    if not words:
        return True

    # Check first word
    if not words[0][0].isupper():
        return False

    for i in range(1, len(words)):
        word = words[i].lower().strip(':')
        # Remove possessive 's for casing check
        clean_word = re.sub(r"'s$", '', word)

        if clean_word in exceptions:
            if words[i][0].isupper() and not words[i-1].endswith(':'):
                 return False # Should be lowercase
        else:
            if not words[i][0].isupper():
                return False # Should be uppercase
    return True

def count_narrative_words(text):
    # Strip blockquotes
    text = re.sub(r'^>.*$', '', text, flags=re.MULTILINE)
    # Strip parenthetical references
    text = re.sub(r'\([A-Za-z0-9 :;,.-]+\)', '', text)
    # Find words
    words = re.findall(r'\b\w+\b', text)
    return len(words)

def verify_article(filepath):
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found")
        return

    with open(filepath, 'r') as f:
        content = f.read()

    # Split frontmatter
    parts = content.split('---')
    if len(parts) < 3:
        print("Missing frontmatter")
        body = content
    else:
        body = parts[2]

    # Verify H1
    h1_match = re.search(r'^# (.*)$', body, re.MULTILINE)
    if h1_match:
        h1_title = h1_match.group(1)
        if not check_title_case(h1_title):
            print(f"H1 Title Case issue: {h1_title}")
    else:
        print("H1 title not found")

    # Verify H2s
    h2s = re.findall(r'^## (.*)$', body, re.MULTILINE)
    for h2 in h2s:
        if not check_title_case(h2):
            print(f"H2 Title Case issue: {h2}")

    # Section mapping and word counts
    sections = re.split(r'^## ', body, flags=re.MULTILINE)

    # Introduction is between H1 and first H2
    intro_match = re.search(r'^# .*?\n\n(.*?)\n\n##', body, re.MULTILINE | re.DOTALL)
    if intro_match:
        intro_text = intro_match.group(1)
        count = count_narrative_words(intro_text)
        if count >= 50:
            print(f"Intro word count too high: {count} (limit 50)")
    else:
        print("Intro section not found")

    limits = {
        'Problem': 200,
        'Condition': 100,
        'Sacrifice': 100,
        'Initial Response': 100,
        'Reaction': 400,
        'Miracle': 200,
        'Result': 200,
        'Conclusion': 150
    }

    for section in sections[1:]:
        lines = section.split('\n')
        title = lines[0].strip()
        text = '\n'.join(lines[1:])

        for key, limit in limits.items():
            if key.lower() in title.lower():
                count = count_narrative_words(text)
                if count >= limit:
                    print(f"Section '{title}' word count too high: {count} (limit {limit})")

    # Check divine pronouns
    # Match mid-sentence capitalized pronouns
    divine_pronouns = r'\b(He|Him|His|Who)\b'
    narrative_lines = [line for line in body.split('\n') if not line.startswith('>')]
    for i, line in enumerate(narrative_lines):
        matches = re.finditer(r'(?<!\. )(?<!^)(?<!\? )(?<!\! )\b(He|Him|His|Who)\b', line)
        for match in matches:
            # Check if it's a known non-divine use or start of sentence (already handled by lookbehind)
            print(f"Line {i}: Potential divine pronoun capitalization check: {match.group(0)}")

    # Check "the Lord" in OT
    if "the Lord" in body and "Old Testament" in body or True: # Basic check for OT articles
        matches = re.finditer(r'\bthe Lord\b', body)
        for match in matches:
            # Need to exclude blockquotes for this check if it's narrative, but rules say OT scriptures must be CAPITALIZED
            pass # Manual check often better for "the Lord" vs "the LORD"

    # Check em/en dashes in narrative
    for i, line in enumerate(body.split('\n')):
        if not line.startswith('>') and not line.startswith('---'):
            if '—' in line or '–' in line:
                print(f"Line {i}: Prohibited dash found in narrative: {line}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        verify_article(sys.argv[1])
    else:
        print("Usage: python3 verify_article.py <filepath>")
