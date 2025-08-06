"""
Database backup utilities for Metal Evaporation History
"""

import io
import zipfile
import pandas as pd
from datetime import datetime
from src.neon_db import MetalEvapDB
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_database_backup_zip():
    """
    Create a ZIP file containing CSV backups of all database tables

    Returns:
        tuple: (success, data, filename)
            - success: Boolean indicating if backup was successful
            - data: Bytes of the ZIP file or None if failed
            - filename: Name of the ZIP file or error message
    """
    try:
        # Initialize database connection
        db = MetalEvapDB()

        # Get current timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"metal_evap_backup_{timestamp}.zip"

        # Create in-memory ZIP file
        zip_buffer = io.BytesIO()
        record_counts = {}

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            # Export users table
            users = db.get_all_users()
            if users:
                users_df = pd.DataFrame(users)
                users_csv = users_df.to_csv(index=False)
                zipf.writestr(f"users_{timestamp}.csv", users_csv)
                record_counts["users"] = len(users)
                logger.info(f"Users backup added: {len(users)} records")

            # Export materials table
            materials = db.get_all_materials()
            if materials:
                materials_df = pd.DataFrame(materials)
                materials_csv = materials_df.to_csv(index=False)
                zipf.writestr(f"materials_{timestamp}.csv", materials_csv)
                record_counts["materials"] = len(materials)
                logger.info(f"Materials backup added: {len(materials)} records")

            # Export tool data with joins
            tool_data = db.get_all_tool_data_with_joins()
            if tool_data:
                tool_data_df = pd.DataFrame(tool_data)
                tool_data_csv = tool_data_df.to_csv(index=False)
                zipf.writestr(f"tool_data_{timestamp}.csv", tool_data_csv)
                record_counts["tool_data"] = len(tool_data)
                logger.info(f"Tool data backup added: {len(tool_data)} records")

        # Close database connection
        db.disconnect()

        # Check if any data was backed up
        if not record_counts:
            return False, None, "No data found to backup"

        # Get the ZIP file bytes
        zip_buffer.seek(0)
        zip_data = zip_buffer.getvalue()

        # Create a summary of what was backed up
        summary = ", ".join(
            [f"{count} {table}" for table, count in record_counts.items()]
        )
        logger.info(f"Backup ZIP created with: {summary}")

        return True, zip_data, zip_filename

    except Exception as e:
        logger.error(f"Backup failed: {e}")
        import traceback

        traceback.print_exc()
        return False, None, str(e)
