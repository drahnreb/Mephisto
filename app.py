
from pathlib import Path
import sys
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, BASE_DIR)

import dash_uploader as du
import dash
import dash_bootstrap_components as dbc
from flask_caching import Cache
from layout import serve_layout
from callbacks import register_callbacks
from os import environ as env
from utils import UPLOADPATH

DEBUG = False

if DEBUG:
    import shutil
    try:
        shutil.rmtree(str(UPLOADPATH))
    except FileNotFoundError:
        pass
UPLOADPATH.mkdir(parents=False, exist_ok=True)

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True, # disable callback vaidations to enable dynamic modification
    external_stylesheets=[dbc.themes.BOOTSTRAP])

# configure the upload folder
du.configure_upload(app, UPLOADPATH)
CACHE_CONFIG = {
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory',

    # should be equal to maximum number of users on the app at a single time
    # higher numbers will store more data in the filesystem / redis cache
    'CACHE_THRESHOLD': 10
}
# cache = Cache()
# cache.init_app(app.server, config=CACHE_CONFIG)
# cache.clear()

env['UPLOADPATH'] = str(UPLOADPATH)
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
    app.run_server(debug=DEBUG)
