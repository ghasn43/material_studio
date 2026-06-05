# Read the current file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace any en-dashes or em-dashes with regular hyphens
original_len = len(content)
content = content.replace('–', '-')  # en-dash (U+2013)
content = content.replace('—', '-')  # em-dash (U+2014)
content = content.replace('−', '-')  # minus sign (U+2212)

# Save back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Replaced all Unicode dashes with ASCII hyphens")
print(f"File size: {original_len} -> {len(content)}")
