import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from serve_modulus import (
    modulus_wrapper, 
    failure_wrapper, 
    get_modulus, 
    get_max_stress,
    get_failure_mode
)

app = dash.Dash(__name__, title='FDM laminate mechanics', 
                external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.CYBORG])

server = app.server   

def serve_layout():
    layout = html.Div([
        
        html.H1('Uniaxial composite mechanical design', id="app-title"),
        
        html.Div([
            
            html.Div([
                html.Div([
                    html.Div([], id="intro-image"),
                ], id="intro-wrapper"),
            ], id="intro", className="pannel"),
            
            html.Div([
                dcc.Tabs([
                    dcc.Tab(label='Elasticity', children=[
                        html.Div([
                            
                            dcc.Graph(id="elastic-plot", className="plot"),
                            
                            html.Div([
                                html.Div([
                                    html.H3('Material', className="pannel-header"),
                                    html.Div([
                                        html.Div([
                                            html.Label([
                                                dcc.Markdown(dangerously_allow_html=True, 
                                                            children="E<sub>1</sub>")
                                            ], htmlFor="e1-input", id="e1-label"),
                                            dcc.Input(type="number", value=70, min=0, id="e1-input")
                                        ], id="e1-container", className="input-container"),
                                        dbc.Tooltip('Elastic modulus - longitudinal (ex. fibers direction) [GPa]', target='e1-input', placement='top'),
                                        html.Div([
                                            html.Label([
                                                dcc.Markdown(dangerously_allow_html=True, 
                                                            children="E<sub>2</sub>")    
                                            ], htmlFor="e2-input", id="e2-label"),
                                            dcc.Input(type="number", value=30, min=0, id="e2-input")
                                        ], id="e2-container", className="input-container"),
                                        dbc.Tooltip('Elastic modulus - transverse [GPa]', target='e2-input', placement='top'),
                                        html.Div([
                                            html.Label("G", htmlFor="g-input", id="g-label"),
                                            dcc.Input(type="number", value=20, min=0, id="g-input")
                                        ], id="g-container", className="input-container"),
                                        dbc.Tooltip('Shear modulus [GPa]', target='g-input', placement='top'),
                                        html.Div([
                                            html.Label(u"\u03bd", htmlFor="mu-input", id="mu-label"),
                                            dcc.Input(type="number", value=0.3, min=0, max=0.99, step=0.01, id="mu-input")
                                        ], id="mu-container", className="input-container"),
                                        dbc.Tooltip('Poisson\'s ratio', target='mu-input', placement='top'),
                                    ], className="props-container"),
                                ], className="material-wrapper"),
                            ], className="material-pannel"),
                            
                            html.Div([
                                html.Div([
                                    html.H3(u"Theta (\u0398)", className="h3-subheader"),
                                    dcc.Slider(
                                        id='theta-elastic',
                                        min=0, max=90, step=5, value=0,
                                        tooltip={"placement": "bottom", "always_visible": True},
                                        updatemode='drag',
                                    ),
                                ], className="slider-wrapper"),                                
                            ], className="slider-pannel"),
                            
                        ], className="tab-wrapper"),                   
                    ]),
                    dcc.Tab(label='Strength', children=[
                        html.Div([  
                            dcc.Graph(id="failure-plot", className="plot"),
                            html.Div([
                                html.Div([
                                    html.H3('Material', className="pannel-header"),
                                    html.Div([
                                        html.Div([
                                            html.Label([
                                                dcc.Markdown(dangerously_allow_html=True, 
                                                            children=u"\u03c3<sub>1</sub>")    
                                            ], htmlFor="s1-input", id="s1-label"),
                                            dcc.Input(type="number", value=110, min=0, id="s1-input")
                                        ], id="s1-container", className="input-container"),
                                        dbc.Tooltip('Max stress - longitudinal [MPa]', target='s1-input', placement='top'),
                                        html.Div([
                                            html.Label([
                                                dcc.Markdown(dangerously_allow_html=True, 
                                                            children=u"\u03c3<sub>2</sub>")    
                                            ], htmlFor="s2-input", id="s2-label"),
                                            dcc.Input(type="number", value=60, min=0, id="s2-input")
                                        ], id="s2-container", className="input-container"),
                                        dbc.Tooltip('Max stress - transverse [MPa]', target='s2-input', placement='top'),
                                        html.Div([
                                            html.Label([
                                                dcc.Markdown(dangerously_allow_html=True, 
                                                            children=u"\u03c4<sub>12</sub>")    
                                            ], htmlFor="tau-input", id="tau-label"),
                                            dcc.Input(type="number", value=40, min=0, id="tau-input")
                                        ], id="tau-container", className="input-container"),
                                        dbc.Tooltip('Max shear stress [MPa]', target='tau-input', placement='top'),
                                    ], className="props-container"),
                                ], className="material-wrapper"),
                            ], className="material-pannel"),
                            
                            html.Div([
                                html.Div([
                                    html.H3(u'Theta (\u0398)', className="h3-subheader"),
                                    dcc.Slider(
                                        id='theta-failure',
                                        min=0, max=90, step=5, value=0,
                                        tooltip={"placement": "bottom", "always_visible": True},
                                        updatemode='drag',
                                    ),
                                ], className="slider-wrapper"),    
                            ], className="slider-pannel"),
                            
                        ], className="tab-wrapper"),
                    ]),
                ], id="tabs"),
            ], id="content", className="pannel"),            
        ], id="content-wrapper")
    ])
    return layout

app.layout = serve_layout

@app.callback(
    Output("elastic-plot", "figure"),
    Input('e1-input', 'value'),
    Input('e2-input', 'value'),
    Input('g-input', 'value'),
    Input('mu-input', 'value'),
    Input('theta-elastic', 'value'),
)
def update_elastic(e1, e2, shear_modulus, poisson_ratio, theta):
    elastic_fig = modulus_wrapper(e1, e2, poisson_ratio, shear_modulus)
    modulus = get_modulus(e1, e2, poisson_ratio, shear_modulus, theta)
    elastic_fig.add_vline(x=theta, line_width=1, line_color="#002833",
                          annotation_text="E<sub>x</sub>= {:.1f} GPa".format(modulus), 
                          annotation_position="top")
    return elastic_fig

@app.callback(
    Output("failure-plot", "figure"),
    Input('s1-input', 'value'),
    Input('s2-input', 'value'),
    Input('tau-input', 'value'),
    Input('theta-failure', 'value'),
)
def update_failure(s1, s2, t12, theta):
    failure_fig = failure_wrapper(s1, s2, t12)
    max_stress = get_max_stress(s1, s2, t12, theta)
    failure_mode = get_failure_mode(s1, s2, t12, theta)
    failure_fig.add_vline(x=theta, line_width=1, line_color="#002833",
                          annotation_text= (
                              "Tsai-Hill: {:.1f} MPa".format(max_stress) 
                              + f"<br>Failure mode: {failure_mode}"
                              ), 
                          annotation_position="top")
    return failure_fig

if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_hot_reload=False)
