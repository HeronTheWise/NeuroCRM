import streamlit.components.v1 as components
import pandas as pd

def render_gantt(df):
    gantt_data = df.dropna(subset=["Start Date", "End Date"])
    if gantt_data.empty:
        return "No valid tasks to render."

    rows = []
    for i, row in gantt_data.iterrows():
        rows.append(f"""{{
            id: '{i}',
            name: '{row["Name"]}',
            actualStart: '{pd.to_datetime(row["Start Date"]).strftime('%Y-%m-%d')}',
            actualEnd: '{pd.to_datetime(row["End Date"]).strftime('%Y-%m-%d')}',
            description: 'Status: {row["Status"]}, Budget: ${row["Budget"]}'
        }}""")

    data_js = ",".join(rows)
    html = f"""
    <script src="https://cdn.anychart.com/releases/8.11.0/js/anychart-bundle.min.js"></script>
    <div id="container" style="width: 100%; height: 550px;"></div>
    <script>
        anychart.onDocumentReady(function () {{
            var data = [{data_js}];
            var chart = anychart.ganttProject();
            chart.data(data, "asTable");
            chart.title("Project Timeline");
            chart.container("container");
            chart.getTimeline().tooltip().useHtml(true);
            chart.getTimeline().tooltip().format(function() {{
                return '<b>' + this.name + '</b><br/>' + this.description;
            }});
            chart.draw();
        }});
    </script>
    """
    components.html(html, height=570)
