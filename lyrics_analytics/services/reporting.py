import pandas as pd
import plotly.express as px


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
        template="plotly_dark",
    )
    fig.update_layout(legend=dict(yanchor="top", y=-0.2, xanchor="left", x=0.0))

    return fig.to_html(include_plotlyjs=True, full_html=False)


def dummy_plot():
    fig = px.scatter(x=[0, 1, 2, 3, 4], y=[0, 1, 4, 9, 16])
    return fig.to_html(include_plotlyjs=True, full_html=False)


def album_distribution(): ...

"""
df=pd.DataFrame(collection.find({}))
df['release_date'] = pd.to_datetime(df['release_date'])

# Group the DataFrame by the "album" column
album_grouped = df.groupby('album')

# Define a dictionary to specify the aggregation functions for each column
agg_functions = {
    'name': 'first',
    'release_date': 'max',             # Latest release date
    'lyrics_count': 'mean',            # Average lyrics count
    'distinct_count': 'mean'         # Average distinct count
}

# Use the agg method to apply aggregation functions to each column
album_info = album_grouped.agg(agg_functions)

# Reset the index to have "album" as a regular column
album_info.reset_index(inplace=True)
album_info
"""