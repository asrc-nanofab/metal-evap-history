"""
Database tests and debugging utilities
"""

import pytest
import logging
from src.neon_db import MetalEvapDB

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def debug_database_contents():
    """
    Debug function to check what's actually in the database
    """
    try:
        with MetalEvapDB() as db:
            # Check materials
            materials_query = "SELECT * FROM materials"
            materials = db.execute_query(materials_query, fetch=True)
            logger.info(
                f"Materials table: {len(materials) if materials else 0} records"
            )
            if materials:
                logger.info(f"Materials: {materials}")

            # Check users
            users_query = "SELECT * FROM users"
            users = db.execute_query(users_query, fetch=True)
            logger.info(f"Users table: {len(users) if users else 0} records")
            if users:
                logger.info(f"Users: {users}")

            # Check tool_data
            tool_data_query = "SELECT * FROM tool_data"
            tool_data = db.execute_query(tool_data_query, fetch=True)
            logger.info(
                f"Tool_data table: {len(tool_data) if tool_data else 0} records"
            )
            if tool_data:
                logger.info(
                    f"Sample tool_data: {tool_data[:3] if len(tool_data) > 3 else tool_data}"
                )

    except Exception as e:
        logger.error(f"Error debugging database: {e}")


# Test functions
def test_database_connection():
    """Test that we can connect to the database"""
    try:
        with MetalEvapDB() as db:
            # Test basic connection
            assert db.connection is not None
            logger.info("✅ Database connection test passed")
    except Exception as e:
        pytest.fail(f"Database connection failed: {e}")


def test_tables_exist():
    """Test that all required tables exist"""
    try:
        with MetalEvapDB() as db:
            # Test materials table
            materials = db.get_all_materials()
            assert isinstance(materials, list)
            logger.info(f"✅ Materials table exists with {len(materials)} records")

            # Test users table
            users = db.get_all_users()
            assert isinstance(users, list)
            logger.info(f"✅ Users table exists with {len(users)} records")

            # Test tool_data table
            tool_data = db.get_all_tool_data_with_joins()
            assert isinstance(tool_data, list)
            logger.info(f"✅ Tool_data table exists with {len(tool_data)} records")

    except Exception as e:
        pytest.fail(f"Table existence test failed: {e}")


def test_data_integrity():
    """Test that data relationships are intact"""
    try:
        with MetalEvapDB() as db:
            # Get all tool data with joins
            tool_data = db.get_all_tool_data_with_joins()

            if tool_data:
                # Check that each record has required fields
                for record in tool_data:
                    assert "date_recorded" in record
                    assert "material_name" in record
                    assert "threshold_pct" in record
                    assert "deposition_pct" in record
                    assert "dep_rate" in record
                    assert "thickness" in record
                    assert "crystal_pct" in record

                logger.info(
                    f"✅ Data integrity test passed for {len(tool_data)} records"
                )
            else:
                logger.info("✅ Data integrity test passed (no data to test)")

    except Exception as e:
        pytest.fail(f"Data integrity test failed: {e}")


if __name__ == "__main__":
    # Run debug function if called directly
    debug_database_contents()
