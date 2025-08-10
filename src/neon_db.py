"""
Neon Database Management for Metal Evaporation History
Handles PostgreSQL database operations using psycopg2
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, fields
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MetalEvapData:
    """Pure data class for metal evaporation data entries"""

    user_id: int
    material_id: int
    date_recorded: str  # Format: 'YYYY-MM-DD'
    thickness: float
    threshold_pct: float
    deposition_pct: float
    dep_rate: float
    crystal_pct: float
    measured_thickness: Optional[float] = None
    notes: Optional[str] = None


class MetalEvapDB:
    """Database manager for metal evaporation data using Neon PostgreSQL"""

    def __init__(self):
        """Initialize database connection"""
        self.database_url = os.getenv("NEON_DATABASE_URL")
        if not self.database_url:
            raise ValueError("NEON_DATABASE_URL environment variable not set")

        self.connection = None
        self.connect()

    def connect(self):
        """Establish connection to the database"""
        try:
            self.connection = psycopg2.connect(
                self.database_url, cursor_factory=RealDictCursor, sslmode="require"
            )
            logger.info("Successfully connected to Neon database")
        except psycopg2.Error as e:
            logger.error(f"Error connecting to database: {e}")
            raise

    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - automatically disconnect"""
        self.disconnect()
        return False

    def execute_query(self, query: str, params: tuple = None, fetch: bool = False):
        """Execute a database query"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                if fetch:
                    result = cursor.fetchall()
                    self.connection.commit()  # Commit BEFORE returning
                    return result
                self.connection.commit()
                return cursor.rowcount
        except psycopg2.Error as e:
            self.connection.rollback()
            logger.error(f"Database error: {e}")
            raise

    def create_tables(self):
        """Create all necessary tables"""

        # Materials table (reference/lookup table)
        materials_table = """
        CREATE TABLE IF NOT EXISTS materials (
            id SERIAL PRIMARY KEY,
            material_name VARCHAR(100) NOT NULL UNIQUE,
            abbreviation VARCHAR(10) NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        # Users table
        users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            email VARCHAR(100) UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        # Tool data table (main table)
        tool_data_table = """
        CREATE TABLE IF NOT EXISTS tool_data (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            material_id INTEGER REFERENCES materials(id),
            date_recorded DATE NOT NULL,
            threshold_pct DECIMAL(5, 2),
            deposition_pct DECIMAL(5, 2),
            dep_rate DECIMAL(5, 2),
            thickness DECIMAL(8, 2) NOT NULL,
            measured_thickness DECIMAL(8, 2),
            crystal_pct DECIMAL(5, 2),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        try:
            # Create tables
            self.execute_query(materials_table)
            self.execute_query(users_table)
            self.execute_query(tool_data_table)

            logger.info("All tables created successfully")

        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise

    def populate_materials(self):
        """Populate materials table with common evaporation materials"""
        common_materials = [
            ("Gold", "Au"),
            ("Silver", "Ag"),
            ("Copper", "Cu"),
            ("Aluminum", "Al"),
            ("Titanium", "Ti"),
            ("Chromium", "Cr"),
            ("Platinum", "Pt"),
            ("Palladium", "Pd"),
            ("Nickel", "Ni"),
            ("Iron", "Fe"),
            ("Tungsten", "W"),
            ("Molybdenum", "Mo"),
            ("Tantalum", "Ta"),
            ("Silicon", "Si"),
            ("Silicon Dioxide", "SiO2"),
            ("Silicon Nitride", "SiN"),
            ("Aluminum Oxide", "Al2O3"),
            ("Germanium", "Ge"),
            ("Cobalt", "Co"),
            ("Nickel/Chrome", "Ni/Cr"),
        ]

        insert_query = """
        INSERT INTO materials (material_name, abbreviation)
        VALUES (%s, %s)
        ON CONFLICT (material_name) DO NOTHING;
        """

        try:
            for material_name, abbreviation in common_materials:
                self.execute_query(insert_query, (material_name, abbreviation))
            logger.info(
                f"Populated materials table with {len(common_materials)} materials"
            )
        except Exception as e:
            logger.error(f"Error populating materials: {e}")
            raise

    def _user_exists(self, first_name: str, last_name: str) -> bool:
        """Check if user already exists by first and last name"""
        query = """
        SELECT id FROM users 
        WHERE first_name = %s AND last_name = %s;
        """

        try:
            result = self.execute_query(query, (first_name, last_name), fetch=True)
            return len(result) > 0
        except Exception as e:
            logger.error(f"Error checking user existence: {e}")
            raise

    def add_user(
        self, first_name: str, last_name: str, email: Optional[str] = None
    ) -> int:
        """Add a new user and return the user ID. Raises ValueError if user already exists."""
        # Check if user already exists
        if self._user_exists(first_name, last_name):
            raise ValueError(
                f"User '{first_name} {last_name}' already exists in the database"
            )

        query = """
        INSERT INTO users (first_name, last_name, email)
        VALUES (%s, %s, %s)
        RETURNING id;
        """

        try:
            result = self.execute_query(
                query, (first_name, last_name, email), fetch=True
            )
            user_id = result[0]["id"]
            logger.info(f"Added user: {first_name} {last_name} (ID: {user_id})")
            return user_id
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            raise

    def get_material_id(self, material_name: str) -> Optional[int]:
        """Get material ID by name"""
        query = "SELECT id FROM materials WHERE material_name = %s;"

        try:
            result = self.execute_query(query, (material_name,), fetch=True)
            return result[0]["id"] if result else None
        except Exception as e:
            logger.error(f"Error getting material ID: {e}")
            raise

    def _evap_data_to_sql_insert(self, evap_data: MetalEvapData):
        """Generate SQL INSERT statement and values from MetalEvapData object"""
        # Get all field names and values (excluding None values for optional fields)
        field_data = {}
        for field in fields(evap_data):
            value = getattr(evap_data, field.name)
            if value is not None:
                field_data[field.name] = value

        columns = ", ".join(field_data.keys())
        placeholders = ", ".join(["%s"] * len(field_data))
        values = tuple(field_data.values())

        query = f"""
        INSERT INTO tool_data ({columns})
        VALUES ({placeholders})
        RETURNING id;
        """

        return query, values

    def add_evap_data(self, evap_data: MetalEvapData) -> int:
        """Add metal evaporation data entry using MetalEvapData object"""
        # Generate SQL automatically from MetalEvapData object
        query, values = self._evap_data_to_sql_insert(evap_data)

        try:
            result = self.execute_query(query, values, fetch=True)
            entry_id = result[0]["id"]
            logger.info(f"Added evap data entry (ID: {entry_id})")
            return entry_id
        except Exception as e:
            logger.error(f"Error adding evap data: {e}")
            raise

    def get_evap_data_by_user(self, user_id: int) -> List[Dict[Any, Any]]:
        """Get all evaporation data for a specific user"""
        query = """
        SELECT td.*, u.first_name, u.last_name, m.material_name, m.abbreviation
        FROM tool_data td
        JOIN users u ON td.user_id = u.id
        JOIN materials m ON td.material_id = m.id
        WHERE td.user_id = %s
        ORDER BY td.date_recorded DESC;
        """

        try:
            return self.execute_query(query, (user_id,), fetch=True)
        except Exception as e:
            logger.error(f"Error getting evap data: {e}")
            raise

    def add_material(self, material_name: str, abbreviation: str) -> int:
        """Add a new material and return the material ID"""
        query = """
        INSERT INTO materials (material_name, abbreviation)
        VALUES (%s, %s)
        RETURNING id;
        """

        try:
            result = self.execute_query(
                query, (material_name, abbreviation), fetch=True
            )
            material_id = result[0]["id"]
            logger.info(
                f"Added material: {material_name} ({abbreviation}) (ID: {material_id})"
            )
            return material_id
        except Exception as e:
            error_msg = str(e)
            # Check for duplicate material name constraint violation
            if (
                "materials_material_name_key" in error_msg
                or "duplicate key value" in error_msg
            ):
                raise ValueError(
                    f"Material '{material_name}' already exists in the database"
                )
            logger.error(f"Error adding material: {e}")
            raise

    def get_all_materials(self) -> List[Dict[Any, Any]]:
        """Get all available materials"""
        query = "SELECT * FROM materials ORDER BY material_name;"

        try:
            return self.execute_query(query, fetch=True)
        except Exception as e:
            logger.error(f"Error getting materials: {e}")
            raise

    def get_all_users(self) -> List[Dict[Any, Any]]:
        """Get all users"""
        query = "SELECT * FROM users ORDER BY last_name, first_name;"

        try:
            return self.execute_query(query, fetch=True)
        except Exception as e:
            logger.error(f"Error getting users: {e}")
            raise

    def get_all_tool_data_with_joins(self) -> List[Dict[Any, Any]]:
        """
        Get all tool data with material and user information
        Returns raw SQL result (list of dictionaries)
        """
        query = """
        SELECT 
            td.id as tool_data_id,
            td.user_id,
            td.material_id,
            td.date_recorded,
            CONCAT(u.first_name, ' ', u.last_name) as user_name,
            m.material_name,
            td.threshold_pct,
            td.deposition_pct,
            td.dep_rate,
            td.thickness,
            td.measured_thickness,
            td.crystal_pct,
            td.notes
        FROM tool_data td
        JOIN users u ON td.user_id = u.id
        JOIN materials m ON td.material_id = m.id
        ORDER BY td.date_recorded DESC
        """

        try:
            result = self.execute_query(query, fetch=True)
            logger.info(f"Retrieved {len(result) if result else 0} tool data records")
            return result
        except Exception as e:
            logger.error(f"Error getting tool data with joins: {e}")
            raise

    def clear_all_data(self):
        """Delete all data from all tables (but keep table structure)"""
        try:
            # Delete in correct order due to foreign key constraints
            # tool_data references users and materials, so delete it first
            self.execute_query("DELETE FROM tool_data;")
            self.execute_query("DELETE FROM users;")
            self.execute_query("DELETE FROM materials;")

            logger.info("All table data cleared successfully")

        except Exception as e:
            logger.error(f"Error clearing table data: {e}")
            raise

    def drop_all_tables(self):
        """Drop all tables completely (removes tables and all data)"""
        try:
            # Drop in correct order due to foreign key constraints
            self.execute_query("DROP TABLE IF EXISTS tool_data CASCADE;")
            self.execute_query("DROP TABLE IF EXISTS users CASCADE;")
            self.execute_query("DROP TABLE IF EXISTS materials CASCADE;")

            logger.info("All tables dropped successfully")

        except Exception as e:
            logger.error(f"Error dropping tables: {e}")
            raise

    def add_entry_from_widgets(
        self,
        user_name: str,  # Full name from dropdown
        material_name: str,  # Material name from dropdown
        thickness: float,
        threshold_pct: float,
        deposition_pct: float,
        dep_rate: float,
        crystal_pct: float,
        measured_thickness: Optional[float] = None,
        notes: Optional[str] = None,
        date_recorded: Optional[str] = None,  # Auto-assign if None
    ) -> int:
        """
        Add metal evaporation data entry from widget inputs
        Returns the ID of the created entry
        """
        from datetime import date

        # Auto-assign current date if not provided
        if date_recorded is None:
            date_recorded = date.today().strftime("%Y-%m-%d")

        # Get user_id from user name
        user_id = self._get_user_id_by_name(user_name)
        if user_id is None:
            raise ValueError(f"User '{user_name}' not found in database")

        # Get material_id from material name
        material_id = self.get_material_id(material_name)
        if material_id is None:
            raise ValueError(f"Material '{material_name}' not found in database")

        # Create MetalEvapData object
        evap_data = MetalEvapData(
            user_id=user_id,
            material_id=material_id,
            date_recorded=date_recorded,
            thickness=thickness,
            threshold_pct=threshold_pct,
            deposition_pct=deposition_pct,
            dep_rate=dep_rate,
            crystal_pct=crystal_pct,
            measured_thickness=measured_thickness,
            notes=notes,
        )

        # Add to database using existing method
        return self.add_evap_data(evap_data)

    def _get_user_id_by_name(self, user_name: str) -> Optional[int]:
        """Get user ID by full name (first_name + ' ' + last_name)"""
        query = """
        SELECT id FROM users 
        WHERE CONCAT(first_name, ' ', last_name) = %s;
        """

        try:
            result = self.execute_query(query, (user_name,), fetch=True)
            return result[0]["id"] if result else None
        except Exception as e:
            logger.error(f"Error getting user ID by name: {e}")
            raise

    def get_user_names_for_dropdown(self) -> List[str]:
        """Get list of user names formatted for dropdown (first_name + ' ' + last_name)"""
        query = """
        SELECT CONCAT(first_name, ' ', last_name) as full_name
        FROM users 
        ORDER BY last_name, first_name;
        """

        try:
            result = self.execute_query(query, fetch=True)
            return [row["full_name"] for row in result] if result else []
        except Exception as e:
            logger.error(f"Error getting user names: {e}")
            raise

    def update_tool_data(
        self,
        tool_data_id: int,
        user_name: str,
        material_name: str,
        date_recorded: str,
        thickness: float,
        threshold_pct: float,
        deposition_pct: float,
        dep_rate: float,
        crystal_pct: float,
        measured_thickness: Optional[float] = None,
        notes: Optional[str] = None,
    ) -> bool:
        """
        Update an existing tool data entry - reuses add_entry_from_widgets logic
        Same parameters as add_entry_from_widgets but updates instead of inserts
        """
        # Reuse all the validation logic from add_entry_from_widgets
        user_id = self._get_user_id_by_name(user_name)
        if user_id is None:
            raise ValueError(f"User '{user_name}' not found in database")

        material_id = self.get_material_id(material_name)
        if material_id is None:
            raise ValueError(f"Material '{material_name}' not found in database")

        # Create MetalEvapData object (same as add_entry_from_widgets)
        evap_data = MetalEvapData(
            user_id=user_id,
            material_id=material_id,
            date_recorded=date_recorded,
            thickness=thickness,
            threshold_pct=threshold_pct,
            deposition_pct=deposition_pct,
            dep_rate=dep_rate,
            crystal_pct=crystal_pct,
            measured_thickness=measured_thickness,
            notes=notes,
        )

        # Generate UPDATE query using same logic as _evap_data_to_sql_insert
        field_data = {}
        for field in fields(evap_data):
            value = getattr(evap_data, field.name)
            if value is not None:
                field_data[field.name] = value

        update_assignments = [f"{field} = %s" for field in field_data.keys()]
        values = list(field_data.values()) + [tool_data_id]

        query = f"""
        UPDATE tool_data 
        SET {", ".join(update_assignments)}
        WHERE id = %s;
        """

        try:
            rows_affected = self.execute_query(query, tuple(values))
            if rows_affected > 0:
                logger.info(f"Updated tool data entry ID: {tool_data_id}")
                return True
            else:
                logger.warning(f"No tool data entry found with ID: {tool_data_id}")
                return False
        except Exception as e:
            logger.error(f"Error updating tool data: {e}")
            raise


def main():
    """Example usage and testing"""
    try:
        # Initialize database
        db = MetalEvapDB()

        # Create tables
        db.create_tables()

        # Populate materials
        db.populate_materials()

        print("✅ Database setup complete!")
        print("✅ Tables created successfully")
        print("✅ Materials populated")

        # Example usage
        print("\n--- Example Usage ---")

        # Add a test user
        user_id = db.add_user("Test", "User", "test@example.com")
        print(f"✅ Added test user (ID: {user_id})")

        # Get material ID for Gold
        gold_material_id = db.get_material_id("Gold")

        # Create MetalEvapData object
        tool_data = MetalEvapData(
            user_id=user_id,
            material_id=gold_material_id,
            date_recorded="2025-01-24",
            thickness=100.0,
            threshold_pct=15.5,
            deposition_pct=85.2,
            dep_rate=2.5,
            measured_thickness=98.5,
            crystal_pct=92.1,
            notes="Test deposition run",
        )

        # Add evap data using the MetalEvapData object
        db.add_evap_data(tool_data)
        print("✅ Added test evap data")

        # Query data
        data = db.get_evap_data_by_user(user_id)
        print(f"✅ Retrieved {len(data)} evap data entries")

        # Close connection
        db.disconnect()

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
