import psycopg2
import pandas as pd
import os

# Step 1: Folder Setup
folder_path = "exported_data"
os.makedirs(folder_path, exist_ok=True)  # Create folder if not exists

# Step 2: DB Connection Info
conn_info = {
    "host": "localhost",
    "port": "5432",
    "database": "postgres",
    "user": "postgres",
    "password": "postgres"
}

try:
    conn = psycopg2.connect(**conn_info)
    print("✅ Connected to database")

    table_name = "flight_data"
    query = f"SELECT * FROM {table_name}"

    df = pd.read_sql(query, conn)

    # Step 3: Save to CSV inside folder
    file_path = os.path.join(folder_path, f"{table_name}.csv")
    df.to_csv(file_path, index=False)
    print(f"✅ Exported to '{file_path}'")

    conn.close()

except Exception as e:
    print("❌ Failed to export table")
    print("Error:", e)
