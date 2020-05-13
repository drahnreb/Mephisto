import dash
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from datetime import datetime as dt
import re

from dash.exceptions import PreventUpdate
from utils import createFigTemplate, queryTensorData, getUploadPath, queryPictureData, queryAnnotationClasses, storeAnnotationClasses, fa, querySimilarSamples, updatePic, updateScatter, updateScatter3d
from layout import spawnGraph, spawnSimilarSamples, spawnDataConnector
import numpy as np

import time

def register_callbacks(app):
    @app.callback(
        [Output('div-graphSpace', 'children'),
         Output('btn-workspace-save', 'disabled')],
        [Input('btn-create-graph', 'n_clicks'),
         Input({'type': 'btn-remove-graph', 'index': ALL}, 'n_clicks_timestamp')],
        [State('div-graphSpace', 'children'),
         State('dropdown-newGraph-coupling-idx', 'value'),
         State('div-newGraph-coupling-gtype', 'children'),
         State('store-data-connectors', 'data')])
    def createRemoveGraph(btnCreateGraph, _btnsRemoveGraph, listGraphSpaceChildren, idxConnector, gtype, dictMetainfo):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
        else:
            prop_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            if "btn-remove-graph" in prop_id:
                idx = eval(prop_id).get('index')
                if idx:
                    print('delete graph unsupported', len(listGraphSpaceChildren))
                    raise PreventUpdate
                    # TODO: fix correct index
                    del listGraphSpaceChildren[idx]
                    # shift prop intGraphIdx
                    listGraphSpaceChildren = treewalkShiftPropIdx(listGraphSpaceChildren)
                    raise PreventUpdate
                else:
                    raise PreventUpdate

            else:
                #create graph

                # general meta information
                intGraphIdx = len(listGraphSpaceChildren)
                listDictAllFeatures = dictMetainfo[idxConnector].get('schema') # pictures: [{'label': path.name, 'value': path}
                strEQ = dictMetainfo[idxConnector].get('eq')
                strType = dictMetainfo[idxConnector].get('dataType') #pictures

                if 'picture' in gtype:
                    kind = 'picture'
                    listPicturePaths = queryPictureData()
                    # last modiefied dates
                    # earliest last modified data
                    mtimes = [os.path.getmtime(file) for file in listPicturePaths]
                    dtMinDate = min(mtimes)
                    dtMaxDate = max(mtimes)
                    listDictAllFeatures = [{'label': path.name, 'value': path} for path in listPicturePaths]
                    intTotSamples = len(listPicturePaths)

                else:
                    tensorIndex = queryTensorData(idxConnector, None)
                    if not len(tensorIndex):
                        raise PreventUpdate

                    intTotSamples = tensorIndex.shape[0]
                    dtMinDate = min(tensorIndex)
                    dtMaxDate = max(tensorIndex)

                    if 'tensor-3D' in gtype:
                        kind = 'scatter3d'
                    else:
                        kind = 'scatter'

                newGraph = spawnGraph(
                    intGraphIdx,
                    kind=kind, 
                    listDictAllFeatures=listDictAllFeatures,
                    strEQ=strEQ,
                    strType=strType,
                    intTotSamples=intTotSamples,
                    dtMinDate=dtMinDate,
                    dtMaxDate=dtMaxDate
                )
                listGraphSpaceChildren.insert(0, newGraph)

            if len(listGraphSpaceChildren): #TODO: this should be -1
                boolSaveBtnDisabled = False
            else:
                boolSaveBtnDisabled = True
                
            return listGraphSpaceChildren, boolSaveBtnDisabled


    @app.callback(
         Output('store-data-connectors', 'data'),
        [Input({'type': 'dialog-connector-save-attributes', 'ctype': ALL}, 'n_clicks'),
         Input('upload-data', 'fileNames')],
        [State({'type': 'dialog-connector-attributes', 'ctype': ALL}, 'is_open'),
         State({'type': 'dialog-connector-gtype', 'ctype': ALL}, 'value'),
         State({'type': 'dialog-connector-schema', 'ctype': ALL}, 'value'),
         State({'type': 'dialog-connector-eq', 'ctype': ALL}, 'value'),
         State({'type': 'dialog-connector-dataType', 'ctype': ALL}, 'value'),
         State({'type': 'dialog-connector-source', 'ctype': ALL}, 'value'),
         State('store-data-connectors', 'data')]
    )
    def createConnectorMetainfo(_btnSaveAttributes, _uploader, dialogIsOpen, gtype, schema, eq, dataType, source, dictMetainfo):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate

        else:
            prop_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            if "upload-data" in prop_id:
                fileNames = eval(prop_id).get('fileNames')
                if len(fileNames):
                    fileNames = set(fileNames)
                    maxIdx = max(set(dictMetainfo), default=0)
                    dictMetainfo[maxIdx]['source'] = [str(getUploadPath() / fn) for fn in fileNames]

            else:
                if not dialogIsOpen: #and not any(btnSaveAttributes)
                    raise PreventUpdate

                else:
                    newSessionIdx = int(max(dictMetainfo.keys(), default=0)) + 1

                    # get via Input Fields
                    gtype = "tensor" # 'picture'
                    schema = [
                                # based on meta information derived from schema / dataframe header
                                {"label": "Antriebsmomenten-Sollwert einer Achse/Spindel an X2",
                                 "value": "aaTorque_X2"},
                                {"label": "Antriebsauslastung einer Achse/Spindel an X2",
                                 "value": "aaLoad_X2"},
                                {"label": "Antriebsstrom-Istwert einer Achse/Spindel an X2",
                                 "value": "aaCurr_X2"},
                                {"label": "Antriebswirkleistung einer Achse/Spindel an X2",
                                 "value": "aaPower_X2"},
                            ] # pictures: [{'label': path.name, 'value': path}
                    eq = "404000500065"
                    source="", # str(getUploadPath() / fn) for n, fn in enumerate(fileNames)
                    dataType = "NC"#'pictures'

                    attr = dict(
                            gtype=gtype,
                            eq=eq,
                            dataType=dataType,
                            source=source,
                            schema=schema
                        )

                    dictMetainfo[newSessionIdx] = attr

        return dictMetainfo


    @app.callback(
         [Output({'type': 'dialog-connector-attributes', 'ctype': 'upload-connector'}, 'is_open'), #
         Output({'type': 'dialog-connector-attributes', 'ctype': 'local-db-connector'}, 'is_open'),
         Output({'type': 'dialog-connector-attributes', 'ctype': 'cloud-blob-connector'}, 'is_open'),
         Output({'type': 'dialog-connector-attributes', 'ctype': 'cloud-stream-connector'}, 'is_open')],
        [Input({'type': 'btn-upload-connector'}, 'n_clicks_timestamp'),
         Input({'type': 'btn-local-db-connector'}, 'n_clicks_timestamp'),
         Input({'type': 'btn-cloud-blob-connector'}, 'n_clicks_timestamp'),
         Input({'type': 'btn-cloud-stream-connector'}, 'n_clicks_timestamp'),
         Input({'type': "dialog-connector-cancel", 'ctype': 'upload-connector'}, "n_clicks_timestamp"),
         Input({'type': "dialog-connector-cancel", 'ctype': 'local-db-connector'}, "n_clicks_timestamp"),
         Input({'type': "dialog-connector-cancel", 'ctype': 'cloud-blob-connector'}, "n_clicks_timestamp"),
         Input({'type': "dialog-connector-cancel", 'ctype': 'cloud-stream-connector'}, "n_clicks_timestamp"),
         Input('div-graphSpace', 'children')]
    )
    def showDialogConnectionAttributes(_btnUploadConnector, _btnDBConnector, _btnBlobConnector, _btnStreamConnector,
            _dialogDismissUpload, _dialogDismissDB, _dialogDismissBlob, _dialogDismissStream, listGraphSpaceChildren):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate

        closeAllDialogs = np.array([False, False, False, False])
        prop_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if not "div-graphSpace" in prop_id: # close dialog after creation
            componentType = eval(ctx.triggered[0]['prop_id'].split('.')[0])['type']

            if not 'dialog-connector-cancel' in componentType:
                openDialog = np.argmax([_btnUploadConnector, _btnDBConnector, _btnBlobConnector, _btnStreamConnector])
                closeAllDialogs[openDialog] = True

        return closeAllDialogs.tolist()


    @app.callback(
         Output('btn-create-graph', 'disabled'),
        [Input('dropdown-newGraph-coupling-idx', 'value')],
        [State('store-data-connectors', 'data')]
    )
    def checkGraphCoupling(idxConnector, dictMetainfo):
        disabled = True
        if idxConnector:
            if idxConnector in dictMetainfo.keys():
                disabled = False
        return disabled


    @app.callback(
        [Output({'type': 'dialog-connector-save-attributes', 'ctype': MATCH}, 'disabled'),
         Output({'type': 'dialog-connector-eq', 'ctype': MATCH}, 'valid')],
        [Input({'type': 'dialog-connector-gtype', 'ctype': MATCH}, 'value'),
         Input({'type': 'dialog-connector-schema', 'ctype': MATCH}, 'value'),
         Input({'type': 'dialog-connector-eq', 'ctype': MATCH}, 'value'),
         Input({'type': 'dialog-connector-dataType', 'ctype': MATCH}, 'value'),
         Input({'type': 'dialog-connector-source', 'ctype': MATCH}, 'value'),
         Input({'type': 'dialog-connector-host', 'ctype': MATCH}, 'value'),
         Input({'type': 'dialog-connector-port', 'ctype': MATCH}, 'value'),
         Input({'type': 'dialog-connector-user', 'ctype': MATCH}, 'value'),
         Input({'type': 'dialog-connector-pw', 'ctype': MATCH}, 'value'),
         Input({'type': 'dialog-connector-host', 'ctype': MATCH}, 'valid')
         ]
    )
    def checkConnectorAttributes(gtype, schema, eq, dataType, source, host, port, user, password, validHost
        ):
        disabled = True
        valid = False

        if eq:
            valid = True
        if gtype and eq and dataType:
            ctx = dash.callback_context
            if ctx.triggered:
                componentType = eval(ctx.triggered[0]['prop_id'].split('.')[0])['ctype']
                if "local-db-connector" in componentType and not (host and port and validHost): #
                    disabled = True
                else:
                    disabled = False

        return disabled, valid


    @app.callback(
        [Output('dropdown-newGraph-coupling-idx', 'options'),
         Output('div-newGraph-coupling-gtype', 'children'),
         Output('dialog-newGraph-coupling', 'is_open')],
        [Input('btn-add-graph-2D', 'n_clicks_timestamp'),
         Input('btn-add-graph-3D', 'n_clicks_timestamp'),
         Input('btn-add-graph-pic', 'n_clicks_timestamp'),
         Input('btn-dimsiss-dialog-newGraph-coupling', 'n_clicks'),
         Input('div-graphSpace', 'children')],
        [State('store-data-connectors', 'data')])
    def openDialogDataGraphConnection(add2D, add3D, addPic, dismissDialogConnection, listGraphSpaceChildren, dictMetainfo):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
        else:
            prop_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if not dictMetainfo or 'btn-dimsiss-dialog-newGraph-coupling' in prop_id or 'div-graphSpace' in prop_id:
                # close dialog after creation
                # no data connector available
                return [], '', False

            else:
                openDialog = True

                if 'btn-add-graph-pic' in prop_id:
                    gtype = 'picture'
                elif 'btn-add-graph-2D' in prop_id:
                    gtype = 'tensor-2D'
                elif 'btn-add-graph-3D' in prop_id:
                    gtype = 'tensor-3D'

                options = []
                for key, dictValues in dictMetainfo.items():
                    if gtype[:-3] in dictValues['gtype']:
                        options.append({'label': str(key)+str(dictValues['eq'])+str(dictValues['dataType']), 'value': key})

                if not len(options):
                    # {"label": "No Data Connector available", "value": None}
                    return [], '', True

                return options, gtype, openDialog


    @app.callback(
         Output({'type': 'graph', 'index': MATCH}, 'figure'),
        [Input({'type': 'dropdown-select-feature-Y', 'index': MATCH}, 'value'),
         Input({'type': 'dropdown-select-feature-Z', 'index': MATCH}, 'value'),
         Input({'type': 'dropdown-select-picture', 'index': MATCH}, 'value'),
         Input({'type': 'input-select-sample-n', 'index': MATCH}, 'value'),
         Input({'type': 'datepicker-select-sample-range', 'index': MATCH}, 'start_date'),
         Input({'type': 'datepicker-select-sample-range', 'index': MATCH}, 'end_date'),
         Input({'type': 'input-select-sample-time', 'index': MATCH}, 'value'),
         Input({'type': 'radio-select-sample-draw', 'index': MATCH}, 'value'),
         Input({'type': 'btn-reload-graph', 'index': MATCH}, 'n_clicks_timestamp')],
        [State({'type': 'dropdown-select-feature-Y', 'index': MATCH}, 'placeholder'),
         State({'type': 'dropdown-select-feature-Z', 'index': MATCH}, 'placeholder'),
         State({'type': 'dropdown-select-picture', 'index': MATCH}, 'placeholder')]
    )
    def changeGraph(strSelectedValuesY, strSelectedValuesZ, strSelectedValuesPic,
            nSamples, start_date, end_date, start_time, samplingMethod, btnReloadGraph,
            shadowY, shadowZ, shadowPic):
        if nSamples is None:
            raise PreventUpdate
        if nSamples < 1:
            raise PreventUpdate
        else:
            ctx = dash.callback_context
            if not ctx.triggered:
                raise PreventUpdate
            else:
                prop_id = ctx.triggered[0]['prop_id'].split('.')[0]
                if 'btn-reload-graph' in prop_id:
                    # TODO: new sampling
                    pass

            # also in store
            start_date = dt.strptime(re.split('T| ', start_date)[0], '%Y-%m-%d')
            if end_date:
                end_date = dt.strptime(re.split('T| ', end_date)[0], '%Y-%m-%d')

            if 'Shadowing' in shadowY:
                if not strSelectedValuesPic:
                    raise PreventUpdate
                # picture
                fig = updatePic(pic=strSelectedValuesPic,
                        start_date=start_date, end_date=end_date,
                        start_time=start_time, method=samplingMethod, n=nSamples)
                return fig

            elif 'Shadowing' in shadowZ:
                if not strSelectedValuesY:
                    raise PreventUpdate
                # scatter
                fig = updateScatter(dimsY=strSelectedValuesY,
                        start_date=start_date, end_date=end_date,
                        start_time=start_time, method=samplingMethod, n=nSamples)
                return fig

            else:
                if not strSelectedValuesY and not trSelectedValuesZ:
                    raise PreventUpdate
                # scatter3d
                fig = updateScatter3d(dimsY=strSelectedValuesY, dimsZ=strSelectedValuesZ,
                        start_date=start_date, end_date=end_date,
                        start_time=start_time, method=samplingMethod, n=nSamples)
                return fig
            # strLabel = [dictOption['label'] for dictOption in listDictAllFeatures if strSelectedValuesY in dictOption['value']][0]
            # config['toImageButtonOptions'] = {
            #     'format': 'png',
            #     'filename': f"{strSelectedValuesY}-{strLabel}_Mephisto.png",
            # }


    @app.callback(
        [Output('loading-workspace-save', 'children'),
         Output('alert-saved', 'is_open'),
         Output('tab-report-data', 'disabled')],
        [Input('btn-workspace-save', 'n_clicks')],
        [State('btn-tools-linker', 'active'),
         State('tab-report-data', 'disabled')
        #[State({'type': 'graph', 'index': MATCH}, 'clickData'), #Data from latest click event.
        # State({'type': 'graph', 'index': MATCH}, 'clickAnnotationData'), #Data from latest click annotation event.
        # State({'type': 'graph', 'index': MATCH}, 'selectedData') #Data from latest select event.
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
         Output('tab-data-connectors', 'label'),
         Output('tab-data-connectors', 'disabled')],
        [Input('store-data-connectors', 'modified_timestamp')],
        [State('div-data-connectors', 'children'),
         State('tab-data-connectors', 'disabled'),
         State('store-data-connectors', 'data')]
    )
    def spawnData(newConnector, listAvailableDataConnectors, disabled, dictMetainfo):
        if not dictMetainfo or not newConnector:
            raise PreventUpdate

        availIdx = [comp for comp in listAvailableDataConnectors] #['id']['index']
        for k, m in dictMetainfo.items():
            # if m not in availIdx:
            listAvailableDataConnectors.append(
                spawnDataConnector(f"{k}:\n  EQ: {m['eq']}\n"+f"{m['dataType']}", idx=k)
            )

        nConnectors = len(listAvailableDataConnectors)

        if nConnectors:
            disabled = False
        else:
            disabled = True

        return listAvailableDataConnectors, f"Data Connectors: {nConnectors}", disabled


#anything uploading??
#                        "", color="light", id="badge-connector"),
                    # color: primary==uploading, success==allready, danger==error


# click on similar samples to plot in another plot