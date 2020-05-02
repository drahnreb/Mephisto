from pathlib import Path
import cufflinks as cf
cf.go_offline()
import pandas as pd

import dash_html_components as html

DATA = Path(__file__).resolve().parent.joinpath("data")

def queryData(t, col):
    if t:
        p = DATA.joinpath("p1.parquet")
    else:
        p = DATA.joinpath("p2.parquet")
        
    df = pd.read_parquet(p)
    
    if not col:
        arr = df.index
    else:
        arr = df.loc[:, col]
    
    return arr
    
def fa(className):
    """A convenience component for adding Font Awesome icons"""
    return html.I(className=className)

def createFig(t=1, col="aaTorque_X2"):
    #"aaCurr_X2"
    if t:
        p = DATA.joinpath("p1.parquet")
    else:
        p = DATA.joinpath("p2.parquet")
        
    df = pd.read_parquet(p)
    feat = df.loc[:, col]
    fig = feat.iplot(kind='scatter', mode='markers+lines', size=3, asFigure=True)
    
    return fig


def fetch_data(data, dim="2D"):
    if dim == "2D":
        return [
            {
                'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                'y': [4, 1, 3, 5, 4, 8, 1, 0, 1, 14],
                'text': ['a', 'b', 'c', 'd'],
                'customdata': ['c.a', 'c.b', 'c.c', 'c.d'],
                'name': '01.01.2000 14:35:23.100',
                'mode': 'markers+lines',
                'marker': {'size': 3}
            }
        ]
    elif dim == "3D":
        return [
            {
                'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                'y': [4, 1, 3, 5, 4, 8, 1, 0, 1, 14],
                'text': ['a', 'b', 'c', 'd'],
                'customdata': ['c.a', 'c.b', 'c.c', 'c.d'],
                'name': '01.01.2000 14:35:23.100',
                'mode': 'markers+lines',
                'marker': {'size': 3}
            }
        ]


def create_layout2D():
    return {
        'clickmode': 'event+select',
        'modebar': dict(activecolor='#0296f3'),
        'autosize': True,
        'showlegend': True,
        'margin': dict(l=0, r=0, t=0, b=0),
        'yaxis': dict(automargin=True),
        'xaxis': dict(automargin=True),
    }

