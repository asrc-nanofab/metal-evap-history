"""
Data service for retrieving and processing metal evaporation data
Separates data logic from presentation logic
"""

import pandas as pd
from src.neon_db import MetalEvapDB
import logging

logger = logging.getLogger(__name__)


def format_tool_data_for_view(raw_result: list) -> pd.DataFrame:
    """
    Format raw SQL result into DataFrame for view display
    Converts database column names to display-friendly names

    Args:
        raw_result: Raw SQL result (list of dictionaries) from database

    Returns:
        Formatted DataFrame with display-friendly column names
    """
    if not raw_result:
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

    # Convert raw SQL result to DataFrame
    raw_df = pd.DataFrame(raw_result)

    # Format to match expected structure
    formatted_df = pd.DataFrame()
    formatted_df["Date"] = pd.to_datetime(raw_df["date_recorded"])
    formatted_df["Material"] = raw_df["material_name"]
    formatted_df["Threshold_Power"] = raw_df["threshold_pct"]
    formatted_df["Power_Deposition"] = raw_df["deposition_pct"]
    formatted_df["Rate"] = raw_df["dep_rate"]
    formatted_df["Thickness"] = raw_df["thickness"]
    formatted_df["Crystal_Monitor"] = raw_df["crystal_pct"]

    return formatted_df


def get_view_data():
    """
    Retrieve and format tool data for view display
    Returns a pandas DataFrame formatted for the view data page
    """
    try:
        with MetalEvapDB() as db:
            raw_result = db.get_all_tool_data_with_joins()
            return format_tool_data_for_view(raw_result)
    except Exception as e:
        logger.error(f"Error retrieving view data: {e}")
        raise  # Re-raise the exception to not hide the problem
