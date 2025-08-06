"""
Data service for retrieving and processing metal evaporation data
Separates data logic from presentation logic
"""

import pandas as pd
from src.neon_db import MetalEvapDB
import logging

logger = logging.getLogger(__name__)


def get_view_data():
    """
    Retrieve all tool data with material and user information from database
    Returns a pandas DataFrame formatted for the view data page
    """
    try:
        with MetalEvapDB() as db:
            # Get all tool data with material and user information
            query = """
            SELECT 
                td.date_recorded,
                CONCAT(u.first_name, ' ', u.last_name) as user_name,
                m.material_name,
                td.threshold_pct,
                td.deposition_pct,
                td.dep_rate,
                td.thickness,
                td.crystal_pct
            FROM tool_data td
            JOIN users u ON td.user_id = u.id
            JOIN materials m ON td.material_id = m.id
            ORDER BY td.date_recorded DESC
            """
            result = db.execute_query(query, fetch=True)

            logger.info(
                f"Retrieved {len(result) if result else 0} records from database"
            )

            if not result:
                logger.warning("No data found in database")
                return pd.DataFrame(
                    columns=[
                        "Date",
                        "Material",
                        "Threshold_Power",
                        "Power_Deposition",
                        "Rate",
                        "Thickness",
                        "Crystal_Monitor",
                    ]
                )

            # Convert to DataFrame
            df = pd.DataFrame(result)

            # Debug: print what we got
            logger.info(f"DataFrame columns: {df.columns.tolist()}")
            logger.info(f"DataFrame shape: {df.shape}")
            if not df.empty:
                logger.info(f"Sample data:\n{df.head()}")

            # Format to match expected structure
            formatted_df = pd.DataFrame()
            formatted_df["Date"] = pd.to_datetime(df["date_recorded"])
            formatted_df["Material"] = df["material_name"]
            formatted_df["Threshold_Power"] = df["threshold_pct"]
            formatted_df["Power_Deposition"] = df["deposition_pct"]
            formatted_df["Rate"] = df["dep_rate"]
            formatted_df["Thickness"] = df["thickness"]
            formatted_df["Crystal_Monitor"] = df["crystal_pct"]

            return formatted_df

    except Exception as e:
        logger.error(f"Error retrieving view data: {e}")
        # Return empty DataFrame with expected columns on error
        return pd.DataFrame(
            columns=[
                "Date",
                "Material",
                "Threshold_Power",
                "Power_Deposition",
                "Rate",
                "Thickness",
                "Crystal_Monitor",
            ]
        )


def get_available_materials():
    """
    Get list of available materials from database
    Returns sorted list of material names
    """
    try:
        with MetalEvapDB() as db:
            materials_data = db.get_all_materials()
            logger.info(f"Retrieved {len(materials_data)} materials")
            return sorted([mat["material_name"] for mat in materials_data])
    except Exception as e:
        logger.error(f"Error retrieving materials: {e}")
        return []


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
