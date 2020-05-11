import dash
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

from dash.exceptions import PreventUpdate
from utils import createFigTemplate, queryData, queryAnnotationClasses, storeAnnotationClasses, fa, querySimilarSamples
from layout import spawnGraph, spawnSimilarSamples, spawnDataConnector
import numpy as np

import time

def register_callbacks(app):    
    @app.callback(
        [Output('div-graphSpace', 'children'),
         Output('btn-workspace-save', 'disabled')],
        [Input('btn-createGraph2D', 'n_clicks_timestamp'),
         Input('btn-createGraph3D', 'n_clicks_timestamp'),
         Input({'type': 'btn-remove-graph-2d', 'index': ALL}, 'n_clicks_timestamp')],
        [State('div-graphSpace', 'children')])
    def addRemoveGraph(create2D, create3D, listRemove, listGraphSpaceChildren):
        boolSaveBtnDisabled = True
        ctx = dash.callback_context
        if not ctx.triggered:
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

        listDictAllFeatures = meta.get('schema')
        strEQ = meta.get('eq')
        strType = meta.get('dataType')
        intNDim = dat.shape[0]
        strMinDate = str(min(dat))[:-3]
        strMaxDate = str(max(dat))[:-3]

        if create2D > create3D:
            newGraph = spawnGraph(intGraphIdx,
                kind='scatter', 
                listDictAllFeatures=listDictAllFeatures,
                strEQ=strEQ,
                strType=strType,
                intNDim=intNDim,
                strMinDate=strMinDate,
                strMaxDate=strMaxDate
            )
        else:
            newGraph = spawnGraph(intGraphIdx,
                kind='scatter3d',
                listDictAllFeatures=listDictAllFeatures,
                strEQ=strEQ,
                strType=strType,
                intNDim=intNDim,
                strMinDate=strMinDate,
                strMaxDate=strMaxDate
            )
            
        listGraphSpaceChildren.insert(0, newGraph)
        if len(listGraphSpaceChildren):
            boolSaveBtnDisabled = False
            
        return listGraphSpaceChildren, boolSaveBtnDisabled


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
         Input('btn-add-cause-category', 'n_clicks_timestamp'),
         Input('btn-workspace-reset', 'n_clicks_timestamp')],
        [State('dropdown-effect-category-selector', 'value'),
         State('dropdown-cause-category-selector', 'value'),
         State('input-new-effect-category', 'value'),
         State('input-new-cause-category', 'value'),
         State('dropdown-effect-category-selector', 'options'),
         State('dropdown-cause-category-selector', 'options')]
    )
    def saveResetAnnotationClasses(effectpressed, causepressed, resetpressed,
        selectedEffect, selectedCause,
        strEffectInput, strCauseInput,
        listEffectOptions, listCauseOptions):
        save = np.argmax((resetpressed, effectpressed, causepressed))
        if not save:
            # also init
            selectedEffect = ''
            selectedCause = ''

        elif save == 1:
            # new effect, reset selection
            selectedEffect = ''
            if strEffectInput:
                listEffectOptions = storeAnnotationClasses(strEffectInput, atype='ecat')

        elif save == 2:
            selectedCause = ''
            if strCauseInput:
                listCauseOptions = storeAnnotationClasses(strCauseInput, atype='ccat')
        
        return listEffectOptions, selectedEffect, listCauseOptions, selectedCause


    @app.callback(
        [Output('div-effect-subcategory', 'style'),
         Output('div-add-effect-subcategory', 'style'),
         Output('div-samples-effect', 'style'),
         Output('div-cause-subcategory', 'style'),
         Output('div-add-cause-subcategory', 'style'),
         Output('div-samples-cause', 'style'),
         Output('btn-workspace-reset', 'disabled')],
        [Input('dropdown-effect-category-selector', 'value'),
         Input('dropdown-cause-category-selector', 'value'),
         Input('btn-workspace-reset', 'n_clicks'),
         Input('alert-saved', 'is_open')],
        [State('div-effect-subcategory', 'style'),
         State('div-cause-subcategory', 'style')]
    )
    def showSubClasses(listSelectedEffects, listSelectedCauses, _, saveSuccess,
        dictSubeffectVisible, dictSubcauseVisible):
        # reset
        dictSubeffectVisible = {"visibility": "hidden"}
        dictSubcauseVisible = {"visibility": "hidden"}
        boolResetBtnDisabled = True

        # check if saving process or reset fired
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
        else:
            prop_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if "alert-saved" in prop_id:
                if saveSuccess:
                    dictSubeffectVisible = dictSubcauseVisible = {"visibility": "hidden"}
                    boolResetBtnDisabled = True
                else:
                    # failed 
                    raise PreventUpdate
            else:
                if listSelectedEffects:
                    dictSubeffectVisible = {"visibility": "visible"}
                    boolResetBtnDisabled = False
                if listSelectedCauses:
                    dictSubcauseVisible = {"visibility": "visible"}
                    boolResetBtnDisabled = False

        return dictSubeffectVisible, dictSubeffectVisible, \
            dictSubeffectVisible, dictSubcauseVisible,\
            dictSubcauseVisible, dictSubcauseVisible,\
            boolResetBtnDisabled


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
         Output('listgroup-similar-cause-samples', 'children'),
         Output('store-similar-effect-samples', 'data'),
         Output('store-similar-cause-samples', 'data')],
        [Input('dropdown-effect-category-selector', 'value'),
         Input('dropdown-cause-category-selector', 'value')],
        [State('store-similar-effect-samples', 'data'),
         State('store-similar-cause-samples', 'data'),
         State('listgroup-similar-effect-samples', 'children'),
         State('listgroup-similar-cause-samples', 'children')],
    )
    def getSimilarSampleItems(selectedEffect, selectedCause,
            effectSamplesStore, causeSamplesStore,
            listSamplesEffect, listSamplesCause):
        if selectedEffect:
            if selectedEffect not in effectSamplesStore['class']:
                # new selected effect
                # sample from data
                effectSamplesStore = querySimilarSamples(selectedEffect)
                # create item
                listSamplesEffect = spawnSimilarSamples(effectSamplesStore, atype='effect')

        # same but independently for cause
        if selectedCause:
            if selectedEffect not in causeSamplesStore['class']:
                causeSamplesStore = querySimilarSamples(selectedCause)
                listSamplesCause = spawnSimilarSamples(causeSamplesStore, atype='cause')

        return listSamplesEffect, listSamplesCause, effectSamplesStore, causeSamplesStore


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
            listAvailableDataConnectors.append(spawnDataConnector(f"EQ: {m['eq']}\n"+f"{m['desc']}", idx=idx))

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