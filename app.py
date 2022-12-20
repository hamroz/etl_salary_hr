
import os
from dash import Dash, html, dcc, Input, Output
import sqlite3
import requests
import pandas as pd
import plotly.express as px
from bs4 import BeautifulSoup



external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
        "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]

app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.title = "Final Exam"

conn = sqlite3.connect("Final/hr")

main_query = pd.read_sql(
    "SELECT employees.first_name, jobs.job_title "
    + "FROM employees "
    + "INNER JOIN jobs ON employees.job_id "
    + "= jobs.job_id",
    conn,
)

income = pd.read_sql(
    "SELECT job_title, min_salary, max_salary FROM jobs", conn)

income.drop(index=0, axis=0, inplace=True)
job_titles = main_query.groupby("job_title").count().index


def exercise_1():
    from sqlalchemy import MetaData
    from sqlalchemy_schemadisplay import create_schema_graph

    graph = create_schema_graph(metadata=MetaData('sqlite:///Final/hr'),
                                rankdir='BT',
                                )
    graph.write_png('exercise_1.png')


def exercise_2(ex_2):
    emp_job = main_query

    if ex_2 == "All":
        cnt = emp_job.groupby("job_title").count().reset_index()
        cnt.columns = ["Job Title", "Count"]
    else:
        emp_job = emp_job[emp_job.job_title.isin(ex_2)]
        cnt = emp_job.groupby("job_title").count().reset_index()
        cnt.columns = ["Job Title", "Count"]

    fig = px.bar(cnt, x="Job Title", y="Count", color="Job Title")

    return fig


def exercise_3(min, max):

    inc_job = income
    inc_job["difference"] = inc_job["max_salary"] - \
        inc_job["min_salary"]
    diff = int(max) - int(min)
    inc_job = inc_job[inc_job["difference"] <= diff]
    fig = px.bar(
        inc_job, x=inc_job.difference, y=inc_job.job_title, orientation="h", color="job_title"
    )
    fig["layout"]["yaxis"]["title"] = "Job Title"
    fig["layout"]["xaxis"]["title"] = "Difference"

    return fig


def scrape_data():

    URL = "https://www.itjobswatch.co.uk/jobs/uk/sqlite.do"

    r = requests.get(URL)
    soup = BeautifulSoup(r.content, 'html5lib')
    t = soup.find('table', attrs={'class': 'summary'})
    t.find('form').decompose()
    td = t.tbody.find_all("tr")
    t = []

    for i in td:
        row = []
        r = i.find_all("td")
        if len(r) == 0:
            r = i.find_all("th")
        for j in r:
            row.append(j.text)
        t.append(row)

    hd = t[1]
    hd[0] = "index"
    emp_inc = pd.read_sql("SELECT employees.salary " +
                          "FROM employees", conn)
    avg = emp_inc['salary'].mean()
    df = pd.DataFrame(t)
    df.drop(index=[0, 1, 2, 3, 4, 5, 6, 7, 10,
            11, 14, 15], axis=0, inplace=True)
    df.columns = hd
    df.set_index("index", inplace=True)
    df.reset_index(inplace=True)

    df['Same period 2021'] = df['Same period 2021'].str.replace('£', '')
    df['Same period 2021'] = df['Same period 2021'].str.replace(',', '')
    df['Same period 2021'] = df['Same period 2021'].str.replace(
        '-', '0').astype(float)
    df['6 months to19 Dec 2022'] = df['6 months to19 Dec 2022'].str.replace(
        '£', '')
    df['6 months to19 Dec 2022'] = df['6 months to19 Dec 2022'].str.replace(
        ',', '').astype(float)
    df['Same period 2020'] = df['Same period 2020'].str.replace('£', '')
    df['Same period 2020'] = df['Same period 2020'].str.replace(
        ',', '').astype(float)

    df.loc[4] = ['Average', avg, avg, avg]

    return df


runner = scrape_data()

years = runner.columns


def exercise_4(year):
    dframe = runner[year]
    fig = px.scatter(
        x=runner["index"], y=dframe, color=["green", "green", "green", "green", "black"], color_discrete_map="identity", symbol=["green", "green", "green", "green", "black"]
    )
    fig.update_traces(marker_size=10)
    fig["layout"]["yaxis"]["title"] = "Count"
    fig["layout"]["xaxis"]["title"] = "Percentile"

    return fig


fig_plot = html.Div(id="fig_plot", style={"margin": "20px"},
                    children=[
    html.Div(
        children=[
            html.Div(
                    children=[
                        html.Div(children="Job Titles Filter",
                                 className="menu-title"),
                        dcc.Dropdown(
                            id="ex_2",
                            options=job_titles,
                            value="All",
                            multi=True,
                            className="dropdown",
                        ),
                    ]
                    ),
        ],
        className="menu",
        id='nav',
    ),
    dcc.Graph(id="graph_ex_2"),

    html.Div(
        children=[
            html.Div(
                children=[
                    html.Div(children="Salary Range",
                             className="menu-title"),
                    dcc.RangeSlider(0, 20000, 1000, value=[
                        0, 20000], id='ex_3'),
                ]
            ),
        ],
        className="menu1",
        id='nav',
    ),
    dcc.Graph(id="graph_ex_3"),

    html.Div(
        children=[
            html.Div(
                children=[
                    html.Div(children="",
                             className="menu-title"),
                    dcc.Dropdown(years[1:],

                                 value=years[-1],
                                 placeholder="6 months to19 Dec 2022",
                                 clearable=False,


                                 id="ex_4"
                                 ),
                ]
            ),
        ],
        className="menu2",
        id='nav',
    ),
    dcc.Graph(id="graph_ex_4"),

    html.Div(
        children=[
            html.Div(
                children=[
                    html.Div(children="Database Diagram",
                             className="menu-title"),
                    html.Img(src="assets/result.png", className="customImage")
                ]
            ),
        ],
        className="menu2",
        id='nav',
    ),

],
)

app.layout = html.Div(
    [
        html.Div(
            children=[
                html.P(children="🎬", className="header-emoji"),
                html.H1(
                    children="Final Exam", className="header-title"
                ),
                html.P(
                    children="Web Scrapping and much more...",
                    className="header-description",
                ),
            ],
            className="header",
        ),


        fig_plot,

    ]
)


@app.callback(
    [
        Output("graph_ex_2", "figure"),
        Output("graph_ex_3", "figure"),
        Output("graph_ex_4", "figure"),
    ],
    [
        Input("ex_2", "value"),
        Input("ex_3", "value"),
        Input('ex_4', 'value')

    ],
)
def update_output(ex_2, ex_3, ex_4):
    if ex_2 == None or len(ex_2) == 0:
        ex_2 = "All"

    i, n = 0, 1
    return exercise_2(ex_2), exercise_3(ex_3[i], ex_3[n]), exercise_4(ex_4)


if __name__ == "__main__":
    app.run_server("0.0.0.0", debug=False, port=int(os.environ.get("PORT", 8000)))
