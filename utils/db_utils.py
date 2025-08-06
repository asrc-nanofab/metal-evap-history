import pandas as pd
from src.neon_db import MetalEvapDB, MetalEvapData


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


# ####################################################################
# Load Users from Badger
# ####################################################################


def read_unique_users_from_badger():
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
    unique_users = read_unique_users_from_badger()
    load_users_to_database(unique_users)

    # Connection automatically closed here!


# ####################################################################
# Load Evaporator Run Data
# ####################################################################


# Evaporation data import functions
def load_user_evap_run_csv():
    """Load user evap run data from CSV and return clean DataFrame"""
    df = pd.read_csv("data/2025_march_user_run_data.csv")
    print(f"Loaded {len(df)} records from CSV")
    return df


def match_and_validate_users(df):
    """Match CSV users to database, error if any are missing"""
    csv_users = df["User Name"].dropna().unique()

    with MetalEvapDB() as db:
        db_users = db.get_all_users()

    # Create user mapping
    user_mapping = {}
    unmatched = []

    for csv_user in csv_users:
        csv_name_lower = csv_user.lower()
        matched = False

        for db_user in db_users:
            db_first_lower = db_user["first_name"].lower()
            db_last_lower = db_user["last_name"].lower()

            if db_first_lower in csv_name_lower and db_last_lower in csv_name_lower:
                first_pos = csv_name_lower.find(db_first_lower)
                last_pos = csv_name_lower.find(db_last_lower)

                if first_pos < last_pos:
                    user_mapping[csv_user] = db_user["id"]
                    matched = True
                    break

        if not matched:
            unmatched.append(csv_user)

    if unmatched:
        raise ValueError(f"Missing users in database: {unmatched}")

    # Add user_id column to DataFrame
    df_with_users = df.copy()
    df_with_users["user_id"] = df_with_users["User Name"].map(user_mapping)

    print(f"Matched {len(user_mapping)} users successfully")
    return df_with_users


def match_and_add_materials(df_with_user_ids):
    """Match materials and add material_id column"""
    csv_materials = df_with_user_ids["Materials"].dropna().unique()

    with MetalEvapDB() as db:
        # Get all materials from database
        all_materials = db.execute_query(
            "SELECT id, material_name, abbreviation FROM materials", fetch=True
        )

        material_mapping = {}
        unmatched_materials = []

        for csv_material in csv_materials:
            material_id = None

            # Try exact match on material_name or abbreviation
            for db_material in all_materials:
                if (
                    csv_material == db_material["material_name"]
                    or csv_material == db_material["abbreviation"]
                ):
                    material_id = db_material["id"]
                    break

            if material_id:
                material_mapping[csv_material] = material_id
            else:
                unmatched_materials.append(csv_material)

        if unmatched_materials:
            raise ValueError(f"Missing materials in database: {unmatched_materials}")

    # Add material_id column
    df_with_materials = df_with_user_ids.copy()
    df_with_materials["material_id"] = df_with_materials["Materials"].map(
        material_mapping
    )

    print(f"Matched {len(material_mapping)} materials successfully")
    return df_with_materials


def insert_tool_data(df_with_ids):
    """Insert the validated data into tool_data table"""
    with MetalEvapDB() as db:
        inserted_count = 0

        for _, row in df_with_ids.iterrows():
            try:
                tool_data = MetalEvapData(
                    user_id=row["user_id"],
                    material_id=row["material_id"],
                    date_recorded=pd.to_datetime(row["Date"]).strftime("%Y-%m-%d"),
                    thickness=float(row["Thickness"]),
                    threshold_pct=float(row["Threshold Power"])
                    if pd.notna(row["Threshold Power"])
                    else None,
                    deposition_pct=float(row["Power Deposition"])
                    if pd.notna(row["Power Deposition"])
                    else None,
                    dep_rate=float(row["Rate"]) if pd.notna(row["Rate"]) else None,
                    crystal_pct=float(row["Crystal Monitor"])
                    if pd.notna(row["Crystal Monitor"])
                    else None,
                )

                db.add_evap_data(tool_data)
                inserted_count += 1

            except Exception as e:
                print(f"Error inserting row {inserted_count + 1}: {e}")
                raise

    print(f"Inserted {inserted_count} tool data records")
    return inserted_count


def import_evap_run_data():
    """Complete workflow: load CSV, validate, and import evap run data"""
    df = load_user_evap_run_csv()
    df_with_users = match_and_validate_users(df)
    df_with_materials = match_and_add_materials(df_with_users)
    inserted_count = insert_tool_data(df_with_materials)
    return inserted_count
