from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd

#http://titi.etsii.urjc.es/splendid/samples/2024_04_02__18_11_26.json
app = Dash()

app.layout = [

    html.H1(children='Splendid validation', style={'textAlign':'center'}),
    html.Button('Submit', id='button', n_clicks=0),
    html.Div(id='unDiv')
]
@callback(
    Output('unDiv', 'children'),
    Input("button", "n_clicks")
)
def buttonClik(value):
    print("update!")
    return html.Div("click")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
