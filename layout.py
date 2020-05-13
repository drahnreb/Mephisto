import dash_uploader as du
from datetime import datetime as dt
from datetime import timedelta
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, State, Output
from utils import fa, queryAnnotationClasses, createFigTemplate, createFigConfig, TENSOR_EXTENSIONS, PICTURE_EXTENSIONS
import uuid
import plotly.express as px
import re

from dash.exceptions import PreventUpdate

__version__ = "1.0"
PROJ_URL = "https://drahnreb.github.io/Mephisto"
PROJ_ISSUE_URL = "https://github.com/drahnreb/Mephisto/issues/"
PERSISTENCE = "local" # session memory local

def initHead():
    """ 
        head with Logo/Description/Link to further resources
    """
    return dbc.Row(
        id="div-head-desc",
        children=[
            dbc.Col(
                html.H1([fa("fab fa-freebsd"), "  Mephisto  "], id="icon-about-mephisto"),
                width=2
            ),
            dbc.Col([
                html.H6(["v. ", __version__], id="version-check"),
            ],
                align="end"
            ),
            dbc.Col([
                dbc.Row(html.A(html.H6([fa("fas fa-external-link-alt"), " Visit Website", "  "]),
                               href=PROJ_URL, target="_blank")),
                dbc.Row(html.A(html.H6([fa("fab fa-github"), " Report issues!"]),
                               href=PROJ_ISSUE_URL, target="_blank"))
            ],
                width=2,
                align="end"
            ),
            html.Hr()
        ],
        className="sticky-top",
        style={"background": "white", "zIndex": 999}
    )


def initSelectData():
    """ select/import/upload data head """
    
    def _createCollapsableTabs():
        """ create more viewable space.
            collapse button and encapsulation
        """
            
        def _createLoadDataTab():
            """ load data tab """
            return dbc.Tab(
                label="Load Data",
                id='tab-load-data',
                children=dbc.Row(
                    [spawnConnectorDialogs(ctype) for ctype \
                        in ['upload-connector','local-db-connector',
                            'cloud-blob-connector','cloud-stream-connector']] + [
                        # upload local data
                        dbc.Col([
                            dbc.Row(dbc.Col(dbc.Label('Upload local data:', style={"fontWeight": "bold"}))),
                            dbc.Row(dbc.Col(dbc.Button(
                                "Upload File(s) (Textual, Picture...)",
                                color="primary",
                                n_clicks=0,
                                n_clicks_timestamp=0,
                                id={
                                    "type": "btn-upload-connector",
                                },
                                disabled=False)), align="center", justify="center")
                            ], width=3
                        ),
                        # connect to local database
                        dbc.Col([
                            dbc.Row(dbc.Col(dbc.Label('Connect to local database:', style={"fontWeight": "bold"}))),
                            dbc.Row(dbc.Col(dbc.Button(
                                "Local Database (SciDB/PostgreSQL)",
                                color="primary",
                                n_clicks=0,
                                n_clicks_timestamp=0,
                                id={
                                    "type": "btn-local-db-connector",
                                },
                                disabled=False)), align="center", justify="center")
                            ], width=3
                            # style={"border-right": "1px grey dash"},
                        ),
                        # setup new cloud connections
                        dbc.Col([
                            dbc.Row(dbc.Col(dbc.Label('Connect to cloud data:', style={"fontWeight": "bold"}))),
                            dbc.Row(dbc.Col(dbc.Button(
                                "DataLake or BlobStorage",
                                color="light",
                                n_clicks=0,
                                n_clicks_timestamp=0,
                                id={
                                    "type": "btn-cloud-blob-connector",
                                },
                                disabled=True)), align="center", justify="center")
                            ], width=3
                            # style={"border-right": "1px grey dash"},
                        ),
                        # setup stream real-time connection
                        dbc.Col([
                            dbc.Row(dbc.Col(
                                dbc.Label('Connect to near-real-time data stream:', style={"fontWeight": "bold"}))),
                            dbc.Row(dbc.Col(dbc.Button(
                                "Connect Stream",
                                color="light",
                                n_clicks=0,
                                n_clicks_timestamp=0,
                                id={
                                    "type": "btn-cloud-stream-connector",
                                },
                                disabled=True)#,width=3
                                ), align="center", justify="center")
                            ], width=3
                        )
                    ], style={'margin-bottom': '8px'}
                )
            )
        
        def _createConnectorTab():
            """ data connector status """
            return dbc.Tab(
                label="Data Connectors: 0",
                disabled=True,
                children=[
                    dbc.Row(
                        children=[],
                        id="div-data-connectors",
                    )
                ],
                id='tab-data-connectors'
            )

        def _createReportTab():
            """ export data tab """
            return dbc.Tab(
                label="Reporting Dashboard",
                disabled=True,
                children=[
                    dbc.Row(dbc.Col(
                        dbc.Button("Reporting", outline=True, color="success", id="btn-selectData-report"), width=2),
                            justify="center", align="center")
                ],
                id='tab-report-data'
            )

        return dbc.Col([
            dbc.Collapse(
                [
                    dbc.Tabs([_createLoadDataTab()] + [_createConnectorTab()] + [_createReportTab()])
                ],
                id="collapse-data-connection",
                is_open=True
            ),
            dbc.Button(
                fa("fas fa-chevron-up"),  # hidden==fas fa-chevron-down
                color="light",
                id="btn-select-data_collapse",
                n_clicks=0,
                style={"visibility": "visible"},  # hidden
                block=True
            )
        ])
        
    return dbc.Row(
        _createCollapsableTabs(),
        id="div-select-data"
    )


