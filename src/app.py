'''

ariel@oapd
19/02/2024

'''

from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.io as pio
from pathlib import Path

pio.templates.default = 'plotly_white'

root_dir = Path(__file__).resolve().parent.parent

data_dir = root_dir / 'data/'
spectra_dir = root_dir / 'data/dashboard_data/'

sample_all = pd.read_csv(data_dir / 'all_galaxy_sample.csv')

reference_lines = {'OII': 3727, 'H\u03B7': 3836, 'H\u03B3': 4341, 'H\u03B4': 4101, 'H\u03B2': 4861, 'OIII': 5007, 'H\u03B1': 6563}

app = Dash(external_stylesheets=[dbc.themes.LUX])
server = app.server

controls = dbc.Card(
    [
        html.Div(
            [
                html.H4("Select Galaxy:"),
                dcc.Dropdown(id="dropdown", options=sample_all['ID'], value="A2744_01", clearable=False),
            ]
        ),
        html.Div(
            [   html.Div('Box Filter:'),
                dcc.RadioItems(['On', 'Off'], 'Off',
                               inline=True, id='box_filter')
            ]
        ),
        html.Div(
            [
                html.H4(id='data_summary_title'),
                html.Div(id='redshift'),
                html.Div(id="category"),
                html.Div(id="sinopsis_fraction"),
                html.Div(id="mag_disk"),
                html.Div(id="sn"),
                html.Div(id="sn_2"),
                html.Div(id="nad_notch")
            ]
        ),
    ],
    body=True,
)

spectra = dbc.Card(html.Div([dcc.Graph(id="observed_spectrum"), 
                             dcc.Graph(id="restframe_spectrum")]))

app.layout = dbc.Container(
    [
        html.H1("Checking Intermediate-z Sample Galaxies"),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(controls, md=4),
                dbc.Col(spectra, md=8),
            ],
            align="top left",
        ),
    ],
    fluid=True,
)


@app.callback(
    Output("data_summary_title", "children"),
    Output("redshift", "children"),
    Output("category", "children"),
    Output("sinopsis_fraction", "children"),
    Output("mag_disk", "children"),
    Output("sn", "children"),
    Output("sn_2", "children"),
    Output("nad_notch", "children"),
    Input("dropdown", "value"),
)


def get_galaxy_table(galaxy):

    galaxy_data = sample_all[sample_all['ID']==galaxy]

    return 'This is the data for ' + galaxy_data['ID'], 'Redshift: {z}'.format(z=galaxy_data['z'].values[0]), \
           'Category: ' + str(galaxy_data['Category'].values[0]), 'Sinopsis Fraction: {fraction:.2f}'.format(fraction=galaxy_data['sinopsis_fraction'].values[0]), \
           'g-band magnitude: {mag:.2f}'.format(mag=galaxy_data['mag_disk'].values[0]), 'S/N (5635): {sn:.2f}'.format(sn=galaxy_data['sn_5635'].values[0]), \
           'S/N (4050): {sn:.2f}'.format(sn=galaxy_data['sn_4050'].values[0]), 'NaD notch: ' + str(galaxy_data['nad_notch'].values[0]), 
            

@app.callback(
    Output("observed_spectrum", "figure"),
    Input("dropdown", "value"),
    Input("box_filter", "value"),
)


def plot_integrated_spectra(galaxy, box_filter):

    if box_filter == 'On':
        box_filter = True
    else:
        box_filter = False

    galaxy_index = np.argwhere(sample_all['ID'] == galaxy)[0][0]

    redshift = sample_all['z'][galaxy_index]

    if box_filter:
        file_name = galaxy + '_filtered.csv'
    else:
        file_name = galaxy + '.csv'

    spectra = pd.read_csv(spectra_dir / file_name)

    fig = px.line(data_frame=spectra,
                  x='Wavelength',
                  y='Flux',
                  color='Contour Limit',
        title='Integrated Spectrum (Observed Frame)',
    )

    for line in reference_lines.keys():
        fig.add_vline(x=reference_lines[line] * (1 + redshift), line_dash='dash', annotation_text=line, annotation_position='top right', line_width=0.75)

    fig.add_vrect(x0=(5635-75) * (1 + redshift), x1=(5635+75) * (1 + redshift), 
                annotation_text="S/N", annotation_position="top",
                fillcolor="green", opacity=0.25, line_width=0, col=1)
    
    fig.add_vrect(x0=(3995) * (1 + redshift), x1=(4075) * (1 + redshift), 
                annotation_text="S/N", annotation_position="top",
                fillcolor="green", opacity=0.25, line_width=0, col=1)


    if galaxy.split('_')[0] in ['MACS0257', 'RXJ1347', 'SMACS2131']:
        fig.add_vrect(x0=5760, x1=6010, annotation_text="NaD notch", annotation_position="top",
                      fillcolor="red", opacity=0.25, line_width=0)

    return fig


@app.callback(
    Output("restframe_spectrum", "figure"),
    Input("dropdown", "value"),
    Input("box_filter", "value"),
)


def plot_integrated_spectra_restframe(galaxy, box_filter):

    if box_filter == 'On':
        box_filter = True
    else:
        box_filter = False

    galaxy_index = np.argwhere(sample_all['ID'] == galaxy)[0][0]

    redshift = sample_all['z'][galaxy_index]

    if box_filter:
        file_name = galaxy + '_restframe_filtered.csv'
    else:
        file_name = galaxy + '_restframe.csv'

    spectra = pd.read_csv(spectra_dir / file_name)

    fig = px.line(data_frame=spectra,
                  x='Wavelength',
                  y='Flux',
                  color='Contour Limit',
        title='Integrated Spectrum (Rest Frame)',
    )

    for line in reference_lines.keys():
        fig.add_vline(x=reference_lines[line], line_dash='dash', annotation_text=line, annotation_position='top right', line_width=0.75)

    fig.add_vrect(x0=5635-75, x1=5635+75, 
                  annotation_text="S/N", annotation_position="top",
                  fillcolor="green", opacity=0.25, line_width=0, col=1)

    fig.add_vrect(x0=3995, x1=4075, 
                  annotation_text="S/N", annotation_position="top",
                  fillcolor="green", opacity=0.25, line_width=0, col=1)

    if galaxy.split('_')[0] in ['MACS0257', 'RXJ1347', 'SMACS2131']:
        fig.add_vrect(x0=5760 / (1 + redshift), x1=6010 / (1 + redshift), 
                      annotation_text="NaD notch", annotation_position="top",
                      fillcolor="red", opacity=0.25, line_width=0)

    return fig


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8080)