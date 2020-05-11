from datetime import datetime as dt
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, State, Output
from utils import fa, queryAnnotationClasses, createFigTemplate

from dash.exceptions import PreventUpdate

__version__ = "1.0"
PROJ_URL = "https://drahnreb.github.io/Mephisto"
PROJ_ISSUE_URL = "https://github.com/drahnreb/Mephisto/issues/"
PERSISTANCE = "memory" # session

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
        style={"background": "white", "z-index": 999}
    )


def initSelectData():
    """ select/import/upload data head """
    
    def _createCollapsableTabs():
        """ create more viewable space.
            collapse button and encapsulation
        """
        
        def _createConnectorTab():
            """ data connector status """
            return dbc.Tab(
                label="Data Connector status",
                disabled=True,
                children=[
                    dcc.Store(
                        data=[],
                        id="store-data-connector",
                        storage_type=PERSISTANCE,
                        modified_timestamp=-1
                    )
                    #dbc.Badge("", color="light", id="badge-connector")
                ],
                id='tab-data-connectors'
            )

        def _createExportTab():
            """ export data tab """
            return dbc.Tab(
                label="Export Data",
                disabled=True,
                children=[
                    dbc.Row(dbc.Col(
                        dbc.Button("Export", outline=True, color="success", id="btn-selectData-export"), width=2),
                            justify="center", align="center")
                ],
                id='tab-export-data'
            )
            
        def _createLoadDataTab():
            """ load data tab """
            return dbc.Tab(
                label="Load Data",
                id='tab-load-data',
                children=dbc.Row(
                    [
                        # upload local data
                        dbc.Col(
                            [
                                dbc.Label('Upload local data:', style={"font-weight": "bold"}),
                                dcc.Upload(
                                    id='upload-data',
                                    children=html.Div([
                                        'Drag and Drop or ',
                                        html.A('Select Files')
                                    ]),
                                    style={
                                        'width': '100%',
                                        'height': '60px',
                                        'lineHeight': '60px',
                                        'borderWidth': '1px',
                                        'borderStyle': 'dashed',
                                        'borderRadius': '5px',
                                        'textAlign': 'center',
                                        'margin': '10px'
                                    },
                                    # Allow multiple files to be uploaded
                                    multiple=True
                                ),
                            ],
                            # style={"border-right": "1px grey dash"},
                        ),
                        # connect to local database
                        dbc.Col([
                            dbc.Row(dbc.Col(dbc.Label('Connect to local database:', style={"font-weight": "bold"}))),
                            dbc.Row(dbc.Col(dbc.Button(
                                "Local Database (SciDB/PostgreSQL)",
                                color="secondary",
                                id="btn-local-connector-db",
                                disabled=False),
                                width=3), align="center", justify="center")
                        ],
                            # style={"border-right": "1px grey dash"},
                        ),
                        # setup new cloud connections
                        dbc.Col([
                            dbc.Row(dbc.Col(dbc.Label('Connect to cloud data:', style={"font-weight": "bold"}))),
                            dbc.Row(dbc.Col(dbc.Button(
                                "DataLake or BlobStorage",
                                color="secondary",
                                id="btn-cloud-connector-blob",
                                disabled=True),
                                width=3), align="center", justify="center")
                        ],
                            # style={"border-right": "1px grey dash"},
                        ),
                        # setup stream real-time connection
                        dbc.Col([
                            dbc.Row(dbc.Col(
                                dbc.Label('Connect to near-real-time data stream:', style={"font-weight": "bold"}))),
                            dbc.Row(dbc.Col(dbc.Button(
                                "Connect Stream",
                                color="light",
                                id="btn-cloud-connector-stream",
                                disabled=True),
                                width=3), align="center", justify="center")
                        ])

                    ]
                )
            )

        return dbc.Col([
            dbc.Collapse(
                [
                    dbc.Tabs([_createLoadDataTab()] + [_createConnectorTab()] + [_createExportTab()])
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
        graphPlaceholder = dbc.Container(
            children=[],
            fluid=True,
            className="pt-2",
            id="div-graphSpace"
        )
        
        # add graph button row
        return dbc.Row(dbc.Col([dbc.ButtonGroup(
            [
                dbc.Button(
                    [fa("fas fa-plus"), " 2D"],
                    n_clicks_timestamp=-1,
                    n_clicks=0,
                    id="btn-createGraph2D"
                ),
                dbc.Button(
                    [fa("fas fa-plus"), " 3D"],
                    n_clicks_timestamp=-1,
                    n_clicks=0,
                    id="btn-createGraph3D"
                )
            ],
            size="md",
            className="mr-1",
        )], width=1, className="p-2"), justify="end")
            # dbc.Row(dbc.Col([dbc.Button(fa("fas fa-plus"), color="dark", id="btn-create-graph")], width=1, className="p-2"), justify="end")
        
    def _createAnnotationSpace():
        """ annotation class space """
        def _createEffectView():
            return [
                dbc.Col(
                    [
                        # selection from existing classes
                        dbc.Row(dbc.Col([
                            dbc.Label("Select from existing effects", style={"font-weight": "bold"}),
                            dcc.Dropdown(
                                id="dropdown-effect-category-selector",
                                options=queryAnnotationClasses(atype='ecat'), # Spawned list of dict options {'label': 'l1', 'value': 'v1'} during session
                                value=None,
                                placeholder="Type to search...",
                                searchable=True,
                                clearable=True,
                                multi=False,
                                persistence=True,
                                persistence_type=PERSISTANCE
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
                                        persistence_type=PERSISTANCE,
                                        id="input-new-effect-category"
                                    ),
                                    dbc.FormText("Try to select from available effects. Care about naming conventions!"),
                                    dbc.Button("Save in database",
                                        color="info",
                                        outline=True,
                                        block=True,
                                        n_clicks_timestamp=-1,
                                        id="btn-add-effect-category")
                                ]
                            )
                        ])),
                        html.Hr(),
                        # specific effect subcategory
                        dbc.Row(dbc.Col([
                                dbc.Label("Specific effect subcategory", style={"font-weight": "bold"}, id='label-effect-subcategory'),
                                dcc.Dropdown(
                                    id="dropdown-effect-subcategory-selector",
                                    options=[], # Spawned list of dict options {'label': 'l1', 'value': 'v1'} during session
                                    placeholder="Type to search...",
                                    searchable=True,
                                    clearable=True,
                                    multi=True,
                                    persistence=True,
                                    persistence_type=PERSISTANCE)
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
                                        persistence_type=PERSISTANCE,
                                        id="input-new-effect-subcategory"
                                    ),
                                    dbc.FormText("Try to select from available sub-effects. Care about naming conventions!"),
                                    dbc.Button("Save in database",
                                        color="info",
                                        outline=True,
                                        block=True,
                                        n_clicks_timestamp=-1,
                                        id="btn-add-effect-subcategory")
                                ]
                            )
                        ]), id="div-add-effect-subcategory", style={"visibility": "hidden"}),
                        # samples with same class assignment
                        dbc.Row([
                            dcc.Store(
                                data={'class': '', 'data': []},
                                id="store-similar-effect-samples",
                                modified_timestamp=-1,
                                storage_type=PERSISTANCE
                            ),
                            dbc.Col([
                                html.Hr(),
                                dbc.Label("Other samples with same effect", style={"font-weight": "bold"}),
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
                        dbc.Label("Select from existing causes", style={"font-weight": "bold"}),
                        dcc.Dropdown(
                            id="dropdown-cause-category-selector",
                            options=queryAnnotationClasses(atype='ccat'), # Spawned list of dict options {'label': 'l1', 'value': 'v1'} during session
                            value=None,
                            placeholder="Type to search...",
                            searchable=True,
                            clearable=True,
                            multi=False,
                            persistence=True,
                            persistence_type=PERSISTANCE
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
                                    persistence_type=PERSISTANCE,
                                    id="input-new-cause-category"
                                ),
                                dbc.FormText("Try to select from available cause. Care about naming conventions!"),
                                dbc.Button("Save in database",
                                    color="info",
                                    outline=True,
                                    block=True,
                                    n_clicks_timestamp=-1,
                                    id="btn-add-cause-category")
                            ]
                        )
                    ])),
                    html.Hr(),
                    # specific effect subcategory
                    dbc.Row(dbc.Col([
                            dbc.Label("Specific cause subcategory", style={"font-weight": "bold"}, id='label-cause-subcategory'),
                            dcc.Dropdown(
                                id="dropdown-cause-subcategory-selector",
                                options=[], # Spawned list of dict options {'label': 'l1', 'value': 'v1'} during session
                                placeholder="Type to search...",
                                searchable=True,
                                clearable=True,
                                multi=True,
                                persistence=True,
                                persistence_type=PERSISTANCE)
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
                                    persistence_type=PERSISTANCE,
                                    id="input-new-cause-subcategory"
                                ),
                                dbc.FormText("Try to select from available sub-causes. Care about naming conventions!"),
                                dbc.Button("Save in database",
                                    color="info",
                                    outline=True,
                                    block=True,
                                    n_clicks_timestamp=-1,
                                    id="btn-add-cause-subcategory")
                            ]
                        )
                    ]), id="div-add-cause-subcategory", style={"visibility": "hidden"}),
                    # samples with same class assignment
                    dbc.Row([
                        dcc.Store(
                            data={'class': '', 'data': []},
                            id="store-similar-cause-samples",
                            modified_timestamp=-1,
                            storage_type=PERSISTANCE
                        ),
                        dbc.Col([
                            html.Hr(),
                            dbc.Label(f"Other samples with same cause", style={"font-weight": "bold"}),
                            dbc.ListGroup(
                                children=[],
                                id="listgroup-similar-cause-samples"
                            )
                        ], id="div-samples-cause")
                    ])
                ])
            ]


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
                    dbc.Col(dbc.Button(children=[fa("fas fa-link"), "  multivariate Linking"], outline=True, block=True,
                                       color="secondary", n_clicks_timestamp=-1, n_clicks=0, id="btn-tools-linker", active=False, className="p-1"), className="p-1")
                    # ,xl=6
                ], className="m-1", justify="between"),
            ], fluid=True, id="div-toolbar", style={'position': 'sticky', 'bottom': 0, "z-index": 5})
        
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
                    n_clicks_timestamp=-1,
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
                        n_clicks_timestamp=-1,
                        n_clicks=0,
                        disabled=True,
                        id="btn-workspace-reset"),
                    id='confirm-dialog-reset',
                    submit_n_clicks_timestamp=-1,
                    message='All annotions since last save will be deleted! Are you sure you want to continue?'
                    )
                ),
                className="my-4"),
        ]
        
    return dbc.Row(
        [
            dbc.Col(
                children=_createAnnotationSpace(),
                style={"border-right": "1px grey solid"},  # 'position':'sticky', 'top':0},
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
        style={"z-index": 5}
    )


##########
# LAYOUT
##########
def serve_layout():
    return dbc.Container([
        ## div-head-desc
        initHead(),
        ## div-select-data
        initSelectData(),
        ## div-workspace
        # style={"height": "calc(100vh)"}, # stretch row over entire screen #-200px
        initWorkspace(),
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
    return dbc.Col([
                str(strConnectorDesc),
                dbc.Progress(
                    value=0,
                    style={"height": "1px"},
                    id={
                        "type": "prg-data-connector",
                        "index": idx
                    },
                )],
            id={
                "type": "div-data-connector",
                "index": idx
            }
        )


def spawnGraph(idx, kind, listDictAllFeatures, strEQ, strType, intNDim, strMinDate, strMaxDate):
    """ 
        fig: json with link to aggregate or pre-cached dataframe to load into plotly graph
        meta: schema with suplimental information
    """
    if kind == 'scatter':
        selectSamplesRow = [
        dbc.Row(
            dbc.FormText(
                f"Machine EQ: {strEQ}. Date Range: {strMinDate} - {strMaxDate}. Data Source: {strType}.",
                id={
                    "type": "formtext-feature",
                    "index": idx,
                    # "eq": strEQ,
                    # "type": strType
                }
            )
        ),
        dbc.Row([
            dbc.Col(
                dbc.FormGroup([
                    dbc.Select(
                        id={
                            "type": "select-feature",
                            "index": idx,
                            # "eq": strEQ,
                            # "type": strType
                        },
                        options=listDictAllFeatures
                    ),
                ]),
                width=6,
            ),
            dbc.Col(
                dbc.Button(
                    fa("fas fa-plus"),
                    color="secondary",
                    id={
                        "type": "btn-add-feature",
                        "index": idx,
                        # "eq": strEQ,
                        # "type": strType
                    }
                ),
                width=1
            ),
            dbc.Col(
                dbc.FormGroup(
                    [
                        dbc.Input(
                            placeholder="no. of sample(s)",
                            valid=None,
                            id={
                                "type": "inp-class-definition",
                                "index": idx,
                                # "eq": strEQ,
                                # "type": strType
                            }
                        ),
                        # SPAWN
                        dbc.FormText(
                            f"of total: {intNDim}",
                            id={
                                "type": "formtext-class-definition",
                                "index": idx,
                                # "eq": strEQ,
                                # "type": strType
                            }
                        )
                    ]
                ),
                width=2
            ),
            dbc.Col([
                dbc.Row([
                    dbc.Button(fa("fas fa-redo-alt"), outline=True, color="info", className="mr-1", size="sm"),
                    dbc.Label("  Choose:"),
                ]),
                dbc.Row(dbc.RadioItems(
                    options=[
                        # als toolbox {"label": "iid", "value": "iid"},
                        {"label": "randomly", "value": "random"},  # uniform distribution
                        {"label": "by sequence", "value": "sequence"}
                    ],
                    value=None,
                    id={
                        "type": "select-sample-selection-type",
                        "index": idx,
                        # "eq": strEQ,
                        # "type": strType
                    }
                ))
            ], width=1
            ),
            dbc.Col(
                dcc.DatePickerSingle(
                    id={
                        "type": "select-sample-selection-datepicker",
                        "index": idx,
                        # "eq": strEQ,
                        # "type": strType
                    },
                    min_date_allowed=strMinDate,
                    max_date_allowed=strMaxDate,
                    display_format="DD.MM.YYYY",
                    placeholder="Start Date",
                    clearable=True,
                    with_portal=True,
                    first_day_of_week=1
                ),
                style={"visibility": "visible"},
                width=2,
                className="dash-bootstrap"
            )
            ], style={"margin": "5px"})
        ]
    else:
        selectSamplesRow = []


    return dbc.Container(
            selectSamplesRow + [
            dbc.Row([
                dcc.Graph(
                    id={
                        "type": "graph",
                        "index": idx,
                        # "eq": strEQ,
                        # "type": strType
                    },
                    figure=createFigTemplate(kind),
                    config=dict(
                        showTips=True, responsive=True, scrollZoom=True,
                        showLink=False, displaylogo=False, watermark=False,
                        modeBarButtonsToRemove=['sendDataToCloud'], showSendToCloud=False,
                        showEditInChartStudio=False,
                        # editable=True,
                        edits={  # make following annotations editable
                            # The main anchor of the annotation, which is the text (if no arrow)
                            # or the arrow (which drags the whole thing leaving the arrow length & direction unchanged)
                            'annotationPosition': True,
                            # Just for annotations with arrows, change the length and direction of the arrow
                            'annotationTail': True,
                            # change label text
                            'annotationText': True,
                        },
                        queueLength=10,  # Set the length of the undo/redo queue,
                        autosizable=True,
                        doubleClick='autosize',
                        showAxisDragHandles=True,
                        displayModeBar=True,  # always show modebar
                    ),
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
            # dbc.Row(dbc.Col(dbc.Button(fa("fas fa-minus"), color="danger", block=True, outline=True, size="sm", id=f"btn-remove-graph_{idx}"), width=1, className="p-1"), justify="end", align="end"),
            html.Hr(
                className="m-3",
                n_clicks_timestamp=-1,
                id={
                    "type": "btn-remove-graph",
                    "index": idx,
                    # "eq": strEQ,
                    # "type": strType
                },
            )
        ], fluid=True, className="pt-2"
    )
