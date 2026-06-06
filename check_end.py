with open('category_registry.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
print('Lines 3920-3931:')
for i in range(3919, len(lines)):
    print(f'{i+1}: {lines[i]}', end='')
