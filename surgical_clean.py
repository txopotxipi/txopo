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
    """)
    free_models_db = cursor.fetchall()
    
    free_map = {}
    for platform, model_id, display_name, rpm, rpd in free_models_db:
        name = model_id.split('/')[-1]
        if name.endswith(':free'):
            name = name[:-5]
        free_map[name.lower()] = True
        
    # Also include models that are known to work or part of essential slots
    essential_ids = {
        'auto', 'fusion', 'default', 'free-router', 'fast', 'kilo-auto',
        'claude-opus-4-5', 'claude-sonnet-4-5', 'claude-haiku-4-5'
    }

    settings_path = 'C:/Users/ragam/.dsh/settings.yaml'
    with open(settings_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find where freellmapi models list starts
    # We look for "freellmapi:" then "models:"
    freellmapi_idx = content.find('freellmapi:')
    if freellmapi_idx == -1:
        print("freellmapi not found")
        return
        
    models_idx = content.find('models:', freellmapi_idx)
    if models_idx == -1:
        print("models under freellmapi not found")
        return

    # Let's split content into lines
    lines = content.split('\n')
    
    # Find the exact line index for models: under freellmapi
    target_line_idx = -1
    for i, line in enumerate(lines):
        if i > 500 and 'models:' in line and 'freellmapi' in '\n'.join(lines[max(0, i-15):i]):
            target_line_idx = i
            break
            
    if target_line_idx == -1:
        print("Could not locate models line for freellmapi")
        return
        
    print(f"Found models line at index {target_line_idx}: {lines[target_line_idx]}")
    
    # The models list items start after target_line_idx
    # Each model entry starts with "- id:" at indent 8 (typically)
    # Let's parse line by line from target_line_idx + 1
    
    header_lines = lines[:target_line_idx + 1]
    model_lines_raw = lines[target_line_idx + 1:]
    
    # Find where the models list ends (when indentation goes back to <= 4 or next top-level key)
    # Let's collect model blocks
    blocks = []
    current_block = []
    
    for line in model_lines_raw:
        # Check if line is a new top-level key or next section (indent 0 to 4)
        stripped = line.strip()
        if stripped and not line.startswith(' '):
            # Hit next section
            break
        if stripped.startswith('- id:'):
            if current_block:
                blocks.append(current_block)
            current_block = [line]
        else:
            if current_block:
                current_block.append(line)
            else:
                # Might be trailing lines or empty lines before next section
                header_lines_tail = header_lines # wait, let's keep them separate
                
    if current_block:
        blocks.append(current_block)
        
    print(f"Total model blocks found: {len(blocks)}")
    
    kept_blocks = []
    removed_count = 0
    
    for block in blocks:
        # Extract model id from first line of block
        first_line = block[0]
        match = re.search(r'-\s+id:\s*(.+)', first_line)
        if match:
            mid = match.group(1).strip().lower()
            # Check if free or essential
            is_free = mid in essential_ids or mid in free_map
            if not is_free:
                # Check fuzzy match
                for free_name in free_map:
                    if mid in free_name or free_name in mid:
                        is_free = True
                        break
            
            if is_free:
                kept_blocks.append(block)
            else:
                removed_count += 1
                print(f"Removing model: {mid}")
        else:
            kept_blocks.append(block)
            
    print(f"Kept blocks: {len(kept_blocks)}, Removed: {removed_count}")
    
    # Reassemble file
    new_model_lines = []
    for block in kept_blocks:
        new_model_lines.extend(block)
        
    # Find what comes after the models list
    # Let's find where the model blocks ended in original model_lines_raw
    total_parsed_lines = sum(len(b) for b in blocks)
    tail_lines = model_lines_raw[total_parsed_lines:]
    
    new_content = '\n'.join(header_lines + new_model_lines + tail_lines)
    
    # Backup
    with open(settings_path + '.backup_surgical', 'w', encoding='utf-8') as f:
        with open(settings_path, 'r', encoding='utf-8') as f_orig:
            f.write(f_orig.read())
            
    with open(settings_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print("Surgical cleanup completed successfully!")

if __name__ == '__main__':
    main()
