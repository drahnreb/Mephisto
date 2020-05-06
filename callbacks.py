import dash
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_html_components as html
import dash_core_components as dcc

from dash.exceptions import PreventUpdate
from layout import spawnGraph2D, spawnSimilarSamples, spawnDataConnector
from utils import createFig, queryData, queryAnnotationClasses, storeAnnotationClasses, fa, querySimilarSamples
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
            strLabel = [dictOption['label'] for dictOption in listDictAllFeatures if strSelectedValue in dictOption['value']][0]
            config['toImageButtonOptions'] = {
                'format': 'png',
                'filename': f"{strSelectedValue}-{strLabel}_Mephisto.png",
            }
                
        return config
    
    
    @app.callback(
        [Output('loading-workspace-save', 'children'),
         Output('alert-saved', 'is_open'),
         Output('tab-export-data', 'disabled')],
        [Input('btn-workspace-save', 'n_clicks')],
        [State('btn-tools-linker', 'active'),
         State('tab-export-data', 'disabled')
        #[State({'type': 'graph-2d', 'index': MATCH}, 'clickData'), #Data from latest click event.
        # State({'type': 'graph-2d', 'index': MATCH}, 'clickAnnotationData'), #Data from latest click annotation event.
        # State({'type': 'graph-2d', 'index': MATCH}, 'selectedData') #Data from latest select event.
        ]
    )
    def saveAnnotations(save, linkingActive, boolExportDisabled): #, dictClickData, dictclickAnnotationData, dictSelectedData
        success = False

        if not save:
            raise PreventUpdate
        else:
            #TODO: we need to track multiple graph annotations. not just latest but also all annotations and link them.
            if linkingActive:
                print('save linked')#, dictClickData, dictclickAnnotationData, dictSelectedData)
            time.sleep(5)
            success = True

        if boolExportDisabled:
            boolExportDisabled = success

        return [], success, boolExportDisabled

        
    @app.callback(
        Output('btn-tools-linker', 'active'),
        [Input('confirm-dialog-reset', 'submit_n_clicks_timestamp'),
         Input('btn-tools-linker', 'n_clicks_timestamp')],
        [State('btn-tools-linker', 'active')]
    )
    def resetWorkspace(reset, link, linkingActive):
        if reset == link:
            raise PreventUpdate
        elif reset > link:
            linkingActive = False
            # TODO: reset all annotations and no selection of classes.
        else:
            linkingActive = not linkingActive
        return linkingActive
    

    @app.callback(
        [Output('collapse-data-connection', 'is_open'),
         Output('btn-select-data_collapse', 'children')],
        [Input('btn-select-data_collapse', 'n_clicks')],
        [State('collapse-data-connection', 'is_open')]
    )
    def makeSomeSpace(clicked, is_open):
        if not clicked:
            raise PreventUpdate
        else:
            if is_open:
                state = fa("fas fa-chevron-down")
            else:
                state = fa("fas fa-chevron-up")

        return not is_open, state


    @app.callback(
        [Output('btn-add-effect-category', 'disabled'),
         Output('btn-add-cause-category', 'disabled'),
         Output('btn-add-effect-subcategory', 'disabled'),
         Output('btn-add-cause-subcategory', 'disabled')],
        [Input('input-new-effect-category', 'value'),
         Input('input-new-cause-category', 'value'),
         Input('input-new-effect-subcategory', 'value'),
         Input('input-new-cause-subcategory', 'value')]
    )
    def activateAddCategory(inputEffect, inputCause, inputSubEffect, inputSubCause):
        effectDisabled = False if inputEffect else True
        causeDisabled = False if inputCause else True
        subEffectDisabled = False if inputSubEffect else True
        subCauseDisabled = False if inputSubCause else True

        return effectDisabled, causeDisabled, subEffectDisabled, subCauseDisabled


    @app.callback(
        [Output('dropdown-effect-category-selector', 'options'),
         Output('dropdown-effect-category-selector', 'value'),
         Output('dropdown-cause-category-selector', 'options'),
         Output('dropdown-cause-category-selector', 'value')],
        [Input('btn-add-effect-category', 'n_clicks_timestamp'),
         Input('btn-add-cause-category', 'n_clicks_timestamp')],
        [State('dropdown-effect-category-selector', 'value'),
         State('dropdown-cause-category-selector', 'value'),
         State('input-new-effect-category', 'value'),
         State('input-new-cause-category', 'value'),
         State('dropdown-effect-category-selector', 'options'),
         State('dropdown-cause-category-selector', 'options')]
    )
    def saveLoadAnnotationClasses(effectpressed, causepressed,
        selectedEffects, selectedCauses,
        strEffectInput, strCauseInput,
        listEffectOptions, listCauseOptions):
        if effectpressed == causepressed:
            listEffectOptions = queryAnnotationClasses(atype='ecat')
            listCauseOptions = queryAnnotationClasses(atype='ccat')

        elif effectpressed > causepressed:
            # new effect, reset selection
            selectedEffects = None
            if strEffectInput:
                listEffectOptions = storeAnnotationClasses(strEffectInput, atype='ecat')
        else:
            selectedCauses = None
            if strCauseInput:
                listCauseOptions = storeAnnotationClasses(strCauseInput, atype='ccat')
        
        return listEffectOptions, selectedEffects, listCauseOptions, selectedCauses


    @app.callback(
        [Output('div-effect-subcategory', 'style'),
         Output('div-add-effect-subcategory', 'style'),
         Output('div-samples-effect', 'style'),
         Output('div-cause-subcategory', 'style'),
         Output('div-add-cause-subcategory', 'style'),
         Output('div-samples-cause', 'style')],
        [Input('dropdown-effect-category-selector', 'value'),
         Input('dropdown-cause-category-selector', 'value')],
        [State('div-effect-subcategory', 'style'),
         State('div-cause-subcategory', 'style')]
    )
    def showSubClasses(listSelectedEffects, listSelectedCauses,
        dictSubeffectVisible, dictSubcauseVisible
        ):
        if listSelectedEffects:
            dictSubeffectVisible = {"visibility": "visible"}
        if listSelectedCauses:
            dictSubcauseVisible = {"visibility": "visible"}

        return dictSubeffectVisible, dictSubeffectVisible, dictSubeffectVisible, dictSubcauseVisible, dictSubcauseVisible, dictSubcauseVisible


    @app.callback(
        [Output('dropdown-effect-subcategory-selector', 'options'),
         Output('dropdown-effect-subcategory-selector', 'value'),
         Output('dropdown-cause-subcategory-selector', 'options'),
         Output('dropdown-cause-subcategory-selector', 'value')],
        [Input('btn-add-effect-subcategory', 'n_clicks_timestamp'),
         Input('btn-add-cause-subcategory', 'n_clicks_timestamp')],
        [State('dropdown-effect-subcategory-selector', 'value'),
         State('dropdown-cause-subcategory-selector', 'value'),
         State('input-new-effect-subcategory', 'value'),
         State('input-new-cause-subcategory', 'value'),
         State('dropdown-effect-subcategory-selector', 'options'),
         State('dropdown-cause-subcategory-selector', 'options')]
    )
    def saveLoadSubClasses(subeffectpressed, subcausepressed,
        selectedSubeffects, selectedSubcauses,
        strSubEffectInput, strSubCauseInput,
        listSubEffectOptions, listSubCauseOptions):
        if subeffectpressed == subcausepressed:
            listSubEffectOptions = queryAnnotationClasses(atype='esubcat')
            listSubCauseOptions = queryAnnotationClasses(atype='csubcat')

        elif subeffectpressed > subcausepressed:
            # new effect, reset selection
            selectedSubeffects = None
            if strSubEffectInput:
                listSubEffectOptions = storeAnnotationClasses(strSubEffectInput, atype='esubcat')
        else:
            selectedSubcauses = None
            if strSubCauseInput:
                listSubCauseOptions = storeAnnotationClasses(strSubCauseInput, atype='csubcat')
        
        return listSubEffectOptions, selectedSubeffects, listSubCauseOptions, selectedSubcauses


    @app.callback(
        [Output('listgroup-similar-effect-samples', 'children'),
         Output('listgroup-similar-cause-samples', 'children')],
        [Input('dropdown-effect-category-selector', 'value'),
         Input('dropdown-cause-category-selector', 'value')],
    )
    def spawnSimilarSamples(listSelectedEffects, listSelectedCauses):
        effectsamples, causesamples = [], []
        idx = 0
        if listSelectedEffects:
            for effect in listSelectedEffects:
                dat = querySimilarSamples(effect)
                for d in dat:
                    idx+=1
                    e = spawnSimilarSamples(d, idx, atype='effect')
                    effectsamples.append(e)

        if listSelectedCauses:
            for cause in listSelectedCauses:
                dat = querySimilarSamples(cause)
                for d in dat:
                    idx+=1
                    c = spawnSimilarSamples(d, idx, atype='cause')
                    causesamples.append(c)

        return effectsamples, causesamples


    @app.callback(
        [Output('tab-data-connectors', 'children'),
         Output('tab-data-connectors', 'disabled')],
        [Input('store-data-connector', 'modified_timestamp')],
        [State('tab-data-connectors', 'children'),
         State('tab-data-connectors', 'disabled'),
         State('store-data-connector', 'data')]
    )
    def spawnData(newConnector, listAvailableDataConnectors, disabled, listMetainfo):
        if not listMetainfo or not newConnector:
            raise PreventUpdate

        for idx, m in enumerate(listMetainfo):
            listAvailableDataConnectors.append(spawnDataConnector(f"EQ: {m['eq']}\n'+f'{m['desc']}", idx=idx))

        nConnectors = len(listAvailableDataConnectors)

        if nConnectors:
            listAvailableDataConnectors = dbc.Row(
                [listAvailableDataConnectors]
            )
            disbaled = False
        else:
            disabled = True

        return listAvailableDataConnectors, disabled


#anything uploading??
#                        "", color="light", id="badge-connector"),
                    # color: primary==uploading, success==allready, danger==error


# click on similar samples to plot in another plot