def initWorkspace():
    """ main annotation window """
    
    def _createGraphSpace():
        """ graph space holds all spawned plots
            and a button to add plots
        """
        # graphPlaceholder = dbc.Container(
        #     children=[],
        #     fluid=True,
        #     className="pt-2",
        #     id="div-graphSpace"
        # )
        
        # add graph button row
        return dbc.Row(dbc.Col([
            dbc.Modal(
                [
                    dbc.ModalHeader("Bind Graph to a Data Connector"),
                    dbc.ModalBody(
                        [   
                            html.Div(id="div-newGraph-coupling-gtype", style={'display': 'none'}),
                            dcc.Dropdown(
                                id='dropdown-newGraph-coupling-idx',
                                placeholder='Choose Data Connector',
                                searchable=True,
                                clearable=True
                            )
                        ]
                    ),
                    dbc.ModalFooter([
                        dbc.Button("Cancel", id="btn-dimsiss-dialog-newGraph-coupling", n_clicks=0, className="ml-auto"),
                        dbc.Button("Create Graph", id="btn-create-graph", disabled=True, n_clicks=0, className="ml-auto")
                    ]),
                ],
                id="dialog-newGraph-coupling",
                size="md",
                centered=True,
            ),
            dbc.ButtonGroup([
                dbc.Button(
                    [fa("fas fa-plus"), " 2D"],
                    n_clicks_timestamp=0,
                    n_clicks=0,
                    id="btn-add-graph-2D"
                ),
                dbc.Button(
                    [fa("fas fa-plus"), " 3D"],
                    n_clicks_timestamp=0,
                    n_clicks=0,
                    id="btn-add-graph-3D"
                ),
                dbc.Button(
                    [fa("fas fa-plus"), " Picture"],
                    n_clicks_timestamp=0,
                    n_clicks=0,
                    id="btn-add-graph-pic"
                )
            ],
            size="md",
            className="mr-1",
            )
        ], width=3, className="p-2"), justify="end", align="stretch")
            # dbc.Row(dbc.Col([dbc.Button(fa("fas fa-plus"), color="dark", id="btn-create-graph")], width=1, className="p-2"), justify="end")
        
    def _createAnnotationSpace():
        """ annotation class space """

        def _createToolbar():
            """ annotation toolset """
            return dbc.Container([
                # dbc.Row([
                #     dbc.Col(dbc.Button(children=[fa("far fa-square"), " Lasso"], outline=True, block=True, color="secondary", id="btn-tools-lasso", className="p-1"), xl=4, className="p-1"),
                #     dbc.Col(dbc.Button(children=[fa("fas fa-mouse-pointer"), " Point"], outline=True, block=True, color="secondary", id="btn-tools-point", className="p-1"), xl=4, className="p-1"),
                #     dbc.Col(dbc.Button(children=[fa("fas fa-grip-lines-vertical"), " Range"], outline=True, block=True, color="secondary", id="btn-tools-range", className="p-1"), xl=4, className="p-1")
                # ], className="m-1", justify="between"),
                # html.Div(className="clearfix visible-xs-block"),
                dbc.Row([
                    # dbc.Col(dbc.Button(children=[fa("fas fa-chart-line"), "  Trend-Line"], outline=True, block=True, color="secondary", id="btn-tools-line", className="p-1"), xl=6, className="p-1"),
                    dbc.Col(dbc.Button(children=[fa("fas fa-link"), "  Multivariate Linking"], outline=True, block=True,
                                       color="secondary", n_clicks_timestamp=0, n_clicks=0, id="btn-tools-linker", active=False, className="p-1"), className="p-1")
                    # ,xl=6
                ], className="m-1", justify="between"),
            ], fluid=True, id="div-toolbar", style={'position': 'sticky', 'bottom': 0, "zIndex": 5})

        def _createEffectView():
            return [
                dbc.Col(
                    [
                        # selection from existing classes
                        dbc.Row(dbc.Col([
                            dbc.Label("Select from existing effects", style={"fontWeight": "bold"}),
                            dcc.Dropdown(
                                id="dropdown-effect-category-selector",
                                options=queryAnnotationClasses(atype='ecat'), # Spawned list of dict options {'label': 'l1', 'value': 'v1'} during session
                                value=None,
                                placeholder="Type to search...",
                                searchable=True,
                                clearable=True,
                                multi=False,
                                persistence=True,
                                persistence_type=PERSISTENCE
                            )
                        ])),
                        # definition of new effect
                        dbc.Row(dbc.Col([
                            dbc.FormGroup(
                                [
                                    dbc.Label("No effect suitable?"),
                                    dbc.Input(placeholder="define new effect category...",
                                        valid=False,
                                        invalid=False,
                                        persistence=True,
                                        persistence_type=PERSISTENCE,
                                        id="input-new-effect-category"
                                    ),
                                    dbc.FormText("Try to select from available effects. Care about naming conventions!"),
                                    dbc.Button("Save in database",
                                        color="info",
                                        outline=True,
                                        block=True,
                                        n_clicks_timestamp=0,
                                        id="btn-add-effect-category")
                                ]
                            )
                        ])),
                        html.Hr(),
                        # specific effect subcategory
                        dbc.Row(dbc.Col([
                                dbc.Label("Specific effect subcategory", style={"fontWeight": "bold"}, id='label-effect-subcategory'),
                                dcc.Dropdown(
                                    id="dropdown-effect-subcategory-selector",
                                    options=[], # Spawned list of dict options {'label': 'l1', 'value': 'v1'} during session
                                    placeholder="Type to search...",
                                    searchable=True,
                                    clearable=True,
                                    multi=True,
                                    persistence=True,
                                    persistence_type=PERSISTENCE)
                            ]
                        ), id="div-effect-subcategory", style={"visibility": "hidden"}),
                        # definition of new effect types
                        dbc.Row(dbc.Col([
                            dbc.FormGroup(
                                [
                                    dbc.Label("No effect subcategory suitable?"),
                                    dbc.Input(placeholder="define new effect subcategory...",
                                        valid=False,
                                        invalid=False,
                                        persistence=True,
                                        persistence_type=PERSISTENCE,
                                        id="input-new-effect-subcategory"
                                    ),
                                    dbc.FormText("Try to select from available sub-effects. Care about naming conventions!"),
                                    dbc.Button("Save in database",
                                        color="info",
                                        outline=True,
                                        block=True,
                                        n_clicks_timestamp=0,
                                        id="btn-add-effect-subcategory")
                                ]
                            )
                        ]), id="div-add-effect-subcategory", style={"visibility": "hidden"}),
                        # samples with same class assignment
                        dbc.Row([
                            dbc.Col([
                                html.Hr(),
                                dbc.Label("Other samples with same effect", style={"fontWeight": "bold"}),
                                dbc.ListGroup(
                                    children=[],
                                    id="listgroup-similar-effect-samples"
                                )
                            ], id="div-samples-effect", style={"visibility": "hidden"})
                        ])
                    ]
                )
            ]

        def _createCauseView():
            return [
                dbc.Col([
                    # selection from existing classes
                    dbc.Row(dbc.Col([
                        dbc.Label("Select from existing causes", style={"fontWeight": "bold"}),
                        dcc.Dropdown(
                            id="dropdown-cause-category-selector",
                            options=queryAnnotationClasses(atype='ccat'), # Spawned list of dict options {'label': 'l1', 'value': 'v1'} during session
                            value=None,
                            placeholder="Type to search...",
                            searchable=True,
                            clearable=True,
                            multi=False,
                            persistence=True,
                            persistence_type=PERSISTENCE
                        )
                    ])),
                    # definition of new effect
                    dbc.Row(dbc.Col([
                        dbc.FormGroup(
                            [
                                dbc.Label("No cause suitable?"),
                                dbc.Input(placeholder="define new cause category...",
                                    valid=False,
                                    invalid=False,
                                    persistence=True,
                                    persistence_type=PERSISTENCE,
                                    id="input-new-cause-category"
                                ),
                                dbc.FormText("Try to select from available cause. Care about naming conventions!"),
                                dbc.Button("Save in database",
                                    color="info",
                                    outline=True,
                                    block=True,
                                    n_clicks_timestamp=0,
                                    id="btn-add-cause-category")
                            ]
                        )
                    ])),
                    html.Hr(),
                    # specific effect subcategory
                    dbc.Row(dbc.Col([
                            dbc.Label("Specific cause subcategory", style={"fontWeight": "bold"}, id='label-cause-subcategory'),
                            dcc.Dropdown(
                                id="dropdown-cause-subcategory-selector",
                                options=[], # Spawned list of dict options {'label': 'l1', 'value': 'v1'} during session
                                placeholder="Type to search...",
                                searchable=True,
                                clearable=True,
                                multi=True,
                                persistence=True,
                                persistence_type=PERSISTENCE)
                        ]
                    ), id="div-cause-subcategory", style={"visibility": "hidden"}),
                    # definition of new effect types
                    dbc.Row(dbc.Col([
                        dbc.FormGroup(
                            [
                                dbc.Label("No cause subcategory suitable?"),
                                dbc.Input(placeholder="define new cause subcategory...",
                                    valid=False,
                                    invalid=False,
                                    persistence=True,
                                    persistence_type=PERSISTENCE,
                                    id="input-new-cause-subcategory"
                                ),
                                dbc.FormText("Try to select from available sub-causes. Care about naming conventions!"),
                                dbc.Button("Save in database",
                                    color="info",
                                    outline=True,
                                    block=True,
                                    n_clicks_timestamp=0,
                                    id="btn-add-cause-subcategory")
                            ]
                        )
                    ]), id="div-add-cause-subcategory", style={"visibility": "hidden"}),
                    # samples with same class assignment
                    dbc.Row([
                        dbc.Col([
                            html.Hr(),
                            dbc.Label(f"Other samples with same cause", style={"fontWeight": "bold"}),
                            dbc.ListGroup(
                                children=[],
                                id="listgroup-similar-cause-samples"
                            )
                        ], id="div-samples-cause")
                    ])
                ])
            ]
        
        return [
            dbc.Row(_createToolbar()),
            html.Hr(),
            dbc.Row(_createEffectView()),
            html.Hr(),
            dbc.Row(_createCauseView()),
            dbc.Row(dbc.Col(
                dbc.Button([
                        "Save phenomenon",
                        dcc.Loading(
                            id="loading-workspace-save",
                            children=[],#html.Div(id="loading-workspace-save"),
                            type="circle",
                        )],
                    disabled=True,
                    outline=False,
                    block=True,
                    color="success",
                    n_clicks_timestamp=0,
                    n_clicks=0,
                    id="btn-workspace-save")),
                className="my-4"),
            dbc.Row(dbc.Col(
                dbc.Alert(
                    "Successfully saved phenomenon",
                    id="alert-saved",
                    is_open=False,
                    duration=2000,
                    )
                ),
                className="my-4"),
            dbc.Row(dbc.Col(
                dcc.ConfirmDialogProvider(
                    dbc.Button("Reset",
                        outline=True,
                        block=True,
                        color="danger",
                        n_clicks_timestamp=0,
                        n_clicks=0,
                        disabled=True,
                        id="btn-workspace-reset"),
                    id='confirm-dialog-reset',
                    submit_n_clicks_timestamp=0,
                    message='All annotions since last save will be deleted! Are you sure you want to continue?'
                    )
                ),
                className="my-4"),
        ]
        
    return dbc.Row(
        [
            dbc.Col(
                children=_createAnnotationSpace(),
                style={"borderRight": "1px grey solid"},  # 'position':'sticky', 'top':0},
                # className="sticky-top",
                width=2,
                id="div-annotationSpace"
            ),
            dbc.Col(
                children=[_createGraphSpace()],
                width=10,
                id="div-graphSpace"
            )
        ],
        id="div-workspace",
        style={"zIndex": 5}
    )


