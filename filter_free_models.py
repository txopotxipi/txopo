import sqlite3
import re

def main():
    # 1. Get free models from FreeLLMAPI database
    conn = sqlite3.connect('C:/Users/ragam/AppData/Roaming/FreeLLMAPI/freeapi.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT platform, model_id, display_name, rpm_limit, rpd_limit
        FROM models
        WHERE enabled = 1 
        AND (rpm_limit IS NOT NULL OR rpd_limit IS NOT NULL)
        AND (paid_input_per_m IS NULL OR paid_input_per_m = 0)
        AND (paid_output_per_m IS NULL OR paid_output_per_m = 0)
        ORDER BY platform, model_id
    """)
    
    free_models_db = cursor.fetchall()
    print(f"Free models in DB: {len(free_models_db)}")
    
    # Create a mapping: model_id -> (platform, display_name, rpm, rpd)
    # Normalize model_id: take last part after slash, remove :free suffix
    free_map = {}
    for platform, model_id, display_name, rpm, rpd in free_models_db:
        # Extract model name: last part after /
        name = model_id.split('/')[-1]
        # Remove :free suffix
        if name.endswith(':free'):
            name = name[:-5]
        # Some have different casing, normalize to lowercase for matching
        free_map[name.lower()] = (platform, model_id, display_name, rpm, rpd)
    
    # 2. Parse settings.yaml freellmapi models
    with open('C:/Users/ragam/.dsh/settings.yaml', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find freellmapi section
    freellmapi_start = content.find('freellmapi:')
    if freellmapi_start == -1:
        print("freellmapi section not found!")
        return
    
    # Extract the models list
    # Look for "models:" after freellmapi:
    models_start = content.find('models:', freellmapi_start)
    if models_start == -1:
        print("models: not found in freellmapi!")
        return
    
    # Find the next top-level key (indented less than freellmapi)
    # freellmapi is at indent 4 (assuming), models at indent 6
    # We'll parse line by line from models_start
    lines = content[models_start:].split('\n')
    
    models_list = []
    in_models = False
    base_indent = None
    for line in lines:
        if 'models:' in line and not in_models:
            in_models = True
            base_indent = len(line) - len(line.lstrip())
            continue
        if in_models:
            stripped = line.strip()
            if not stripped:
                continue
            # Check if we've exited the models list (line with less indent than base_indent + 2)
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= base_indent:
                break
            # Model entry: "- id: something"
            match = re.match(r'-\s+id:\s*(.+)', stripped)
            if match:
                model_id = match.group(1).strip()
                models_list.append(model_id)
    
    print(f"\nModels in settings.yaml freellmapi: {len(models_list)}")
    
    # 3. Match settings.yaml models with free models from DB
    matched = []
    unmatched = []
    
    for model_id in models_list:
        # Normalize for matching
        norm_id = model_id.lower()
        
        # Direct match
        if norm_id in free_map:
            matched.append((model_id, free_map[norm_id]))
        else:
            # Try fuzzy matching: some models have slightly different names
            # e.g., settings has "nemotron-3-ultra-550b" but DB has "nemotron-3-ultra-550b-a55b"
            # Let's try partial matching
            found = False
            for db_name, db_info in free_map.items():
                # Check if settings model_id is contained in DB name or vice versa
                if norm_id in db_name or db_name in norm_id:
                    matched.append((model_id, db_info))
                    found = True
                    break
            
            if not found:
                unmatched.append(model_id)
    
    print(f"\nMatched free models: {len(matched)}")
    print(f"Unmatched (not free or not in DB): {len(unmatched)}")
    
    print("\n--- MATCHED FREE MODELS ---")
    for model_id, (platform, db_model_id, display_name, rpm, rpd) in matched:
        print(f"  {model_id} -> {platform}/{db_model_id} ({display_name}) rpm={rpm} rpd={rpd}")
    
    print("\n--- UNMATCHED MODELS (likely NOT free) ---")
    for m in unmatched:
        print(f"  {m}")
    
    # 4. Generate new filtered models list for settings.yaml
    print("\n--- RECOMMENDED FILTERED LIST (only free & active) ---")
    # Keep essential ones: auto, fusion, plus all matched free models
    essential = ['auto', 'fusion']
    filtered = essential + [m[0] for m in matched]
    
    for m in filtered:
        print(f"  - id: {m}")

if __name__ == '__main__':
    main()