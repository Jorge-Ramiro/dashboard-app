import plotly.express as px
from dash import dcc, html, Dash, Input, Output
import pandas as pd
from dash.exceptions import PreventUpdate
import requests

data = pd.read_csv("data/denue_inegi.csv")

repo_url = 'https://raw.githubusercontent.com/angelnmara/geojson/master/mexicoHigh.json'
mx_regions_geo = requests.get(repo_url).json()

def corrected_state(dataframe):
    dataframe['entidad'] = dataframe['entidad'].apply(
        lambda x: 'Veracruz' if 'Veracruz' in x else ('Coahuila' if 'Coahuila' in x else ('Michoacán' if 'Michoacán' in x else x)))
    return dataframe


app = Dash(__name__)

app.layout = html.Div(
    className='content',
    children=[
        # div that contains the title, slider dropdown and radiobuttons
        html.Div(
            className='Top-content',
            children=[
                # title div
                html.Div(
                    className='title-content',
                    children=[
                        html.H1(children='Manufacturing industries registered in Mexico by INEGI')
                    ]),
                    # slider div
                html.Div(
                    className='slider-content',
                    children=[
                        html.P(id='title-slider', children=['Drag the slider to change the year:']),
                        dcc.Slider(
                            id='year-slider',
                            min=data['registration year'].min(),
                            max=data['registration year'].max(),
                            value=data['registration year'].min(),
                            marks={str(year): {'label': str(year), 'style': {'color': '#7fafdf'}} for year in data['registration year'].unique()},
                            step=None)
                    ]),
                    # div that contains the dropdown and radiobottoms
                html.Div(
                    className='widgets',
                    children=[
                        # regions dropdown
                        dcc.Dropdown(
                            id='memory-regions',
                            options=[{'label': i, 'value': i} for i in data.region.unique()],
                            placeholder="Select a region", searchable=False, value='norte'),
                        # radiobuttons
                        dcc.RadioItems(
                            id='top-type',
                            options=[{'label': i, 'value': i} for i in ['Top 3', 'Top 5']],
                            value='Top 3', inline=True)
                    ])
            ]),
            # map div
        html.Div(
            className='map-graph',
            children=[
                dcc.Graph(id='MapGraph', hoverData={'points': [{'customdata': 1}]})
            ]),
            # bar graphic div
        html.Div(
            className='bar-graph',
            children=[
                dcc.Graph(id='BarGraph'),
                dcc.Graph(id='RegionPie')
            ])
        ])

@app.callback(
    Output(component_id='MapGraph', component_property='figure'),
    Input(component_id='year-slider', component_property='value')
)
def update_map(selected_year):
    filtered_data = data[data['registration year'] == selected_year].groupby(['cve_ent', 'entidad'], as_index=False).size().rename({'size':'total'}, axis=1)
    corrected_data = corrected_state(filtered_data)
    fig = px.choropleth_mapbox(data_frame=corrected_data, geojson=mx_regions_geo, featureidkey='properties.name', locations='entidad',
                                color='total', opacity=0.8, color_continuous_scale="Blugrn", mapbox_style='carto-darkmatter',
                                center= {'lat': 24, 'lon': -102}, zoom=3.74, hover_name='entidad') #  width=718, height=532,

    fig.update_traces(customdata=corrected_data['cve_ent'])
    fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)'}, margin={"l":0,"t":35,"r":0,"b":0})
    fig.update_layout(title='Heatmap of Total manufacturing industries per year and state', font=dict(color='#53f9ae'))

    return fig


@app.callback(
    Output('BarGraph', 'figure'),
    [Input('MapGraph', 'hoverData'),
    Input('top-type', 'value')]
)
def update_bGraph(hoverData, selected_top):
    state_name = hoverData['points'][0]['customdata']
    top = 3 if selected_top == 'Top 3' else 5

    filtered_data = data[data['cve_ent'] == state_name].loc[:,['nombre_act','codigo_act']].value_counts().reset_index()[:top]
    filtered_data['codigo_act'] = filtered_data['codigo_act'].astype(str)
    
    fig = px.bar(filtered_data, x='codigo_act', y=0, color='nombre_act',
    labels={'0':'total number of registers', 'codigo_act': 'activity code', 'nombre_act':'activity name'})

    fig.update_yaxes(showline=True, linewidth=2, linecolor='black', color='#53f9ae')
    fig.update_xaxes(showline=True, linewidth=2, linecolor='black', color= '#53f9ae')
    fig.update_layout({'plot_bgcolor':'#1f2630', 'paper_bgcolor': 'rgba(0, 0, 0, 0)'}, 
    title_text= data[data['cve_ent'] == state_name]['entidad'].values[0], showlegend=False,
    font=dict(color='#53f9ae'))  

    return fig


@app.callback(
    Output('RegionPie', 'figure'),
    [Input('memory-regions', 'value'),
    Input('top-type', 'value')]
)
def updateRegionsPie(selected_region, top):
    translated_region = ''
    if selected_region == 'centro':
        translated_region = 'Center'
    
    elif selected_region == 'norte':
        translated_region = 'North'

    elif selected_region == 'sur':
        translated_region = 'South'
    else:
        raise PreventUpdate
    
    filtered_data = data[data['region'] == selected_region]
    
    filtered_df = filtered_data.groupby(['nombre_act'], as_index=False).size().rename(columns={'nombre_act':'activity_name', 'size':'total_registers'}).sort_values('total_registers', ascending=False)[:int(top[-1])]

    fig = px.pie(filtered_df, values='total_registers', names='activity_name') #width=586, height=270
    fig.update_layout(margin={"r":0,"t":32,"l":0,"b":0})
    fig.update_layout(showlegend=False)
    fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)'}, 
    title='Total % of activity names with the most registrations in the region: {}'.format(translated_region), title_y=0.95, title_x=0,
    font=dict(size=11.5, color='#53f9ae'))
    fig.update_traces(textfont_size=14)
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)