##########
# LAYOUT
##########
def serve_layout():
    session_id = str(uuid.uuid4())
    return dbc.Container([
        ## div-head-desc
        initHead(),
        ## div-select-data
        initSelectData(),
        ## div-workspace
        # style={"height": "calc(100vh)"}, # stretch row over entire screen #-200px
        initWorkspace(),
        html.Div(session_id, id='session-id', style={'display': 'none'}),
        dcc.Store(
            data={},
            id="store-data-connectors",
            storage_type=PERSISTENCE,
            modified_timestamp=0
        ),
        dcc.Store(
            data={'class': '', 'data': []},
            id="store-similar-effect-samples",
            modified_timestamp=0,
            storage_type=PERSISTENCE
        ),
        dcc.Store(
            data={'class': '', 'data': []},
            id="store-similar-cause-samples",
            modified_timestamp=0,
            storage_type=PERSISTENCE
        ),
    ],
        fluid=True
        # style={"height": "100vh"}
    )


##########
# Templates for
# "spawnable" elements
##########

def spawnSimilarSamples(atypeSamplesStore: dict, atype: str = 'effect'):

    samples = []
    annotatedClass = atypeSamplesStore.get('class')
    listData = atypeSamplesStore.get('data')

    if len(listData):
        for data in listData:
            eq = data.get('eq')
            TID = data.get('TID')
            epochtime = data.get('t0')
            if epochtime:
                epochtime = epochtime/1000
                strDatetime =  dt.fromtimestamp(epochtime).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            else:
                strDatetime = ''

            if 'cause' in atype:
                atype = 'cause'
                color = 'primary'
            else:
                atype = 'effect'
                color = 'light'

            item = dbc.ListGroupItem(
                [
                    dbc.Row([
                        dbc.Col([
                            dbc.Row([
                                dbc.Col(strDatetime),
                                dbc.Col(dbc.Badge(
                                    "",  # plot number
                                    color="info",
                                    style={"visibility": "visible"},
                                    id={
                                        "type": f"badge-similar-{atype}-sample",
                                        "eq": eq,
                                        "index": epochtime
                                    },
                                ))
                            ]),
                            dbc.Row(
                                dbc.Col(annotatedClass)
                            )
                        ])
                    ],justify="between")
                ],
                id={
                    "type": f"list-similar-{atype}-sample",
                    "eq": eq,
                    "index": epochtime
                },
                n_clicks=0,
                action=True,
                color=color
            )
            samples.append(item)
            
    return samples


