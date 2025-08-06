from utils.app_utils import load_clean_data
from src.neon_db import MetalEvapDB


def reset_database():
    """Drop all tables and recreate them fresh"""
    # Use context manager for automatic cleanup
    with MetalEvapDB() as db:
        print("🗑️  Dropping all tables...")
        db.drop_all_tables()  # ✅ Drops ALL tables completely

        print("🔧 Creating fresh tables...")
        db.create_tables()  # ✅ Creates fresh empty tables

        print("📦 Populating materials...")
        db.populate_materials()  # ✅ ONLY populates materials table

        print("✅ Database reset complete!")
    # Connection automatically closed here!


def load_original_data():
    """Load original data from files"""
    # TODO: Implement this function with your file names
    print("📂 Loading original data...")
    pass


def read_unique_users():
    """Read user data from badger file and extract unique entries"""
    import pandas as pd

    print("📂 Reading user data from badger file...")

    # Read the file, skipping the malformed first line
    df = pd.read_csv(
        "data/2025_07_31_badger_metal_evap_data.txt",
        sep="\t",  # Tab-separated
        skiprows=1,  # Skip the malformed first line
        names=[
            "equipment",
            "date",
            "role",
            "active",
            "last_name",
            "first_name",
            "member",
        ],
    )

    print(f"Read {len(df)} records from badger file")

    # Extract and format names properly (capitalize first letter, lowercase rest)
    df["first_name"] = df["first_name"].str.title()
    df["last_name"] = df["last_name"].str.title()

    # Extract unique users based on first_name and last_name only (no email)
    unique_users = df[["first_name", "last_name"]].drop_duplicates()

    print(f"Found {len(unique_users)} unique users")

    return unique_users


def load_users_to_database(unique_users):
    """Load unique users into the database"""
    print("💾 Loading users into database...")

    # Add unique users to database
    with MetalEvapDB() as db:
        added_count = 0
        for _, user in unique_users.iterrows():
            try:
                user_id = db.add_user(
                    first_name=user["first_name"],
                    last_name=user["last_name"],
                    email=None,  # No email - keep it optional
                )
                added_count += 1
                print(
                    f"  Added: {user['first_name']} {user['last_name']} (ID: {user_id})",
                    flush=True,
                )
            except Exception as e:
                print(
                    f"  ⚠️  Skipped {user['first_name']} {user['last_name']}: {e}",
                    flush=True,
                )

        print(f"✅ Successfully added {added_count} users to database")

    return added_count


def load_user_data():
    """Complete workflow: read unique users and load to database"""
    unique_users = read_unique_users()
    added_count = load_users_to_database(unique_users)
    return unique_users, added_count


load_user_data()
reset_database()

# Your existing data loading
df = load_clean_data()
print(f"Loaded {len(df)} rows of data")
print(f"Materials: {df.Materials.unique().tolist()}")


print("\n--- Available Functions ---")
print("reset_database() - Drop all tables and recreate fresh (auto-cleanup)")
print("load_original_data() - Load original data (to be implemented)")
print("load_user_data() - Load user data (to be implemented)")
print("\n--- Ready for interactive use! ---")
print("💡 Use 'with MetalEvapDB() as db:' pattern for all database operations")
