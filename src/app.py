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

reference_lines = {'OII': 3727, 'H\u03B4': 4101, 'H\u03B2': 4861, 'OIII': 5007, 'H\u03B1': 6563}

app = Dash(external_stylesheets=[dbc.themes.LUX])

controls = dbc.Card(
    [
        html.Div(
            [
                html.H4("Select Galaxy:"),
                dcc.Dropdown(id="dropdown", options=sample_all['ID'], value="A370_01", clearable=False),
            ]
        ),
        html.Div(
            [
                dbc.Label("Box Filter Width"),
                dcc.Slider(1, 20, 1, marks={1: '1', 5: '5', 10: '10', 15: '15', 20: '20'}, value=1, id='width_slider'),
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
            align="top",
        ),
    ],
    fluid=True,
)

def box_filter(wl_in, flux_in, box_width=3):

    wl_out = np.array([np.mean(wl_in[i:i+box_width]) for i in range(len(wl_in)-box_width)])
    flux_out = np.array([np.mean(flux_in[i:i + box_width]) for i in range(len(flux_in) - box_width)])

    return wl_out, flux_out

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
    Input("width_slider", "value"),
)


def plot_integrated_spectra(galaxy, box_width):

    galaxy_index = np.argwhere(sample_all['ID'] == galaxy)[0][0]

    redshift = sample_all['z'][galaxy_index]

    file_name = galaxy + '.csv'

    spectra = pd.read_csv(spectra_dir / file_name)

    wl_plot, flux_plot15 = box_filter(spectra['Wavelength'][spectra['Contour Limit'] == 1.5], spectra['Flux'][spectra['Contour Limit'] == 1.5], box_width)
    flux_plot3 = box_filter(spectra['Wavelength'][spectra['Contour Limit'] == 3], spectra['Flux'][spectra['Contour Limit'] == 3], box_width)[1]
    flux_plot5 = box_filter(spectra['Wavelength'][spectra['Contour Limit'] == 5], spectra['Flux'][spectra['Contour Limit'] == 5], box_width)[1]

    labels = [np.full_like(wl_plot, '1.5'), np.full_like(wl_plot, '3'), np.full_like(wl_plot, '5')]
    labels = np.concatenate(labels)
    wl_all = np.concatenate([wl_plot, wl_plot, wl_plot])
    flux_all = np.concatenate([flux_plot15, flux_plot3, flux_plot5])

    plot_df = pd.DataFrame({'Wavelength': wl_all, 'Flux': flux_all, 'Contour Limit': labels})

    fig = px.line(data_frame=plot_df,
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
    Input("width_slider", "value"),
)


def plot_integrated_spectra_restframe(galaxy, box_width):

    galaxy_index = np.argwhere(sample_all['ID'] == galaxy)[0][0]

    redshift = sample_all['z'][galaxy_index]

    file_name = galaxy + '_restframe.csv'

    spectra = pd.read_csv(spectra_dir / file_name)

    wl_plot, flux_plot15 = box_filter(spectra['Wavelength'][spectra['Contour Limit'] == 1.5], spectra['Flux'][spectra['Contour Limit'] == 1.5], box_width)
    flux_plot3 = box_filter(spectra['Wavelength'][spectra['Contour Limit'] == 3], spectra['Flux'][spectra['Contour Limit'] == 3], box_width)[1]
    flux_plot5 = box_filter(spectra['Wavelength'][spectra['Contour Limit'] == 5], spectra['Flux'][spectra['Contour Limit'] == 5], box_width)[1]

    labels = [np.full_like(wl_plot, '1.5'), np.full_like(wl_plot, '3'), np.full_like(wl_plot, '5')]
    labels = np.concatenate(labels)
    wl_all = np.concatenate([wl_plot, wl_plot, wl_plot])
    flux_all = np.concatenate([flux_plot15, flux_plot3, flux_plot5])

    plot_df = pd.DataFrame({'Wavelength': wl_all, 'Flux': flux_all, 'Contour Limit': labels})

    fig = px.line(data_frame=plot_df,
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
    app.run_server(debug=True)