def spawnDataConnector(strConnectorDesc, idx):
    return dbc.Button(
        [
            str(strConnectorDesc),
            # dbc.Progress(
            #     value=0,
            #     style={"height": "1px"},
            #     id={
            #         "type": "prg-data-connector",
            #         "index": idx
            #     },
            # )
        ],
        id={
            "type": "btn-data-connector",
            "index": idx
        },
        color="secondary",
        className="mr-1"
    )


def spawnGraph(idx, kind, listDictAllFeatures, strEQ, strType, intTotSamples, dtMinDate, dtMaxDate):
    """ 
        fig: json with link to aggregate or pre-cached dataframe to load into plotly graph
        meta: schema with suplimental information
    """
    # calculate end date for datetimerange
    strMaxDate = str(dtMaxDate)
    diff = dtMaxDate - dtMinDate
    if not diff.days:
        strMaxDate = str(dtMaxDate + timedelta(days=1))
    strMinDate = str(dtMinDate)

    if kind == 'scatter3d' and len(listDictAllFeatures) >= 2:
        intHalfOfFeatures = len(listDictAllFeatures) // 2

        listComponentSelectFeature = [
            dbc.Col(
                width=7,
                style={"padding-left": "0px"},
                children=[
                    dbc.Row(dbc.Col(
                        dcc.Dropdown(
                            options=listDictAllFeatures[:intHalfOfFeatures],
                            value=[],
                            multi=True,
                            persistence_type=PERSISTENCE,
                            placeholder='Select feature(s) on y-Axis',
                            id={
                                "type": "dropdown-select-feature-Y",
                                "index": idx
                            },
                        )
                    )),
                    dbc.Row(dbc.Col(
                        dcc.Dropdown(
                            options=listDictAllFeatures[intHalfOfFeatures:],
                            value=[],
                            multi=True,
                            persistence_type=PERSISTENCE,
                            placeholder='Select feature(s) on z-Axis',
                            id={
                                "type": "dropdown-select-feature-Z",
                                "index": idx
                            },
                        )
                    ), style={"margin-top": "5px"}),
                    html.Div(dcc.Dropdown(
                                options=[],
                                value=[],
                                multi=True,
                                persistence_type=PERSISTENCE,
                                placeholder='Shadowing',
                                id={
                                    "type": "dropdown-select-picture",
                                    "index": idx
                                },
                    ), style={'display': 'none'})
                ]
            )
        ]

    elif kind == 'picture':
        pH = 'picture'
        dT = 'picture'

        intTotSamples = 1
        listComponentSelectFeature = [
            dbc.Col(
                width=7,
                style={"padding-left": "0px"},
                children=[
                    dcc.Dropdown(
                        options=listDictAllFeatures,
                        value=[],
                        multi=True,
                        persistence_type=PERSISTENCE,
                        placeholder=f'Select {pH}',
                        id={
                            "type": "dropdown-select-picture",
                            "index": idx
                        },
                    )
                ]
            ),
            html.Div(dcc.Dropdown(
                        options=[],
                        value=[],
                        multi=True,
                        persistence_type=PERSISTENCE,
                        placeholder='Shadowing',
                        id={
                            "type": "dropdown-select-feature-Y",
                            "index": idx
                        },
            ), style={'display': 'none'}),
            html.Div(dcc.Dropdown(
                options=[],
                value=[],
                multi=True,
                persistence_type=PERSISTENCE,
                placeholder='Shadowing',
                id={
                    "type": "dropdown-select-feature-Z",
                    "index": idx
                },
            ), style={'display': 'none'})
    ]

    else:
        pH = 'feature(s) on y-Axis'

        intTotSamples = 1
        listComponentSelectFeature = [
            dbc.Col(
                width=7,
                style={"padding-left": "0px"},
                children=[
                    dcc.Dropdown(
                        options=listDictAllFeatures,
                        value=[],
                        multi=True,
                        persistence_type=PERSISTENCE,
                        placeholder=f'Select {pH}',
                        id={
                            "type": "dropdown-select-feature-Y",
                            "index": idx
                        },
                    )
                ]
            ),
            html.Div(dcc.Dropdown(
                options=[],
                value=[],
                multi=True,
                persistence_type=PERSISTENCE,
                placeholder='Shadowing',
                id={
                    "type": "dropdown-select-feature-Z",
                    "index": idx
                },
            ), style={'display': 'none'}),
            html.Div(dcc.Dropdown(
                        options=[],
                        value=[],
                        multi=True,
                        persistence_type=PERSISTENCE,
                        placeholder='Shadowing',
                        id={
                            "type": "dropdown-select-picture",
                            "index": idx
                        },
            ), style={'display': 'none'})
        ]

    return dbc.Container([
            dbc.Row(
                [
                    dbc.Col([
                        dbc.Row(
                            dbc.FormText(
                                f"Machine EQ: {strEQ}.\t Date Range: {dtMinDate} - {dtMaxDate}.\t Data Source: {strType}.\t Total samples: {intTotSamples}",
                                id={
                                    "type": "formtext-data",
                                    "index": idx,
                                    # "eq": strEQ,
                                    # "type": strType
                                }
                            ),
                            align="stretch",
                            no_gutters=True,
                        ),
                        dbc.Row(
                            listComponentSelectFeature + [
                            dbc.Col(
                                width=5,
                                style={"padding-right": "0px"},
                                id="div-choose-samples",
                                children=[
                                    dbc.Row([
                                        dbc.Col(
                                            width=3,
                                            children=[
                                                dbc.FormGroup([
                                                    dbc.Input(
                                                        placeholder="no. of sample(s)",
                                                        type='number',
                                                        id={
                                                            "type": "input-select-sample-n",
                                                            "index": idx,
                                                            # "eq": strEQ,
                                                            # "type": strType
                                                        },
                                                        max=intTotSamples,
                                                        min=1,
                                                        step=1
                                                    )
                                                ])
                                            ],
                                            style={"padding": "0px"},
                                        ),
                                        dbc.Col(
                                            width=6,
                                            style={"visibility": "visible"},
                                            className="dash-bootstrap",
                                            children=[
                                                dcc.DatePickerRange(
                                                    id={
                                                        "type": "datepicker-select-sample-range",
                                                        "index": idx,
                                                        # "eq": strEQ,
                                                        # "type": strType
                                                    },
                                                    min_date_allowed=strMinDate,
                                                    max_date_allowed=strMaxDate,
                                                    display_format="DD.MM.YYYY",
                                                    start_date=strMinDate,
                                                    clearable=True,
                                                    with_portal=False,
                                                    first_day_of_week=1,
                                                    start_date_placeholder_text="Start Date",
                                                    end_date_placeholder_text="End Date",
                                                    persistence_type=PERSISTENCE,
                                                    updatemode='singledate'
                                                )
                                            ]
                                        ),
                                        dbc.Col(
                                            width=2,
                                            children=dbc.Input(
                                                id={
                                                    "type": "input-select-sample-time",
                                                    "index": idx,
                                                    # "eq": strEQ,
                                                    # "type": strType
                                                },
                                                placeholder="hh:mm",
                                                value='00:00',
                                                type="text",
                                                max=23,
                                                min=0,
                                                maxLength=5,
                                                pattern="^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$",
                                                persistence_type=PERSISTENCE
                                            ),
                                            style={"padding-left": "0px"},
                                        ),
                                        dbc.Col(
                                            width=1,
                                            children=[
                                                dbc.Button(fa("far fa-trash-alt"),
                                                    outline=True,
                                                    color="danger",
                                                    className="mr-1",
                                                    size="sm",
                                                    n_clicks_timestamp=0,
                                                    n_clicks=0,
                                                    id={
                                                        "type": "btn-remove-graph",
                                                        "index": idx,
                                                        # "eq": strEQ,
                                                        # "type": strType
                                                    },
                                                ),
                                            ], 
                                            style={"padding": "0px"},
                                        )
                                    ]
                                ),
                                dbc.Row([
                                    dbc.Col(
                                        dbc.FormGroup(
                                            [
                                                dbc.Label(
                                                    "Choose: ",
                                                    html_for="choose-radios-row",
                                                    width=1,
                                                    style={"padding": "0px"}
                                                ),
                                                dbc.Col(
                                                    dbc.RadioItems(
                                                        inline=True,
                                                        id={
                                                            "type": "radio-select-sample-draw",
                                                            "index": idx,
                                                            # "eq": strEQ,
                                                            # "type": strType
                                                        },
                                                        options=[
                                                            # als toolbox {"label": "iid", "value": "iid"},
                                                            {"label": "randomly ~U(0,n)", "value": "random"},  # uniform distribution
                                                            {"label": "by sequence", "value": "sequence"}
                                                        ],
                                                        value='random',
                                                    ),
                                                    width=10,
                                                ),
                                            ],
                                            row=True,
                                            style={"margin": "0px"},

                                        ),
                                        style={"padding": "0px"},
                                    ),
                                    dbc.Col(
                                        width=1,
                                        children=[
                                            dbc.Button(fa("fas fa-redo-alt"),
                                                outline=True,
                                                color="info",
                                                className="mr-1",
                                                size="sm",
                                                n_clicks_timestamp=0,
                                                n_clicks=0,
                                                id={
                                                    "type": "btn-reload-graph",
                                                    "index": idx,
                                                    # "eq": strEQ,
                                                    # "type": strType
                                                },
                                            ),
                                        ], 
                                        style={"padding": "0px", "margin-bottom": "5px"},
                                        align='center',
                                    )
                                ])
                            ])
                        ],
                        align="stretch",
                        style={"margin": "0px"},
                        )
                    ], style={"padding": "0px"})
                ], no_gutters=True
            ),
            dbc.Row([
                dcc.Graph(
                    id={
                        "type": "graph",
                        "index": idx,
                        # "eq": strEQ,
                        # "type": strType
                    },
                    figure=createFigTemplate(kind),
                    config=createFigConfig(kind),
                    style={"width": "100vh"},
                )
            ],
                # style={"width": "100vh"},
                justify="center",
                align="stretch",
                no_gutters=True,
                id={
                    "type": "row-graph",
                    "index": idx,
                    # "eq": strEQ,
                    # "type": strType
                },
            ),
            html.Hr(
                className="m-3",
            )
        ], fluid=True, className="pt-2"
    )


