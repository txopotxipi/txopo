import sqlite3
import re
import yaml

def main():
    # 1. Get free models from FreeLLMAPI database
    conn = sqlite3.connect('C:/Users/ragam/AppData/Roaming/FreeLLMAPI/freeapi.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT platform, model_id, display_name, rpm_limit, rpd_limit, context_window, supports_vision, supports_tools
        FROM models
        WHERE enabled = 1 
        AND (rpm_limit IS NOT NULL OR rpd_limit IS NOT NULL)
        AND (paid_input_per_m IS NULL OR paid_input_per_m = 0)
        AND (paid_output_per_m IS NULL OR paid_output_per_m = 0)
        ORDER BY platform, model_id
    """)
    
    free_models_db = cursor.fetchall()
    
    # Create a mapping: normalized model_id -> info
    free_map = {}
    for platform, model_id, display_name, rpm, rpd, ctx, vision, tools in free_models_db:
        name = model_id.split('/')[-1]
        if name.endswith(':free'):
            name = name[:-5]
        free_map[name.lower()] = {
            'platform': platform,
            'model_id': model_id,
            'display_name': display_name,
            'rpm': rpm,
            'rpd': rpd,
            'context_window': ctx or 131072,
            'supports_vision': vision,
            'supports_tools': tools
        }
    
    # 2. Parse settings.yaml freellmapi models with full details
    with open('C:/Users/ragam/.dsh/settings.yaml', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the freellmapi section and extract models with their full entries
    freellmapi_start = content.find('freellmapi:')
    if freellmapi_start == -1:
        print("freellmapi section not found!")
        return
    
    # Parse YAML to get the full structure
    settings = yaml.safe_load(content)
    freellmapi = settings.get('freellmapi', {})
    models = freellmapi.get('models', [])
    
    print(f"Total models in settings.yaml freellmapi: {len(models)}")
    
    # 3. Match each model
    matched_models = []
    unmatched_models = []
    
    for model in models:
        model_id = model.get('id', '')
        name = model.get('name', '')
        ctx = model.get('contextWindow', 131072)
        
        norm_id = model_id.lower()
        
        # Direct match
        if norm_id in free_map:
            db_info = free_map[norm_id]
            matched_models.append({
                'id': model_id,
                'name': name,
                'contextWindow': ctx,
                'db_info': db_info
            })
        else:
            # Fuzzy match: try partial matching
            found = False
            for db_name, db_info in free_map.items():
                if norm_id in db_name or db_name in norm_id:
                    matched_models.append({
                        'id': model_id,
                        'name': name,
                        'contextWindow': ctx,
                        'db_info': db_info
                    })
                    found = True
                    break
            
            if not found:
                unmatched_models.append(model)
    
    print(f"Matched free models: {len(matched_models)}")
    print(f"Unmatched models: {len(unmatched_models)}")
    
    # 4. Build filtered list - keep essential + matched free models
    # Essential models that are always available (router models)
    essential_ids = {'auto', 'fusion', 'default', 'free-router', 'fast', 'kilo-auto'}
    
    filtered_models = []
    seen_ids = set()
    
    # First add essential models
    for model in models:
        if model['id'] in essential_ids:
            filtered_models.append(model)
            seen_ids.add(model['id'])
    
    # Then add matched free models (avoid duplicates)
    for matched in matched_models:
        if matched['id'] not in seen_ids:
            # Use the original model entry but we could enhance with DB info
            orig_model = next((m for m in models if m['id'] == matched['id']), None)
            if orig_model:
                filtered_models.append(orig_model)
                seen_ids.add(matched['id'])
    
    print(f"\nFiltered models count: {len(filtered_models)}")
    
    # 5. Generate new freellmapi section
    freellmapi['models'] = filtered_models
    settings['freellmapi'] = freellmapi
    
    # 6. Write new settings.yaml
    # We need to preserve comments and formatting. Let's do a more surgical approach.
    # Instead of rewriting entire file, let's just replace the models list in the original content.
    
    # Find the models list boundaries
    lines = content.split('\n')
    models_start_line = -1
    models_end_line = -1
    base_indent = None
    
    for i, line in enumerate(lines):
        if 'freellmapi:' in line and models_start_line == -1:
            # Find models: after this
            continue
        if models_start_line == -1 and 'models:' in line and i > 0 and 'freellmapi' in '\n'.join(lines[max(0,i-10):i]):
            models_start_line = i
            base_indent = len(line) - len(line.lstrip())
            continue
        if models_start_line != -1 and models_end_line == -1:
            stripped = line.strip()
            if not stripped:
                continue
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= base_indent:
                models_end_line = i
                break
    
    if models_start_line == -1 or models_end_line == -1:
        print("Could not find models list boundaries")
        return
    
    # Build new models list YAML
    new_models_yaml = "  models:\n"
    for model in filtered_models:
        new_models_yaml += f"    - id: {model['id']}\n"
        new_models_yaml += f"      name: {model['name']}\n"
        new_models_yaml += f"      contextWindow: {model['contextWindow']}\n"
    
    # Replace in content
    new_lines = lines[:models_start_line] + new_models_yaml.split('\n') + lines[models_end_line:]
    new_content = '\n'.join(new_lines)
    
    # Write backup
    with open('C:/Users/ragam/.dsh/settings.yaml.backup_before_filter', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Write new content
    with open('C:/Users/ragam/.dsh/settings.yaml', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("\nFiltered settings.yaml written!")
    print(f"Backup saved to settings.yaml.backup_before_filter")
    
    # Show summary
    print("\n--- KEPT MODELS ---")
    for model in filtered_models:
        db_info = free_map.get(model['id'].lower())
        if db_info:
            print(f"  {model['id']} - {model['name']} (FREE: {db_info['platform']}/{db_info['model_id']})")
        else:
            print(f"  {model['id']} - {model['name']} (ESSENTIAL)")

if __name__ == '__main__':
    main()