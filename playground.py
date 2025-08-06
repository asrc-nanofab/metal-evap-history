from utils.db_utils import reset_database, load_user_data, import_evap_run_data


# Setup database with users
reset_database()
load_user_data()

# Import evaporation run data
print("Importing evaporation run data...")
inserted_count = import_evap_run_data()
print(f"Import complete - {inserted_count} records inserted")
