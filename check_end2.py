with open('category_registry.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
print('Lines 3900-3931:')
for i in range(3899, len(lines)):
    print(f'{i+1}: {lines[i]}', end='')