def spawnConnectorDialogs(connectorType):
    metaInfos = [
        dbc.InputGroup(
            [
                dbc.Select(
                    options=[
                        {"label": "Tensor / Time Series / nd-Arrays", "value": 'tensor'},
                        {"label": "Picture (s)", "value": 'picture'},
                    ],
                    id={
                        'type': 'dialog-connector-gtype',
                        'ctype': connectorType
                    }
                ),
                dbc.InputGroupAddon("Visualization Type: ", addon_type="prepend"),
            ]
        ),
        dbc.InputGroup(
            [
                dbc.Textarea(
                    id={
                        'type': 'dialog-connector-schema',
                        'ctype': connectorType
                    }
                ),
                dbc.InputGroupAddon("Schema: ", addon_type="prepend"),
            ]
        ),
        dbc.InputGroup(
            [
                dbc.Input(
                    placeholder="Equipment Number or Data Group Identifier",
                    id={
                        'type': 'dialog-connector-eq',
                        'ctype': connectorType
                    }
                ),
                dbc.InputGroupAddon("EQ: ", addon_type="prepend"),
            ]
        ),
        dbc.InputGroup(
            [
                dbc.Select(
                    options=[
                        {"label": "NC", "value": 'NC'},
                        {"label": "SPS", "value": 'SPS'},
                        {"label": "Bolting", "value": 'Bolting'},
                        {"label": "Xray", "value": 'Xray'}
                    ],
                    id={
                        'type': 'dialog-connector-dataType',
                        'ctype': connectorType
                    }
                ),
                dbc.InputGroupAddon("Data Type: ", addon_type="prepend"),
            ]
        ),
        dbc.InputGroup(
            [
                dbc.Input(
                    placeholder="optional",
                    type="text",
                    id={
                        'type': 'dialog-connector-source',
                        'ctype': connectorType
                    }
                ),
                dbc.InputGroupAddon("Data Source: ", addon_type="prepend"),
            ]
        ),
        # dummies so our wildcard callbacks don't fail
        dbc.Input(id={'type': 'dialog-connector-host','ctype': connectorType}, style={'display': 'none'}),
        dbc.Input(id={'type': 'dialog-connector-port','ctype': connectorType}, style={'display': 'none'}),
        dbc.Input(id={'type': 'dialog-connector-user','ctype': connectorType}, style={'display': 'none'}),
        dbc.Input(id={'type': 'dialog-connector-pw','ctype': connectorType}, style={'display': 'none'}),
    ]

    if connectorType == 'upload-connector':
        header = "Upload (large) file(s)"
        body = metaInfos + [
            f"Supported extensions {[ext.replace('*', '') for ext in ['.'+e for e in TENSOR_EXTENSIONS]+PICTURE_EXTENSIONS]}",
            du.Upload(
                text="Drag and Drop here or click to select files to upload",
                text_completed='Completed: ',
                pause_button=True,
                cancel_button=True,
                max_file_size=1800,  # 1800 Mb
                css_id='upload-data',
                default_style={
                    'width': '100%',
                    'minHeight': '50px',
                    'lineHeight': '50px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '5px'
                },
                filetypes=TENSOR_EXTENSIONS
            )
        ]

    elif connectorType == 'local-db-connector':
        header = "Connect to local DB"
        body = metaInfos[:-4] + [
            f"Supported Databases are PostgreSQL (with TimescaleDB Extension) or SciDB",
        ] + [
            html.Div([
                dbc.InputGroup(
                    [
                        dbc.Input(
                            placeholder="localhost",
                            valid=True,
                            id={
                                'type': 'dialog-connector-host',
                                'ctype': connectorType
                            },
                            pattern=r"^(localhost|(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])))))?$"
                        ),
                        dbc.InputGroupAddon("Server Host: ", addon_type="append"),
                    ],
                    className="mb-9",
                ),
                dbc.InputGroup(
                    [
                        dbc.Input(
                            placeholder="8080",
                            type="number",
                            id={
                                'type': 'dialog-connector-port',
                                'ctype': connectorType
                            }
                        ),
                        dbc.InputGroupAddon("Server Port: ", addon_type="append"),
                    ],
                    className="mb-3",
                ),
                dbc.InputGroup(
                    [
                        dbc.Input(
                            placeholder="user",
                            type="number",
                            id={
                                'type': 'dialog-connector-user',
                                'ctype': connectorType
                            }
                        ),
                        dbc.InputGroupAddon("DB Server User: ", addon_type="append"),
                    ],
                    className="mb-3",
                ),
                dbc.InputGroup(
                    [
                        dbc.Input(
                            placeholder="*****",
                            type="password",
                            id={
                                'type': 'dialog-connector-pw',
                                'ctype': connectorType
                            }
                        ),
                        dbc.InputGroupAddon("DB Server Password: ", addon_type="append"),
                    ],
                    className="mb-3",
                )
            ])
        ]

    elif connectorType == 'cloud-blob-connector':
        header = "Connect to Azure Blob Storage"
        body = metaInfos + [
            f"Supported Databases will be AzureBlobStorage or DataLake",
        ]
    elif connectorType == 'cloud-stream-connector':
        header = "Connect to near-realtime Stream "
        body = metaInfos + [
            f"Supported Stream Connections will be via Kafka or MQTT Broker",
        ]

    return dbc.Modal(
        [
            dbc.ModalHeader(
                header,
                id={
                    'type': "dialog-connector-header",
                    'ctype': connectorType
                }
            ),
            dbc.ModalBody(
                body,
                id={
                    'type': "dialog-connector-body",
                    'ctype': connectorType
                }
            ),
            dbc.ModalFooter([
                dbc.Button(
                    "Cancel",
                    id={
                        'type': "dialog-connector-cancel",
                        'ctype': connectorType
                    },
                    n_clicks=0,
                    n_clicks_timestamp=0,
                    className="ml-auto"
                ),
                dbc.Button(
                    "Create Data Connector",
                    id={
                        'type': "dialog-connector-save-attributes",
                        'ctype': connectorType
                    },
                    n_clicks=0,
                    n_clicks_timestamp=0,
                    className="ml-auto"
                )
            ]),
        ],
        id={
            'type': "dialog-connector-attributes",
            'ctype': connectorType
        }
    )

