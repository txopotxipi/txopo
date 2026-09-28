import sqlite3

def main():
    conn = sqlite3.connect('C:/Users/ragam/AppData/Roaming/FreeLLMAPI/freeapi.db')
    cursor = conn.cursor()
    
    # Get all models with their details
    cursor.execute("""
        SELECT id, platform, model_id, display_name, enabled, 
               rpm_limit, rpd_limit, tpm_limit, tpd_limit,
               monthly_token_budget, context_window, supports_vision, supports_tools,
               intelligence_rank, speed_rank, size_label,
               paid_input_per_m, paid_output_per_m,
               source, endpoint_scope
        FROM models
        ORDER BY platform, model_id
    """)
    
    models = cursor.fetchall()
    
    print(f"Total models: {len(models)}")
    print("\n--- FREE MODELS (enabled, rpm_limit or rpd_limit set, paid=0) ---")
    
    free_models = []
    for m in models:
        model_id = m[2]
        platform = m[1]
        enabled = m[4]
        rpm = m[5]
        rpd = m[6]
        paid_in = m[16]
        paid_out = m[17]
        
        # Consider free if enabled and has rate limits (free tier) and paid=0 or NULL
        is_free = enabled and (rpm or rpd) and (paid_in is None or paid_in == 0) and (paid_out is None or paid_out == 0)
        
        if is_free:
            free_models.append(m)
            print(f"  {platform}/{model_id} - {m[3]} (rpm={rpm}, rpd={rpd}, ctx={m[10]})")
    
    print(f"\nTotal free models: {len(free_models)}")
    
    # Also show models by platform
    print("\n--- MODELS BY PLATFORM ---")
    by_platform = {}
    for m in models:
        platform = m[1]
        if platform not in by_platform:
            by_platform[platform] = []
        by_platform[platform].append(m)
    
    for platform, mlist in by_platform.items():
        free_count = sum(1 for m in mlist if m[4] and (m[5] or m[6]) and (m[16] is None or m[16] == 0))
        print(f"  {platform}: {len(mlist)} total, {free_count} free")
    
    # Check quota observations for free models
    print("\n--- QUOTA OBSERVATIONS (recent errors) ---")
    cursor.execute("""
        SELECT platform, model_id, status_code, notes, observed_at
        FROM provider_quota_observations
        WHERE status_code = 429 OR notes LIKE '%rate limit%' OR notes LIKE '%free%'
        ORDER BY observed_at DESC
        LIMIT 20
    """)
    quota = cursor.fetchall()
    for q in quota:
        print(f"  {q[0]}/{q[1]} - {q[2]} - {q[3]} ({q[4]})")

if __name__ == '__main__':
    main()