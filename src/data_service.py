"""
Data service for retrieving and processing metal evaporation data
Separates data logic from presentation logic
"""

import pandas as pd
from src.neon_db import MetalEvapDB
import logging

logger = logging.getLogger(__name__)


def format_tool_data_complete(raw_result: list) -> pd.DataFrame:
    """
    Format raw SQL result into complete DataFrame with ALL columns
    Single source of truth for data formatting

    Args:
        raw_result: Raw SQL result (list of dictionaries) from database

    Returns:
        Formatted DataFrame with all columns from database query including measured_thickness
    """
    if not raw_result:
        logger.warning("No data found in database")
        return pd.DataFrame(
            columns=[
                "Tool_Data_ID",
                "User_ID",
                "Material_ID",
                "Date",
                "User",
                "Material",
                "Threshold_Power",
                "Power_Deposition",
                "Rate",
                "Thickness",
                "Measured_Thickness",
                "Crystal_Monitor",
            ]
        )

    # Convert raw SQL result to DataFrame
    raw_df = pd.DataFrame(raw_result)

    # Format to match expected structure (ALL columns)
    formatted_df = pd.DataFrame()
    formatted_df["Tool_Data_ID"] = raw_df["tool_data_id"]
    formatted_df["User_ID"] = raw_df["user_id"]
    formatted_df["Material_ID"] = raw_df["material_id"]
    formatted_df["Date"] = pd.to_datetime(raw_df["date_recorded"])
    formatted_df["User"] = raw_df["user_name"]
    formatted_df["Material"] = raw_df["material_name"]
    formatted_df["Threshold_Power"] = raw_df["threshold_pct"]
    formatted_df["Power_Deposition"] = raw_df["deposition_pct"]
    formatted_df["Rate"] = raw_df["dep_rate"]
    formatted_df["Thickness"] = raw_df["thickness"]
    formatted_df["Measured_Thickness"] = raw_df["measured_thickness"]
    formatted_df["Crystal_Monitor"] = raw_df["crystal_pct"]

    return formatted_df


def get_and_format_tool_data():
    """
    Retrieve and format all tool data from database
    Returns complete pandas DataFrame with all columns
    """
    try:
        with MetalEvapDB() as db:
            raw_result = db.get_all_tool_data_with_joins()
            return format_tool_data_complete(raw_result)
    except Exception as e:
        logger.error(f"Error retrieving tool data: {e}")
        raise  # Re-raise the exception to not hide the problem
