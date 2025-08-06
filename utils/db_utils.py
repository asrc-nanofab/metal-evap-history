import pandas as pd
from src.neon_db import MetalEvapDB


def read_unique_users():
    """Read user data from badger file and extract unique entries"""
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
    df["first_name"] = df["first_name"].str.lower().str.title()
    df["last_name"] = df["last_name"].str.lower().str.title()

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
        skipped_count = 0
        for _, user in unique_users.iterrows():
            try:
                db.add_user(
                    first_name=user["first_name"],
                    last_name=user["last_name"],
                    email=None,  # No email - keep it optional
                )
                added_count += 1
            except Exception:
                skipped_count += 1

        print(f"✅ Added {added_count} users, skipped {skipped_count} duplicates")

    return added_count


def load_user_data():
    """Complete workflow: read unique users and load to database"""
    unique_users = read_unique_users()
    load_users_to_database(unique_users)


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
