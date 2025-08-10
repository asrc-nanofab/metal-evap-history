"""
Graphing utilities for metal evaporation data visualization
Contains different chart types and visualization functions
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from typing import Optional
import streamlit as st


# Available chart types for UI selection
CHART_TYPES = {
    "histogram": "Histogram (Value Distributions)",
    "box": "Box Plot (Distribution by Date)",
    "line": "Line Plot (Trends Over Time)",
    "scatter": "Scatter Plot (Deposition vs Threshold)",
    # "matplotlib_line": "Line Plot (Matplotlib)",
}


def create_power_box_plot(
    data: pd.DataFrame,
    material: str,
    title: Optional[str] = None,
    height: int = 500,
    show_points: bool = True,
) -> go.Figure:
    """
    Create a box plot showing power distribution by date

    Args:
        data: DataFrame with Date, Power_Deposition, Threshold_Power columns
        material: Material name for title
        title: Custom title (optional)
        height: Chart height in pixels
        show_points: Whether to show individual data points

    Returns:
        Plotly figure object
    """
    if data.empty:
        # Return empty figure if no data
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    # Prepare data for box plot
    df_plot = data.copy()

    # Convert Date to string for better box plot grouping
    if pd.api.types.is_datetime64_any_dtype(df_plot["Date"]):
        df_plot["Date_Str"] = df_plot["Date"].dt.strftime("%Y-%m-%d")
    else:
        df_plot["Date_Str"] = df_plot["Date"].astype(str)

    # Reshape data to long format for plotly
    df_long = pd.melt(
        df_plot,
        id_vars=["Date_Str"],
        value_vars=["Deposition (%)", "Threshold (%)"],
        var_name="Power_Type",
        value_name="Power",
    )

    # Rename for better legend
    df_long["Power_Type"] = df_long["Power_Type"].map(
        {
            "Deposition (%)": "Deposition Power",
            "Threshold (%)": "Threshold Power",
        }
    )

    # Create box plot
    fig = px.box(
        df_long,
        x="Date_Str",
        y="Power",
        color="Power_Type",
        points="all" if show_points else False,
        title=title or f"Power Distribution by Date for {material}",
        labels={
            "Date_Str": "Date",
            "Power": "Power (%)",
            "Power_Type": "Power Type",
        },
    )

    # Improve layout
    fig.update_layout(
        xaxis_tickangle=-45,
        height=height,
        showlegend=True,
        xaxis_title="Date",
        yaxis_title="Power (%)",
    )

    return fig


def create_power_line_plot(
    data: pd.DataFrame,
    material: str,
    title: Optional[str] = None,
    height: int = 500,
) -> go.Figure:
    """
    Create a line plot showing power trends over time

    Args:
        data: DataFrame with Date, Power_Deposition, Threshold_Power columns
        material: Material name for title
        title: Custom title (optional)
        height: Chart height in pixels

    Returns:
        Plotly figure object
    """
    if data.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    fig = go.Figure()

    # Add deposition power line
    fig.add_trace(
        go.Scatter(
            x=data["Date"],
            y=data["Deposition (%)"],
            mode="lines+markers",
            name="Deposition Power",
            line=dict(color="#1f77b4"),
            marker=dict(size=6),
        )
    )

    # Add threshold power line
    fig.add_trace(
        go.Scatter(
            x=data["Date"],
            y=data["Threshold (%)"],
            mode="lines+markers",
            name="Threshold Power",
            line=dict(color="#ff7f0e"),
            marker=dict(size=6),
        )
    )

    fig.update_layout(
        title=title or f"Power Trends Over Time for {material}",
        xaxis_title="Date",
        yaxis_title="Power (%)",
        height=height,
        hovermode="x unified",
    )

    return fig


def create_power_scatter_plot(
    data: pd.DataFrame,
    material: str,
    title: Optional[str] = None,
    height: int = 500,
    show_trendline: bool = True,
) -> go.Figure:
    """
    Create a scatter plot comparing deposition vs threshold power

    Args:
        data: DataFrame with Power_Deposition, Threshold_Power columns
        material: Material name for title
        title: Custom title (optional)
        height: Chart height in pixels

    Returns:
        Plotly figure object
    """
    if data.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    # Try to add trendline, fallback to no trendline if statsmodels not available
    try:
        if show_trendline:
            fig = px.scatter(
                data,
                x="Threshold (%)",
                y="Deposition (%)",
                title=title or f"Deposition vs Threshold Power for {material}",
                labels={
                    "Threshold (%)": "Threshold Power (%)",
                    "Deposition (%)": "Deposition Power (%)",
                },
                trendline="ols",  # Add trend line
            )
        else:
            raise ImportError("Trendline disabled")
    except ImportError:
        # Fallback to scatter plot without trendline if statsmodels not available
        fig = px.scatter(
            data,
            x="Threshold (%)",
            y="Deposition (%)",
            title=title or f"Deposition vs Threshold Power for {material}",
            labels={
                "Threshold (%)": "Threshold Power (%)",
                "Deposition (%)": "Deposition Power (%)",
            },
        )

    fig.update_layout(height=height)

    return fig


def create_power_histogram(
    data: pd.DataFrame,
    material: str,
    title: Optional[str] = None,
    height: int = 500,
) -> go.Figure:
    """
    Create histograms showing power value distributions

    Args:
        data: DataFrame with Power_Deposition, Threshold_Power columns
        material: Material name for title
        title: Custom title (optional)
        height: Chart height in pixels

    Returns:
        Plotly figure object
    """
    if data.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    # Create subplots
    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Threshold Power", "Deposition Power"),
        shared_yaxes=True,
    )

    # Add threshold power histogram
    fig.add_trace(
        go.Histogram(
            x=data["Threshold (%)"],
            name="Threshold Power",
            opacity=0.7,
            marker_color="#ff7f0e",
        ),
        row=1,
        col=1,
    )

    # Add deposition power histogram
    fig.add_trace(
        go.Histogram(
            x=data["Deposition (%)"],
            name="Deposition Power",
            opacity=0.7,
            marker_color="#1f77b4",
        ),
        row=1,
        col=2,
    )

    fig.update_layout(
        title_text=title or f"Power Distribution Histograms for {material}",
        height=height,
        showlegend=False,
    )

    fig.update_xaxes(title_text="Power (%)", row=1, col=1)
    fig.update_xaxes(title_text="Power (%)", row=1, col=2)
    fig.update_yaxes(title_text="Frequency", row=1, col=1)

    return fig


def create_matplotlib_line_plot(
    data: pd.DataFrame,
    material: str,
    title: Optional[str] = None,
    figsize: tuple = (10, 6),
) -> plt.Figure:
    """
    Create a matplotlib line plot (for comparison/legacy support)

    Args:
        data: DataFrame with Date, Power_Deposition, Threshold_Power columns
        material: Material name for title
        title: Custom title (optional)
        figsize: Figure size tuple

    Returns:
        Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)

    if data.empty:
        ax.text(
            0.5,
            0.5,
            "No data available",
            transform=ax.transAxes,
            ha="center",
            va="center",
        )
        return fig

    # Plot lines
    ax.plot(
        data["Date"],
        data["Deposition (%)"],
        label="Deposition Power",
        marker="o",
        linewidth=2,
    )
    ax.plot(
        data["Date"],
        data["Threshold (%)"],
        label="Threshold Power",
        marker="o",
        linewidth=2,
    )

    ax.set_xlabel("Date")
    ax.set_ylabel("Power (%)")
    ax.set_title(title or f"Power Trends for {material}")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)
    plt.tight_layout()

    return fig


# Utility function to display charts in Streamlit
def display_chart(chart_type: str, data: pd.DataFrame, material: str, **kwargs) -> None:
    """
    Display a chart in Streamlit based on type

    Args:
        chart_type: Type of chart ('box', 'line', 'scatter', 'histogram', 'matplotlib_line')
        data: DataFrame with chart data
        material: Material name
        **kwargs: Additional arguments for chart functions
    """
    if chart_type == "box":
        fig = create_power_box_plot(data, material, **kwargs)
        st.plotly_chart(fig, use_container_width=True)
    elif chart_type == "line":
        fig = create_power_line_plot(data, material, **kwargs)
        st.plotly_chart(fig, use_container_width=True)
    elif chart_type == "scatter":
        fig = create_power_scatter_plot(data, material, **kwargs)
        st.plotly_chart(fig, use_container_width=True)
    elif chart_type == "histogram":
        fig = create_power_histogram(data, material, **kwargs)
        st.plotly_chart(fig, use_container_width=True)
    elif chart_type == "matplotlib_line":
        fig = create_matplotlib_line_plot(data, material, **kwargs)
        st.pyplot(fig)
    else:
        st.error(f"Unknown chart type: {chart_type}")
