import dash
import dash_bootstrap_components as dbc
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, BASE_DIR)

from layout import serve_layout
from callbacks import register_callbacks

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True, # disable callback vaidations to enable dynamic modification
    external_stylesheets=[dbc.themes.BOOTSTRAP])
    
app.layout = serve_layout()
register_callbacks(app)

"""
# Mephisto - Data Annotation for Tensor data e.g. Time Series or general multidimensional Arrays

Non-intuitive human intelligence task for physical highly complex data produced in dynamic production systems.
Data Labeling Tool for physical mechanisms in subsystems of a cyber-physical production system.\n
Collaborative Human Intelligence Tasks (Process/Mechanical Engineers meet Data Engineers++)\n
[Project: GuineaPig]
"""

if __name__ == '__main__':
    app.run_server(debug=True)

