import dash
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_html_components as html
import dash_core_components as dcc

from dash.exceptions import PreventUpdate
from layout import spawnGraph2D
from utils import createFig, queryData
import numpy as np

import time

def register_callbacks(app):
    # ctx = dash.callback_context
    #if not ctx.triggered:
        #button_id = 'No clicks yet'
    #else:
        #button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    #ctx_msg = json.dumps({
        #'states': ctx.states,
        #'triggered': ctx.triggered,
        #'inputs': ctx.inputs
    #}, indent=2)
    
    @app.callback(
        Output('div-graphSpace', 'children'),
        [Input('btn-createGraph2D', 'n_clicks_timestamp'),
         Input('btn-createGraph3D', 'n_clicks_timestamp'),
         Input({'type': 'btn-remove-graph-2d', 'index': ALL}, 'n_clicks_timestamp')],
        [State('div-graphSpace', 'children')])
    def addRemoveGraph(create2D, create3D, listRemove, listGraphSpaceChildren):
        ctx = dash.callback_context
        if not ctx.triggered: #create2D == create3D:
            raise PreventUpdate
        else:
            prop_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
        if "btn-remove-graph-2d" in prop_id:
            idx = eval(prop_id).get('index')
            if idx:
                #TODO: fragile. causes trouble with rest of callbacks
                #del listGraphSpaceChildren[idx-1]
                return listGraphSpaceChildren
        
        intGraphIdx = len(listGraphSpaceChildren)
        # test
        meta = dict(
            eq="404000500065",
            dataType="NC",
            schema=[
                # based on meta information derived from schema /dataframe header
                {"label": "Antriebsmomenten-Sollwert einer Achse/Spindel an X2",
                 "value": "aaTorque_X2"},
                {"label": "Antriebsauslastung einer Achse/Spindel an X2",
                 "value": "aaLoad_X2"},
                {"label": "Antriebsstrom-Istwert einer Achse/Spindel an X2",
                 "value": "aaCurr_X2"},
                {"label": "Antriebswirkleistung einer Achse/Spindel an X2",
                 "value": "aaPower_X2"},
            ]
        )
          
        #TODO:
        # meta. meta: schema with suplimental information 
        # data: json with link to aggregate or pre-cached dataframe to load into plotly graph
        dat = queryData(intGraphIdx-1, None)
        if not len(dat):
            raise PreventUpdate
        fig = createFig(intGraphIdx-1)
        # {
        #     'data': fetch_data(data, dim="2D"),
        #     'layout': create_layout2D() # figure.layout.autosize to True and unsetting figure.layout.height and figure.layout.width.
        # },
        listDictAllFeatures = meta.get('schema')
        strEQ = meta.get('eq')
        strType = meta.get('type')
        intNDim = dat.shape[0]
        strMinDate = min(dat)
        strMaxDate = max(dat)

        if create2D > create3D:
            newGraph = spawnGraph2D(intGraphIdx, fig=fig, listDictAllFeatures=listDictAllFeatures, strEQ=strEQ, strType=strType, intNDim=intNDim, strMinDate=strMinDate, strMaxDate=strMaxDate)
        else:
            newGraph = spawnGraph3D(intGraphIdx, fig=fig, listDictAllFeatures=listDictAllFeatures, strEQ=strEQ, strType=strType, intNDim=intNDim, strMinDate=strMinDate, strMaxDate=strMaxDate)
            
        listGraphSpaceChildren.insert(0, newGraph)
            
        return listGraphSpaceChildren


    @app.callback(
        Output({'type': 'graph-2d', 'index': MATCH}, 'config'),
        [Input({'type': 'select-feature', 'index': MATCH}, 'value')],
        [State({'type': 'select-feature', 'index': MATCH}, 'options'),
         State({'type': 'graph-2d', 'index': MATCH}, 'config')]
    )
    def changeSaveFilename(strSelectedValue, listDictAllFeatures, config):
        if not strSelectedValue:
            raise PreventUpdate
        else:
            print(strSelectedValue)
            strLabel = [dictOption['label'] for dictOption in listDictAllFeatures if strSelectedValue in dictOption['value']][0]
            print(strLabel)
            config['toImageButtonOptions'] = {
                'format': 'png',
                'filename': f"{strSelectedValue}-{strLabel}_Mephisto.png",
            }
                
        return config
    
    
    @app.callback(
        Output('loading-workspace-save', 'children'),
        [Input('btn-workspace-save', 'n_clicks_timestamp'),
         Input('btn-workspace-reset', 'n_clicks_timestamp')],
        #[State({'type': 'graph-2d', 'index': MATCH}, 'clickData'), #Data from latest click event.
        # State({'type': 'graph-2d', 'index': MATCH}, 'clickAnnotationData'), #Data from latest click annotation event.
        # State({'type': 'graph-2d', 'index': MATCH}, 'selectedData') #Data from latest select event.
        # ]
    )
    def saveResetAnnotations(save, reset): #, dictClickData, dictclickAnnotationData, dictSelectedData
        if save == reset:
            raise PreventUpdate
        elif save > reset:
            #print('save', dictClickData, dictclickAnnotationData, dictSelectedData)
            time.sleep(1)
            return 
        else:
            #print('reset', dictClickData, dictclickAnnotationData, dictSelectedData)
            time.sleep(5)
            return
                
        return config
        
    @app.callback(
        Output('btn-tools-linker', 'active'),
        [Input('btn-tools-linker', 'n_clicks')],
        [State('btn-tools-linker', 'active')]
    )
    def activateMultivariateLinking(clicked, linkingActive):
        if clicked:
            #TODO: we need to track multiple graph annotations. not just latest but also all annotations and link them.
            linkingActive = not linkingActive
        return linkingActive
    
