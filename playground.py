from utils.csv_utils import load_clean_data
from utils.db_utils import reset_database, load_user_data


reset_database()
load_user_data()


def load_original_data():
    """Load original data from files"""
    # TODO: Implement this function with your file names
    print("📂 Loading original data...")
    pass


# Load existing data
df = load_clean_data()
print(f"📊 Loaded {len(df)} rows of clean data")

print("\n--- Available Functions ---")
print("load_original_data() - Load original data (to be implemented)")
print("reset_database() - Drop all tables and recreate fresh")
print("load_user_data() - Load user data from badger file")
print("💡 Use 'with MetalEvapDB() as db:' pattern for all database operations")
