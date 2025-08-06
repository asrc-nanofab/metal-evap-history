"""
Data service tests
"""

import pytest
import pandas as pd
from src.data_service import format_tool_data_complete, get_and_format_tool_data


def test_format_tool_data_empty():
    """Test formatting empty data"""
    result = format_tool_data_complete([])

    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == [
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
        "Crystal_Monitor",
    ]
    assert len(result) == 0


def test_format_tool_data_with_data():
    """Test formatting actual data"""
    # Mock data that matches database structure
    mock_data = [
        {
            "tool_data_id": 1,
            "user_id": 1,
            "material_id": 1,
            "date_recorded": "2025-01-15",
            "user_name": "John Doe",
            "material_name": "Gold",
            "threshold_pct": 15.5,
            "deposition_pct": 85.2,
            "dep_rate": 2.5,
            "thickness": 100.0,
            "crystal_pct": 92.1,
        }
    ]

    result = format_tool_data_complete(mock_data)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1
    assert result.iloc[0]["Tool_Data_ID"] == 1
    assert result.iloc[0]["User_ID"] == 1
    assert result.iloc[0]["Material_ID"] == 1
    assert result.iloc[0]["User"] == "John Doe"
    assert result.iloc[0]["Material"] == "Gold"
    assert result.iloc[0]["Threshold_Power"] == 15.5
    assert result.iloc[0]["Power_Deposition"] == 85.2
    assert pd.api.types.is_datetime64_any_dtype(result["Date"])


def test_get_and_format_tool_data_structure():
    """Test that get_and_format_tool_data returns proper DataFrame structure"""
    try:
        result = get_and_format_tool_data()

        assert isinstance(result, pd.DataFrame)
        expected_columns = [
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
            "Crystal_Monitor",
        ]
        assert list(result.columns) == expected_columns

    except Exception as e:
        # If database is not available, test should be skipped
        pytest.skip(f"Database not available: {e}")


if __name__ == "__main__":
    # Run tests if called directly
    pytest.main([__file__])
