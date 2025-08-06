from utils.db_utils import reset_database, load_user_data, import_evap_run_data
from src.neon_db import MetalEvapDB


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
                print(f"Latest entry details:")
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


# Setup database with users
reset_database()
load_user_data()

# Import evaporation run data
print("Importing evaporation run data...")
inserted_count = import_evap_run_data()
print(f"Import complete - {inserted_count} records inserted")

# Run the new test function
test_new_db_functions()
