import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# see https://community.plot.ly/t/nolayoutexception-on-deployment-of-multi-page-dash-app-example-code/12463/2?u=dcomfort
from app import server
from app import app
from layouts import layout_birst_category, layout_ga_category, layout_paid_search, noPage, layout_display, layout_publishing, layout_metasearch
import callbacks

# Update page
# # # # # # # # #
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == 'player':
        return layout_player
    else:
        return layout_admin

if __name__ == '__main__':
    app.run_server(debug=True)
