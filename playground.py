from utils.db_utils import reset_database, load_user_data, import_evap_run_data
from src.neon_db import MetalEvapDB
import os
import pandas as pd

# Setup database with users
reset_database()
load_user_data()

# Import evaporation run data
print("Importing evaporation run data...")
inserted_count = import_evap_run_data()
print(f"Import complete - {inserted_count} records inserted")


def test_new_db_functions():
    """Test the new database functions for the Add Entry page"""
    print("\n🧪 Testing new database functions...")

    try:
        # Initialize database
        db = MetalEvapDB()
        print("✅ Database connection successful")

        # Test 1: Get user names for dropdown
        print("\n📋 Test 1: Getting user names for dropdown...")
        user_names = db.get_user_names_for_dropdown()
        print(f"Found {len(user_names)} users:")
        for i, name in enumerate(user_names, 1):
            print(f"  {i}. {name}")

        # Test 2: Get materials for dropdown
        print("\n🔬 Test 2: Getting materials for dropdown...")
        materials = db.get_all_materials()
        print(f"Found {len(materials)} materials:")
        for i, material in enumerate(materials[:5], 1):  # Show first 5
            print(f"  {i}. {material['material_name']} ({material['abbreviation']})")
        if len(materials) > 5:
            print(f"  ... and {len(materials) - 5} more")

        # Test 3: Test add_entry_from_widgets function
        print("\n➕ Test 3: Testing add_entry_from_widgets function...")
        if user_names and materials:
            # Use first user and first material for testing
            test_user = user_names[0]
            test_material = materials[0]["material_name"]

            print(f"Using test user: {test_user}")
            print(f"Using test material: {test_material}")

            # Add a test entry
            entry_id = db.add_entry_from_widgets(
                user_name=test_user,
                material_name=test_material,
                thickness=100.0,
                threshold_pct=15.5,
                deposition_pct=85.2,
                dep_rate=2.5,
                crystal_pct=92.1,
                measured_thickness=98.5,
                notes="Test entry from playground",
            )

            print(f"✅ Successfully added test entry with ID: {entry_id}")

            # Test 4: Verify the entry was added
            print("\n🔍 Test 4: Verifying the added entry...")
            all_data = db.get_all_tool_data_with_joins()
            latest_entry = all_data[0] if all_data else None

            if latest_entry:
                print("Latest entry details:")
                print(f"  - User: {latest_entry['user_name']}")
                print(f"  - Material: {latest_entry['material_name']}")
                print(f"  - Date: {latest_entry['date_recorded']}")
                print(f"  - Thickness: {latest_entry['thickness']} nm")
                print(f"  - Rate: {latest_entry['dep_rate']} A/s")
            else:
                print("❌ No entries found")

        else:
            print("❌ Cannot test add_entry_from_widgets - missing users or materials")

        # Test 5: Test user ID lookup
        print("\n👤 Test 5: Testing user ID lookup...")
        if user_names:
            test_user_name = user_names[0]
            user_id = db._get_user_id_by_name(test_user_name)
            print(f"User '{test_user_name}' has ID: {user_id}")

        # Test 6: Test material ID lookup
        print("\n🔬 Test 6: Testing material ID lookup...")
        if materials:
            test_material_name = materials[0]["material_name"]
            material_id = db.get_material_id(test_material_name)
            print(f"Material '{test_material_name}' has ID: {material_id}")

        # Test 7: Test dropdown options (simulate what the UI would see)
        print("\n📋 Test 7: Testing dropdown options...")
        if user_names and materials:
            user_options = ["None"] + user_names
            material_options = ["None"] + [m["material_name"] for m in materials]

            print(f"User dropdown would have {len(user_options)} options:")
            print(f"  First option: {user_options[0]}")
            print(f"  Second option: {user_options[1]}")

            print(f"Material dropdown would have {len(material_options)} options:")
            print(f"  First option: {material_options[0]}")
            print(f"  Second option: {material_options[1]}")

        # Close connection
        db.disconnect()
        print("\n✅ All tests completed successfully!")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()


def combine_monthly_csv_files():
    """
    Combine all monthly combined CSV files into one master file.

    This function looks for files matching the pattern:
    data/output_csvs/2025_XX_Metal_Evap_Data/2025_XX_combined_all_pages.csv

    It combines them in chronological order (Jan-Jun) with only one header row.
    """
    print("\n📊 Combining monthly CSV files into one master file...")

    # Base directory for output CSVs
    base_dir = "data/output_csvs"

    # Output file path for the master combined CSV
    output_file = os.path.join(base_dir, "2025_01_to_06_master_combined.csv")

    # List to store DataFrames for each month
    monthly_dfs = []

    # Process months in order (01-06)
    for month in range(1, 7):
        month_str = f"{month:02d}"  # Format as 01, 02, etc.
        month_dir = os.path.join(base_dir, f"2025_{month_str}_Metal_Evap_Data")
        csv_file = os.path.join(month_dir, "combined_all_pages.csv")

        if os.path.exists(csv_file):
            print(f"  ✓ Reading: {csv_file}")
            try:
                # Read the CSV file
                df = pd.read_csv(csv_file)
                monthly_dfs.append(df)
                print(f"    Found {len(df)} rows for month {month_str}")
            except Exception as e:
                print(f"  ✗ Error reading {csv_file}: {e}")
        else:
            print(f"  ✗ File not found: {csv_file}")

    if not monthly_dfs:
        print("❌ No monthly CSV files found to combine")
        return False

    # Combine all DataFrames
    combined_df = pd.concat(monthly_dfs, ignore_index=True)

    # Sort by date if possible
    if "Date" in combined_df.columns:
        try:
            # Try to convert dates and sort
            combined_df["Date"] = pd.to_datetime(combined_df["Date"], errors="coerce")
            combined_df = combined_df.sort_values("Date")
            # Convert back to string format
            combined_df["Date"] = combined_df["Date"].dt.strftime("%m/%d/%Y")
        except Exception as e:
            print(f"⚠️ Could not sort by date: {e}")

    # Save the combined DataFrame to CSV
    combined_df.to_csv(output_file, index=False)

    print(f"\n✅ Successfully combined {len(monthly_dfs)} monthly files")
    print(f"✅ Total rows in combined file: {len(combined_df)}")
    print(f"✅ Master file saved to: {output_file}")

    return True


# Uncomment the function you want to run:

# Reset and populate database
# reset_database()
# load_user_data()
# print("Importing evaporation run data...")
# inserted_count = import_evap_run_data()
# print(f"Import complete - {inserted_count} records inserted")

# Test database functions
# test_new_db_functions()

# Combine monthly CSV files
combine_monthly_csv_files()
