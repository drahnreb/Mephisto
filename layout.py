from datetime import datetime as dt

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, State, Output
from utils import fa

from dash.exceptions import PreventUpdate
# import adapt.sup.siemens as siemens # read_json

__version__ = "0.1"
PROJ_URL = "https://d.ai/mephisto"
PROJ_ISSUE_URL = "https://git.daimler.com/I40PT/Mephisto/issues/new"


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
                    dbc.Col(
                        #TODO TEST!
                        [spawnDataConnector('test', idx=1)],
                        id='div-data-connectors'
                    ),
                    dbc.Badge("", color="light", id="badge-connector"),
                    # color: primary==uploading, success==allready, danger==error
                ]
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
                ]
            )
            
        def _createLoadDataTab():
            """ load data tab """

            return dbc.Tab(
                label="Load Data",
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
    
        def _createClassView():
            return [
                dbc.Col(
                    [
                        # selection from existing classes
                        dbc.Row(dbc.Col([
                            dbc.Label("Select existing class", style={"font-weight": "bold"}),
                            dbc.FormGroup([
                                dbc.RadioItems(
                                    id="radio-class-selector",
                                    options=[
                                        # DB-dependant SPAWN
                                        # randomize
                                        {"label": "normal", "value": "class_normal"},
                                        {"label": "tool wear", "value": "class_tool_wear"},
                                        {"label": "tool failure", "value": "class_tool_failure"},
                                    ],
                                    inline=False,
                                    value=None,
                                ),
                            ])
                        ])),
                        # definition of new class
                        dbc.Row(
                            dbc.InputGroup(
                                # TODO: class and subclass
                                [
                                    dbc.InputGroupAddon(dbc.RadioButton(), addon_type="prepend"),
                                    dbc.InputGroupAddon(
                                        dbc.Button("save for others", id="input-group-button"),
                                        addon_type="append",
                                    ),
                                    dbc.Input(
                                        placeholder="define new class...",
                                        valid=None,  # SPAWN: green when synced with cloud
                                        id="inp-class-definition"
                                    )
                                ]
                            )
                        ),
                        html.Hr(),
                        # subclass specific type
                        dbc.Row(dbc.Col([
                            dbc.Label("Subclass for class type ", style={"font-weight": "bold"}, id='label-subclass'),
                            dbc.FormGroup([
                                dbc.RadioItems(
                                    id="radio-class-type-selector",
                                    options=[
                                        # DB-dependant SPAWN
                                        {"label": "tool wear solidified", "value": "class_tool_wear_solidified"},
                                        {"label": "tool wear through cooling", "value": "class_tool_wear_cooling"},
                                    ],
                                    inline=False,
                                    value=None,
                                ),
                            ])
                        ])),
                        # samples with same class assignment
                        dbc.Row(dbc.Col([
                            html.Hr(),
                            dbc.Label("Sample with same assigned class", style={"font-weight": "bold"}),
                            dbc.ListGroup([
                                # DB-dependant: SPAWN sample item
                                dbc.ListGroupItem(
                                    [
                                        dbc.Row([
                                            dbc.Col("01.01.2000 01:01:04"),
                                            dbc.Col(dbc.Badge(
                                                "plot 1",  # plot number
                                                color="info",
                                                style={"visibility": "hidden"}  # set when button pressed to display
                                            ))
                                        ], justify="between")
                                    ],
                                    id="list-class-similar-samples",
                                    n_clicks=0,
                                    action=True
                                ),
                                dbc.ListGroupItem(
                                    [
                                        dbc.Row([
                                            dbc.Col("01.01.2000 13:33:04"),
                                            dbc.Col(dbc.Badge(
                                                "plot 1",  # plot number
                                                color="info",
                                                style={"visibility": "visible"}  # set when button pressed to display
                                            ))
                                        ], justify="between")
                                    ],
                                    id="list-class-similar-samples-2",
                                    n_clicks=0,
                                    action=True
                                ),
                            ])
                        ]))
                    ]
                )
            ]

        def _createCauseView():
            return [
                # anomaly / class cause
                dbc.Col(
                    [
                        # selection of existing causes
                        dbc.Row(dbc.Col([
                            dbc.Label("Select existing cause", style={"font-weight": "bold"}),
                            dbc.FormGroup([
                                dbc.RadioItems(
                                    id="radio-cause-selector",
                                    options=[
                                        # DB-dependant SPAWN
                                        {"label": "axial speed above 50rpm", "value": True},
                                        {"label": "cooling below 23°", "value": False},
                                    ],
                                    inline=False,
                                    value=None,
                                ),
                            ])
                        ])),
                        # definition of new cause
                        dbc.Row(dbc.Col([
                            dbc.Input(
                                placeholder="define new cause...",
                                valid=None,  # True
                                id="inp-cause-definition"
                            )
                        ])),
                        html.Hr(),
                        # comments
                        dbc.Row(dbc.Col(dbc.Input(
                            placeholder="additional comment (optional)",
                            valid=None,  # saved:True
                            id="input-comment"
                        )))
                    ]
                )
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
                                       color="secondary", id="btn-tools-linker", className="p-1"), className="p-1")
                    # ,xl=6
                ], className="m-1", justify="between"),
            ], fluid=True, id="div-toolbar", style={'position': 'sticky', 'bottom': 0, "z-index": 5})
        
        return [
            dbc.Row(_createToolbar()),
            html.Hr(),
            dbc.Row(_createClassView()),
            html.Hr(),
            dbc.Row(_createCauseView()),
            dbc.Row(dbc.Col(
                dbc.Button([
                        "Next phenomenon",
                        dcc.Loading(
                            id="loading-2",
                            children=html.Div(id="loading-workspace-save"),
                            type="circle",
                        )],
                    outline=False,
                    block=True,
                    color="success",
                    n_clicks_timestamp=-1,
                    id="btn-workspace-save")),
                className="my-4"),
            dbc.Row(dbc.Col(
                dbc.Button("Reset",
                    outline=True,
                    block=True,
                    color="danger",
                    n_clicks_timestamp=-1,
                    id="btn-workspace-reset")),
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

def spawnDataConnector(data_desc, idx):
    return dbc.Row(
        dbc.Col([
            str(data_desc),
            dbc.Progress(
                value=0,
                style={"height": "1px"},
                id={
                    "type": "prg-data-connector",
                    "index": idx
                },
            )
        ]),
        id={
            "type": "div-data-connector",
            "index": idx
        },
    )


def spawnGraph2D(idx, fig, listDictAllFeatures, strEQ, strType, intNDim, strMinDate, strMaxDate):
    """ 
        fig: json with link to aggregate or pre-cached dataframe to load into plotly graph
        meta: schema with suplimental information
    """

    return dbc.Container([
        dbc.Row([
            dbc.Col(
                dbc.FormGroup([
                    dbc.Select(
                        id={
                            "type": "select-feature",
                            "index": idx
                        },
                        options=listDictAllFeatures
                    ),
                    dbc.FormText(
                        f"Machine EQ: {strEQ}. Date Range: {strMinDate} - {strMaxDate}. Data Source: {strType}.",
                        id={
                            "type": "formtext-feature",
                            "index": idx
                        }
                   )
                ]),
                width=6,
            ),
            dbc.Col(
                dbc.Button(
                    fa("fas fa-plus"),
                    color="secondary",
                    id={
                        "type": "btn-add-feature",
                        "index": idx
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
                                "index": idx
                            }
                        ),
                        # SPAWN
                        dbc.FormText(
                            f"of total: {intNDim}",
                            id={
                                "type": "formtext-class-definition",
                                "index": idx
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
                        "index": idx
                    }
                ))
            ], width=1
            ),
            dbc.Col(
                dcc.DatePickerSingle(
                    id={
                        "type": "select-sample-selection-datepicker",
                        "index": idx
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
            ], style={"margin": "5px"}),
            dbc.Row([
                dcc.Graph(
                    id={
                        "type": "graph-2d",
                        "index": idx
                    },
                    figure=fig,
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
                    "type": "row-graph-2d",
                    "index": idx
                },
            ),
            # dbc.Row(dbc.Col(dbc.Button(fa("fas fa-minus"), color="danger", block=True, outline=True, size="sm", id=f"btn-remove-graph_{idx}"), width=1, className="p-1"), justify="end", align="end"),
            html.Hr(
                className="m-3",
                n_clicks_timestamp=-1,
                id={
                    "type": "btn-remove-graph-2d",
                    "index": idx
                },
            )
        ], fluid=True, className="pt-2"
    )
