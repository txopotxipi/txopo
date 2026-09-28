import sqlite3
import yaml

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
    """)
    free_models_db = cursor.fetchall()
    
    free_map = {}
    for platform, model_id, display_name, rpm, rpd in free_models_db:
        name = model_id.split('/')[-1]
        if name.endswith(':free'):
            name = name[:-5]
        free_map[name.lower()] = True
    
    # 2. Load settings.yaml
    settings_path = 'C:/Users/ragam/.dsh/settings.yaml'
    with open(settings_path, 'r', encoding='utf-8') as f:
        settings = yaml.safe_load(f)
    
    freellmapi = settings.get('llm-pi-ai', {}).get('providers', {}).get('freellmapi', {})
    models = freellmapi.get('models', [])
    
    print(f"Original models count in freellmapi: {len(models)}")
    
    # Essential router / slot models to always keep
    essential_ids = {'auto', 'fusion', 'default', 'free-router', 'fast', 'kilo-auto', 
                     'claude-opus-4-5', 'claude-sonnet-4-5', 'claude-haiku-4-5'}
    
    filtered_models = []
    kept_count = 0
    removed_count = 0
    
    for model in models:
        mid = model.get('id', '').lower()
        if mid in essential_ids or mid in free_map:
            filtered_models.append(model)
            kept_count += 1
        else:
            # Check fuzzy match
            found = False
            for free_name in free_map:
                if mid in free_name or free_name in mid:
                    filtered_models.append(model)
                    kept_count += 1
                    found = True
                    break
            if not found:
                removed_count += 1
                print(f"Removing non-free / inactive model: {model.get('id')}")
    
    print(f"Kept: {kept_count}, Removed: {removed_count}")
    
    # Update models in freellmapi
    freellmapi['models'] = filtered_models
    
    # Save backup
    with open(settings_path + '.backup_clean', 'w', encoding='utf-8') as f:
        with open(settings_path, 'r', encoding='utf-8') as f_orig:
            f.write(f_orig.read())
            
    # Write updated settings.yaml using PyYAML
    # Wait, PyYAML dump might lose comments if not careful, but let's check if yaml.safe_dump is okay or if we should use round-trip or custom dumping.
    # Actually, settings.yaml has many comments. If we use standard yaml.safe_dump, we will lose all comments!
    # Let's verify if yaml.safe_dump loses comments. Yes, it does.
    # Instead of safe_dumping the whole file, let's just use our surgical replacement script from before, but fixed.

if __name__ == '__main__':
    main()
