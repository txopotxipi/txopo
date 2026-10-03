#!/usr/bin/env python3
"""
Add JSON-LD structured data (ImageGallery schema.org) to all gallery index.html files.
Reads existing og:title, og:description, og:url, og:image tags and creates
corresponding JSON-LD script blocks.
"""
import os
import re
import glob
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def extract_og(filepath):
    """Extract OG tag values from an HTML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    og_title = re.search(r'<meta\s+property=["\']og:title["\']\s+content=["\']([^"\']*)["\']', content)
    og_desc = re.search(r'<meta\s+property=["\']og:description["\']\s+content=["\']([^"\']*)["\']', content)
    og_url = re.search(r'<meta\s+property=["\']og:url["\']\s+content=["\']([^"\']*)["\']', content)
    og_image = re.search(r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']*)["\']', content)
    
    return {
        'title': og_title.group(1) if og_title else None,
        'description': og_desc.group(1) if og_desc else None,
        'url': og_url.group(1) if og_url else None,
        'image': og_image.group(1) if og_image else None,
    }

def has_jsonld(content):
    """Check if file already has JSON-LD."""
    return 'application/ld+json' in content

def create_jsonld(og_data):
    """Create JSON-LD script tag from OG data."""
    ld = {
        "@context": "https://schema.org",
        "@type": "ImageGallery",
        "name": og_data['title'] or '',
        "description": og_data['description'] or '',
        "url": og_data['url'] or '',
        "image": og_data['image'] or '',
    }
    json_str = json.dumps(ld, indent=2, ensure_ascii=False)
    return f'<script type="application/ld+json">\n{json_str}\n</script>'

def add_jsonld_to_file(filepath):
    """Add JSON-LD to a single HTML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if has_jsonld(content):
        return False, "already has JSON-LD"
    
    og_data = extract_og(filepath)
    
    if not og_data['title'] or not og_data['url']:
        return False, f"missing OG data (title={og_data['title']}, url={og_data['url']})"
    
    jsonld_block = create_jsonld(og_data)
    
    # Insert before </head>
    new_content = content.replace('</head>', f'\n{jsonld_block}\n</head>', 1)
    
    if new_content == content:
        # Try alternative: insert after twitter:card
        tc_match = re.search(r'<meta\s+name=["\']twitter:card["\'][^>]*>', content)
        if tc_match:
            pos = tc_match.end()
            new_content = content[:pos] + f'\n{jsonld_block}' + content[pos:]
        else:
            # Insert before first <link after OG tags
            link_match = re.search(r'<link\s+', content)
            if link_match:
                pos = link_match.start()
                new_content = content[:pos] + f'{jsonld_block}\n' + content[pos:]
            else:
                return False, "could not find insertion point"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True, "OK"

def main():
    # Find all gallery index.html files
    gallery_files = glob.glob(os.path.join(BASE_DIR, '*/index.html'))
    
    # Also include root index.html
    root_index = os.path.join(BASE_DIR, 'index.html')
    if os.path.exists(root_index):
        gallery_files.append(root_index)
    
    results = {'ok': [], 'skip': [], 'fail': []}
    
    for filepath in sorted(gallery_files):
        relpath = os.path.relpath(filepath, BASE_DIR)
        
        try:
            success, msg = add_jsonld_to_file(filepath)
            if success:
                results['ok'].append(relpath)
                print(f"✅ {relpath}")
            else:
                results['skip'].append((relpath, msg))
                print(f"⏭️ {relpath} - {msg}")
        except Exception as e:
            results['fail'].append((relpath, str(e)))
            print(f"❌ {relpath} - ERROR: {e}")
    
    print(f"\n--- RESULTADOS ---")
    print(f"✅ Añadidos: {len(results['ok'])}")
    print(f"⏭️ Omitidos: {len(results['skip'])}")
    print(f"❌ Fallos: {len(results['fail'])}")
    
    if results['skip']:
        print("\nOmitidos:")
        for path, reason in results['skip']:
            print(f"  {path}: {reason}")
    
    if results['fail']:
        print("\nFallos:")
        for path, reason in results['fail']:
            print(f"  {path}: {reason}")

if __name__ == '__main__':
    main()
