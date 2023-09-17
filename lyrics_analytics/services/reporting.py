import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go


def create_histogram(
    data: list[dict],
    metric_field: str,
    category_field: str,
    title: str,
    category_label: str = "",
) -> str:
    df = pd.DataFrame(data)

    labels = {
        category_field: f"{category_label} {category_field}",
        metric_field: metric_field.replace("_", " ").title(),
    }

    fig = px.histogram(
        df,
        x=metric_field,
        color=category_field,
        marginal="violin",
        hover_data=df.columns,
        nbins=20,
        barmode="overlay",
        labels=labels,
        title=title,
    )
    fig.update_layout(legend=dict(yanchor="top", y=-0.2, xanchor="left", x=0.0))

    return fig.to_html(include_plotlyjs=True, full_html=False)
