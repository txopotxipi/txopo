import os
import re
import glob

base_dir = r'D:\Proyectos VSC\txopo'

# Find all index.html files in subdirectories
pattern = os.path.join(base_dir, '*', 'index.html')
files = glob.glob(pattern)

# Also include root index.html
root_index = os.path.join(base_dir, 'index.html')
if os.path.exists(root_index):
    files.append(root_index)

count_updated = 0
count_skipped = 0

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Only process files that have ld+json but don't have isPartOf
    if 'application/ld+json' not in content:
        count_skipped += 1
        continue
    
    if 'isPartOf' in content:
        count_skipped += 1
        continue
    
    # Replace the closing } of the JSON-LD object with isPartOf
    # The pattern: the last } before </script> in the ld+json block
    # We match: "image": "..."\n}\n</script>
    old_pattern = r'(<script type="application/ld\+json">\s*\{[^}]*?)\}\s*\n\s*</script>'
    
    def add_ispartof(match):
        prefix = match.group(1)
        return prefix + ',\n  "isPartOf": {\n    "@type": "WebSite",\n    "name": "Txipi Txopo",\n    "url": "https://txopo.lovestoblog.com/"\n  }\n}\n</script>'
    
    new_content = re.sub(old_pattern, add_ispartof, content, flags=re.DOTALL)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        count_updated += 1
        print(f'  ✅ {os.path.relpath(filepath, base_dir)}')
    else:
        count_skipped += 1

print(f'\nDone: {count_updated} updated, {count_skipped} skipped')
