import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# Load the prepared dataset.
# Keep spacex_launch_dash_prepared.csv in the same folder as this Python file.
spacex_df = pd.read_csv("spacex_launch_dash_prepared.csv")

# Make sure payload mass is numeric.
spacex_df["Payload Mass (kg)"] = pd.to_numeric(
    spacex_df["Payload Mass (kg)"], errors="coerce"
)
spacex_df = spacex_df.dropna(subset=["Launch Site", "Payload Mass (kg)", "class"])

# Set up the dashboard.
app = Dash(__name__)

# The supplied dataset has payloads up to 15,600 kg.
# Use the real maximum so the slider can include every record.
min_payload = 0
max_payload = int(
    ((spacex_df["Payload Mass (kg)"].max() + 999) // 1000) * 1000
)

app.layout = html.Div(
    style={"fontFamily": "Arial", "margin": "25px"},
    children=[
        html.H1("SpaceX Launch Records Dashboard"),
        html.Label("Select a launch site:"),
        dcc.Dropdown(
            id="site-dropdown",
            options=[
                {"label": "All Sites", "value": "ALL"}
            ] + [
                {"label": site, "value": site}
                for site in sorted(spacex_df["Launch Site"].unique())
            ],
            value="ALL",
            placeholder="Select a launch site",
            searchable=True,
            clearable=False
        ),
        dcc.Graph(id="success-pie-chart"),
        html.Label("Select payload mass range (kg):"),
        dcc.RangeSlider(
            id="payload-slider",
            min=min_payload,
            max=max_payload,
            step=1000,
            marks={i: str(i) for i in range(0, max_payload + 1, 1000)},
            value=[min_payload, max_payload],
            tooltip={"placement": "bottom", "always_visible": False}
        ),
        dcc.Graph(id="success-payload-scatter-chart")
    ]
)


# Update the pie chart when the launch-site dropdown changes.
@app.callback(
    Output("success-pie-chart", "figure"),
    Input("site-dropdown", "value")
)
def get_pie_chart(entered_site):
    if entered_site == "ALL":
        filtered_df = spacex_df
    else:
        filtered_df = spacex_df[spacex_df["Launch Site"] == entered_site]

    counts = (
        filtered_df["class"]
        .value_counts()
        .reindex([1, 0], fill_value=0)
    )

    figure = px.pie(
        names=["Successful", "Failed"],
        values=[int(counts.loc[1]), int(counts.loc[0])],
        title="Successful and Failed Launches",
        hole=0.25
    )
    return figure


# Update the scatter plot when the site or payload range changes.
@app.callback(
    Output("success-payload-scatter-chart", "figure"),
    [
        Input("site-dropdown", "value"),
        Input("payload-slider", "value")
    ]
)
def get_scatter_chart(entered_site, payload_range):
    filtered_df = spacex_df[
        (spacex_df["Payload Mass (kg)"] >= payload_range[0]) &
        (spacex_df["Payload Mass (kg)"] <= payload_range[1])
    ]

    if entered_site != "ALL":
        filtered_df = filtered_df[
            filtered_df["Launch Site"] == entered_site
        ]

    figure = px.scatter(
        filtered_df,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",
        hover_data=["Launch Site"],
        title="Payload Mass and Launch Outcome",
        labels={
            "class": "Launch outcome (1 = success, 0 = failure)",
            "Payload Mass (kg)": "Payload Mass (kg)"
        }
    )
    figure.update_yaxes(tickmode="array", tickvals=[0, 1])
    return figure


if __name__ == "__main__":
    print("Starting the SpaceX dashboard...")
    print("Open the local address shown below in your web browser.")
    app.run(debug=False)
