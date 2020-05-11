from pathlib import Path
import cufflinks as cf
cf.go_offline()
import pandas as pd

import dash_html_components as html

DATA = Path(__file__).resolve().parent.joinpath("data")


PLACEHOLDER_EFFECT_CATEGORIES = [
    {"label": "normal", "value": "normal"},
    {"label": "tool wear", "value": "tool_wear"},
    {"label": "tool failure", "value": "tool_failure"}]
PLACEHOLDER_EFFECT_SUB = [
    {"label": "tool wear solidified", "value": "tool_wear_solidified"},
    {"label": "tool wear through cooling", "value": "tool_wear_cooling"}]
PLACEHOLDER_CAUSE_CATEGORIES = [
    {"label": "axial speed", "value": "speed"},
    {"label": "cooling below 23°", "value": "cooling"}]
PLACEHOLDER_CAUSE_SUB = [
    {"label": "speed > 8000rpm", "value": "8000"},
    {"label": "speed > 5500rpm", "value": "5500"}]


def queryData(t, col):
    # TODO: db query
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


def querySimilarSamples(annotatedClass, n=3):
    """
        annotatedClass is index of a class
    """
    # sample nsize=3
    data = []

    #TODO: query: where annotatedClass
    values = [[0,13,46,342,543],[1.23,345.5,45.43,124.4,342.4]]
    for _ in range(n):
        data.append({'eq': '', 't0': 1588636800021, 'TID': None, 'values': values})

    store = {'class': annotatedClass, 'data': data}

    return store


def queryAnnotationClasses(atype='ecat'):
    # TODO: db query
    options = []
    if 'ecat' in atype:
        options = PLACEHOLDER_EFFECT_CATEGORIES
    elif 'esub' in atype:
        options = PLACEHOLDER_EFFECT_SUB
    elif 'ccat' in atype:
        options = PLACEHOLDER_CAUSE_CATEGORIES
    elif 'csub' in atype:
        options = PLACEHOLDER_CAUSE_SUB

    return options
                        

def storeAnnotationClasses(strInput, atype='ecat'):
    saved = queryAnnotationClasses(atype)
    idx = len(saved) + 1
    new = {"label": strInput, "value": idx}
    # TODO: add entry to db
    dictOptions = saved + new
    if 'ecat' in atype:
        PLACEHOLDER_EFFECT_CATEGORIES = dictOptions
    elif 'esub' in atype:
        PLACEHOLDER_EFFECT_SUB = dictOptions
    elif 'ccat' in atype:
        PLACEHOLDER_CAUSE_CATEGORIES = dictOptions
    elif 'csub' in atype:
        PLACEHOLDER_CAUSE_SUB = dictOptions

    return dictOptions

    
def fa(className):
    """A convenience component for adding Font Awesome icons"""
    return html.I(className=className)

def updateFig(data, col="aaTorque_X2"):
    # layout = dict()
    if t:
        p = DATA.joinpath("p1.parquet")
    else:
        p = DATA.joinpath("p2.parquet")
        
    df = pd.read_parquet(p)
    feat = df.loc[:, col]

    feat.iplot(
            kind='scatter',
            mode='markers+lines',
            size=5,
            #layout=layout,
            asFigure=True)

    return fig


def createFigTemplate(kind):
    if kind == 'scatter3d':
        dictHideOptions = dict(visible=False, showgrid=False, zeroline=False, showline=False, autorange=True, showticklabels=False)
        placeholder = pd.DataFrame([{'x':1, 'y':1, 'z':1, 'text': "Select sample(s) of two features"}])
        fig = placeholder.iplot(
                kind='scatter3d',
                mode='markers+lines'+'+text',
                size=1,
                x='x',
                y='y',
                z='z',
                text='text',
                textposition="bottom center",
                asFigure=True)
        fig.layout.scene = {
            'xaxis': dictHideOptions,
            'yaxis': dictHideOptions,
            'zaxis': dictHideOptions
        }
    else:
        dictHideOptions = dict(showgrid=False, zeroline=False, showline=False, autorange=True, showticklabels=False)
        
        placeholder = pd.DataFrame([1])
        fig = placeholder.iplot(
                kind='scatter',
                mode='markers+lines'+'+text',
                size=1,
                text=["Select sample(s) of a feature"],
                textposition="bottom center",
                asFigure=True)
        fig.layout.xaxis = dictHideOptions
        fig.layout.yaxis = dictHideOptions

    # do some polishing
    fig.data[0].update(
        textfont=dict(size=30)
    )
    fig.layout.update(hovermode=False)
    
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

