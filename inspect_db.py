import sqlite3

def main():
    conn = sqlite3.connect('C:/Users/ragam/AppData/Roaming/FreeLLMAPI/freeapi.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Tables:", tables)
    for table_name in [t[0] for t in tables]:
        print(f"\nSchema of {table_name}:")
        cursor.execute(f"PRAGMA table_info({table_name})")
        print(cursor.fetchall())
        
        # let's try to query some data
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        print("Count:", cursor.fetchone()[0])
        
        # sample data
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
        print("Sample:", cursor.fetchall())

if __name__ == '__main__':
    main()
