"""
Validation utilities for the deposition app.
"""

from typing import Dict, Any, Tuple
from pydantic import ValidationError
from models import DepositionEntry
import streamlit as st


def validate_entry_data(data: Dict[str, Any]) -> Tuple[bool, DepositionEntry, list]:
    """
    Validate entry data using Pydantic model.

    Returns:
        (is_valid, validated_data_or_none, error_messages)
    """
    try:
        validated_entry = DepositionEntry(**data)
        return True, validated_entry, []
    except ValidationError as e:
        error_messages = []
        for error in e.errors():
            field = error["loc"][0] if error["loc"] else "Unknown"
            message = error["msg"]
            error_messages.append(f"{field}: {message}")
        return False, None, error_messages


def display_validation_errors(errors: list):
    """Display validation errors in Streamlit."""
    if errors:
        st.error("Please fix the following validation errors:")
        for error in errors:
            st.error(f"• {error}")


def validate_and_show_errors(data: Dict[str, Any]) -> Tuple[bool, DepositionEntry]:
    """
    Validate data and display errors in Streamlit if any.

    Returns:
        (is_valid, validated_data_or_none)
    """
    is_valid, validated_data, errors = validate_entry_data(data)

    if not is_valid:
        display_validation_errors(errors)
        return False, None

    return True, validated_data
