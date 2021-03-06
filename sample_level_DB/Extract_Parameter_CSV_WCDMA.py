#!/usr/bin/python

import os
import sys
# import matplotlib.pyplot as plt
import itertools
import re
import datetime
# import pandas as pd
import collections
from collections import Counter
import sqlite3
import time, csv

globalFileNames = {}
Eventsbool = {'event: e1f': 0, 'event: e1d': 0, 'event: e1e': 0, 'event: e1b': 0, 'event: e1c': 0, 
'event: e1a': 0, 'event: e1j': 0, 'event: 2b': 0, 'event: 2d': 0, 'event: 2f': 0}


try:
    filelist = [ f for f in os.listdir('Data_Out/') if f.endswith(".csv") ]
    for f in filelist:
        os.remove(os.path.join(mydir, f))
except Exception as e:
    pass
def processSibs(primKey,secKey,line):
    try:
        if line not in dictCell[primKey][secKey]:
            dictCell[primKey][secKey][line] = 1
        else:
            dictCell[primKey][secKey][line] += 1

        if secKey == "lte_measurement_report_config" or secKey == "lte_measurement_object" \
        or secKey == "utra_3g_measurement_object":
            if line not in table[secKey]:
                table[secKey][line] = 1
            else: 
                table[secKey][line] += 1

        elif secKey == "lte_report_configuration" or secKey == "2g3g_report_reconfiguration":
            # print line
            reportConfig = eval(line)
            currReportId = int(reportConfig['report_id'])
            objType = str()

            if secKey == "2g3g_report_reconfiguration":
                objType = "utra_3g_measurement_object"
            elif secKey == "lte_report_configuration":
                objType = "lte_measurement_object"

            flag = 0
            for each in table["lte_measurement_report_config"]:
                measReport = eval(each)
                if currReportId == measReport["reportConfigId"]:
                    objVal = measReport["measObjectId"]
                    for eachObj in table[objType]:
                        currObj = eval(eachObj)
                        if objVal == int(currObj['measobj_id']):
                            reportConfig['freq'] = currObj['freq']
                            flag = 1
                            break
            if flag == 0:
                reportConfig['freq'] = -1

            currEventList = reportConfig.pop('event_list')
            if currEventList != []:
                currEventDict = currEventList[0]
                for eachKey in currEventDict:
                    reportConfig[eachKey] = currEventDict[eachKey]
                secKey = 'lte_'+reportConfig['event_type']
                # print primKey, secKey
                
                if secKey.startswith('lte_'):
                    global Events
                    Events =  copyVals(Events,reportConfig)
                    writeDB(Events,globalFileNames['Events'])

                    # print Events
                    # sys.exit()

                line = str(reportConfig)
                if line not in dictCell[primKey][secKey]:
                    dictCell[primKey][secKey][line] = 1
                else:
                    dictCell[primKey][secKey][line] += 1

        if secKey[1:5]=='sib3':
            global ServCell
            ServCell =  copyVals(ServCell,eval(line))
            # print ServCell
            # sys.exit()
        elif secKey[1:5]=='sib5':
            global SIB5
            SIB5 =  copyVals(SIB5,eval(line))
            writeDB(SIB5,globalFileNames['SIB5'])
            # print SIB5
            # sys.exit()
        elif secKey[1:5]=='sib6':
            global SIB6
            SIB6 =  copyVals(SIB6,eval(line))
            writeDB(SIB6,globalFileNames['SIB6'])

            # print SIB6
            # sys.exit()
        elif secKey[1:5]=='sib8':
            global SIB8
            SIB8 =  copyVals(SIB8,eval(line))
            writeDB(SIB8,globalFileNames['SIB8'])

            # print SIB8
            # sys.exit()

        # elif secKey=='2g3g_report_reconfiguration' or secKey=="lte_report_configuration":
        # elif secKey.startswith('lte_'):
        #     global Events
        #     Events =  copyVals(Events,eventInfo)
        #     print Events
        #     sys.exit()

    except Exception as e:
        pass
        # print e


def process3g(primKey,secKey,line):

    # tupleDict = str(dict3gCell.items())
    try:
        if line not in dict3gCell[primKey][secKey]:
            dict3gCell[primKey][secKey][line] = 1
        else:
            dict3gCell[primKey][secKey][line] += 1

        global utra_ServingCell
        global cellSelectReselectInfo
        global EUTRA_FrequencyAndPriorityInfo
        global interRATCell
        global intraFreqCell
        global interFreqCell
        global threeg_rrc_cerv_cell_info
        global Events3g


        if secKey=='utra_ServingCell':
            # global utra_ServingCell
            utra_ServingCell =  copyVals(utra_ServingCell,eval(line))
            # print ServCell
            # sys.exit()
        elif secKey=='cellSelectReselectInfo':
            # global cellSelectReselectInfo
            cellSelectReselectInfo =  copyVals(cellSelectReselectInfo,eval(line))
            # writeDB(SIB5,globalFileNames['SIB5'])
            # print SIB5
            # sys.exit()
        elif secKey=='3g_rrc_cerv_cell_info':
            # global threeg_rrc_cerv_cell_info
            threeg_rrc_cerv_cell_info =  copyVals(threeg_rrc_cerv_cell_info,eval(line))

            utra_ServingCell =  copyVals(utra_ServingCell,eval(line))
            cellSelectReselectInfo =  copyVals(cellSelectReselectInfo,eval(line))
            threeg_rrc_cerv_cell_info =  copyVals(threeg_rrc_cerv_cell_info,eval(line))
            interRATCell =  copyVals(interRATCell,eval(line))
            interFreqCell =  copyVals(interFreqCell,eval(line))
            intraFreqCell =  copyVals(intraFreqCell,eval(line))
            EUTRA_FrequencyAndPriorityInfo =  copyVals(EUTRA_FrequencyAndPriorityInfo,eval(line))
            # writeDB(SIB6,globalFileNames['SIB6'])

            # print SIB6
            # sys.exit()
        elif secKey=='interRATCell':
            # global interRATCell
            interRATCell =  copyVals(interRATCell,eval(line))
            # writeDB(SIB8,globalFileNames['SIB8'])
        elif secKey=='interFreqCell':
            # global interFreqCell
            interFreqCell =  copyVals(interFreqCell,eval(line))
            # writeDB(SIB8,globalFileNames['SIB8'])
        elif secKey=='intraFreqCell':
            # global intraFreqCell
            intraFreqCell =  copyVals(intraFreqCell,eval(line))
            # writeDB(SIB8,globalFileNames['SIB8'])
        elif secKey == 'EUTRA_FrequencyAndPriorityInfo':
            EUTRA_FrequencyAndPriorityInfo = copyVals(EUTRA_FrequencyAndPriorityInfo,eval(line))
        elif 'event' in secKey:
            Events3g[secKey] = eval(line)
            # print Events3g
            # sys.exit()


    except Exception as e:
        pass
        print line
        # print
    
def Flush():
    global ServCell
    global SIB5
    global SIB6
    global SIB8
    global Events
    global Events3g
    # global Eventsbool
    global utra_ServingCell
    global cellSelectReselectInfo
    global EUTRA_FrequencyAndPriorityInfo
    global interRATCell
    global intraFreqCell
    global interFreqCell
    global threeg_rrc_cerv_cell_info


    utra_ServingCell = {'PLMN': None, 'timestamp': None,'Cell ID': None,'LAC ID': None,'priority': None, 
    'threshServingLow': None, 's_PrioritySearch2': None, 's_PrioritySearch1': None}

    EUTRA_FrequencyAndPriorityInfo = {'PLMN': None, 'timestamp': None,'Cell ID': None,'LAC ID': None,'priority': None,
    'priority': None, 'threshXlow': None, 'earfcn': None, 'threshXhigh': None, 'qRxLevMinEUTRA': None}

    Events3g = {'event: e1f': {}, 'event: e1d': {}, 'event: e1e': {}, 'event: e1b': {}, 'event: e1c': {}, 
    'event: e1a': {}, 'event: e1j': {}, 'event: 2b': {}, 'event: 2d': {}, 'event: 2f': {}}

    cellSelectReselectInfo = {'PLMN': None, 'timestamp': None,'Cell ID': None,'LAC ID': None, 
    't_Reselection_S': None, 'rrc.rat_Identifier': None, 's_Intersearch': None, 
    'q_HYST_2_S': None, 'rrc.s_HCS_RAT': None, 'rrc.s_Limit_SearchRAT': None, 'q_Hyst_1_S': None, 
    'maxAllowedUL_Tx_Power': None, 's_Intrasearch': None, 'rrc.s_SearchRAT': None, 's_SearchHCS': None, 
    'q_RxlevMin': None, 'q_QualMin': None}

    threeg_rrc_cerv_cell_info = {'city': None, 'PLMN': None, 'timestamp': None, 'UtraDLFreq': None, 
    'LAC ID': None, 'lon': None, 'state': None, 'Cell ID': None, 'country': None, 'lat': None, 'RAC ID': None}

    interFreqCell = {'PLMN': None, 'timestamp': None,'Cell ID': None,'LAC ID': None, 
    'rrc.uarfcn_DL': None, 'rrc.q_Offset2S_N': None, 'rrc.q_Offset1S_N': None, 
    'rrc.maxAllowedUL_TX_Power': None, 'rrc.modeSpecificInfo': None, 'rrc.q_RxlevMin': None, 
    'rrc.primaryScramblingCode': None, 'rrc.q_QualMin': None, 'rrc.cellSelectQualityMeasure': None}

    interRATCell = {'PLMN': None, 'timestamp': None,'Cell ID': None,'LAC ID': None, 
    'rrc.bcc': None, 'rrc.q_Offset2S_N': None, 'rrc.q_Offset1S_N': None, 
    'rrc.maxAllowedUL_TX_Power': None, 'rrc.bcch_ARFCN': None, 'rrc.modeSpecificInfo': None, 
    'rrc.q_RxlevMin': None, 'rrc.frequency_band': None, 'rrc.ncc': None, 'rrc.q_QualMin': None, 
    'rrc.cellSelectQualityMeasure': None}

    intraFreqCell = {'PLMN': None, 'timestamp': None,'Cell ID': None,'LAC ID': None, 
    'rrc.q_Offset2S_N': None, 'rrc.q_Offset1S_N': None, 'rrc.maxAllowedUL_TX_Power': None, 
    'rrc.modeSpecificInfo': None, 'rrc.q_RxlevMin': None, 'rrc.primaryScramblingCode': None, 
    'rrc.q_QualMin': None, 'rrc.cellSelectQualityMeasure': None}

    ServCell = {'Uplink bandwidth': 'Null', 'city': 'Null', 'Band Indicator': 'Null', 'timestamp': 'Null',
     'MCC': 'Null', 'lon': 'Null', 'country': 'Null', 'state': 'Null', 'Downlink bandwidth': 'Null', 
     'Cell Identity': 'Null', 'lat': 'Null', 'Uplink frequency': 'Null', 'Downlink frequency': 'Null', 
     'MNC': 'Null', 'TAC': 'Null','Allowed Access': 'Null','q_Hyst':'Null','threshServingLow': 'Null', 
     'cellReselectionPriority': 'Null', 's_NonIntraSearch': 'Null', 't_ReselectionEUTRA': 'Null', 
     's_IntraSearch': 'Null', 'p_Max': 'Null', 'q_RxLevMin': 'Null','Cell ID': 'Null'}

    SIB5 = {'Cell Identity': 'Null','MNC': 'Null','MCC': 'Null','TAC': 'Null','timestamp': 'Null', 
    'threshX_High': 'Null', 'threshX_Low': 'Null', 'q_RxLevMin': 'Null', 
    'dl_CarrierFreq': 'Null', 't_ReselectionEUTRA': 'Null', 'cellReselectionPriority': 'Null', 
    'p_Max': 'Null', 'allowedMeasBandwidth': 'Null'}

    SIB6 = {'Cell Identity': 'Null','MNC': 'Null','MCC': 'Null','TAC': 'Null','timestamp': 'Null',
    'p_MaxUTRA': 'Null', 'carrierFreq': 'Null', 'threshX_High': 'Null', 'q_RxLevMin': 'Null', 
    'lte_rrc_freq': 'Null', 'q_QualMin': 'Null', 'cellReselectionPriority': 'Null', 'threshX_Low': 'Null'}

    SIB8 = {'Cell Identity': 'Null','MNC': 'Null','MCC': 'Null','TAC': 'Null','timestamp': 'Null',
    'bandClass': 'Null', 'cellReselectionPriority': 'Null', 'threshX_High': 'Null', 'threshX_Low': 'Null'}

    Events = {'Cell Identity': 'Null','MNC': 'Null','MCC': 'Null','TAC': 'Null','timestamp': 'Null', 'offset': 'Null',
    'hyst': 'Null', 'event_type': 'Null', 'threshold1': 'Null', 'threshold2': 'Null', 'freq': 'Null', 
    'report_id': 'Null','threshold': 'Null'}

def copyVals(To,From):
    for eachKey in From:
        if eachKey in To:
            To[eachKey] = From[eachKey]
    return To
    # return {k: From[k] for k in To if k in From}

def writeDB(mydict, fileName):
    try:
        fileName.write("|".join(map(lambda x:str(x),mydict.values())))
        fileName.write('\n')
    except:
        pass
    # with open(fileName, 'ab') as csv_file:
    #     writer = csv.writer(csv_file, delimiter=',')
    #     writer.writerow(mydict.values())
        # for key, value in mydict.items():
def tryint(s):
    try:
        return int(s)
    except:
        return s

def alphanum_key(s):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    return [ tryint(c) for c in re.split('([0-9]+)', s) ]

def sort_nicely(l):
    """ Sort the given list in the way that humans expect.
    """
    l.sort(key=alphanum_key)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: python parseConfigDist.py [/Folder_with_log_output]"
        exit()

    resultFile = []
    for root, dirs, files in os.walk(sys.argv[1]):
        for f in files:
            resultFile.append(os.path.join(root, f))
            
    # resultFile = ['Data_In/mi2log_D1.txt']
    Flush()
    print resultFile
    for filename in resultFile:
        # globalFileNames = {'ServCell':'Data_Out/ServCell.csv','SIB5':'Data_Out/SIB5.csv',
        # 'SIB6':'Data_Out/SIB6.csv','SIB8':'Data_Out/SIB8.csv','Events':'Data_Out/Events.csv'}
        foo = filename.split('.')[0]
        foo = 'Data_Out/'+foo.split('/')[1]
        globalFileNames = {'utra_ServingCell':open(foo+'utra_ServingCell.csv','a+'),
        'threeg_rrc_cerv_cell_info':open(foo+'threeg_rrc_cerv_cell_info.csv','a+'),
        'cellSelectReselectInfo':open(foo+'cellSelectReselectInfo.csv','a+'),
        'interRATCell':open(foo+'interRATCell.csv','a+'),
        'intraFreqCell':open(foo+'intraFreqCell.csv','a+'),
        'interFreqCell':open(foo+'interFreqCell.csv','a+'),
        'EUTRA_FrequencyAndPriorityInfo':open(foo+'EUTRA_FrequencyAndPriorityInfo.csv','a+')}
        for each in Events3g:
            globalFileNames[each] = open(foo+each+'.csv','a+')
        globalFileNames['utra_ServingCell'].write(",".join(utra_ServingCell.keys())+'\n')
        globalFileNames['threeg_rrc_cerv_cell_info'].write(",".join(threeg_rrc_cerv_cell_info.keys())+'\n')
        globalFileNames['cellSelectReselectInfo'].write(",".join(cellSelectReselectInfo.keys())+'\n')
        globalFileNames['interRATCell'].write(",".join(interRATCell.keys())+'\n')
        globalFileNames['intraFreqCell'].write(",".join(intraFreqCell.keys())+'\n')
        globalFileNames['EUTRA_FrequencyAndPriorityInfo'].write(",".join(EUTRA_FrequencyAndPriorityInfo.keys())+'\n')
        globalFileNames['interFreqCell'].write(",".join(interFreqCell.keys())+'\n')
        currentMsgType = None
        currentRAT = None
        # Out


        dictLteConfig = {"lte_rrc_cerv_cell_info":{},\
                "lte_rrc_measurement_report":{},\
                "[sib3]cellReselectionInfoCommon_element":{},\
                "[sib3]cellReselectionServingFreqInfo_element":{},\
                "[sib3]intraFreqCellReselectionInfo_element":{},\
                "[sib4]intraFreqBlackCellList":{},\
                "[sib5]InterFreqCarrierFreqInfo_element":{},\
                "[sib5]interFreqBlackCellList":{},\
                "[sib6]CarrierFreqUTRA_FDD_element":{},\
                "[sib8]":{},\
                "lte_measurement_object":{},\
                "utra_3g_measurement_object":{},\
                "lte_report_configuration":{},\
                "2g3g_report_reconfiguration":{},\
                "lte_measurement_report_config":{},\
                "lte_a1":{},\
                "lte_a2":{},\
                "lte_a3":{},\
                "lte_a4":{},\
                "lte_a5":{},\
                "lte_b1":{},\
                "lte_b2":{},\
                "lte_interRAT_b1":{},\
                "lte_interRAT_b2":{},\

                }

        dictWcdmaConfig = {"utra_ServingCell":{},\
                "cellSelectReselectInfo":{},\
                "EUTRA_FrequencyAndPriorityInfo":{},\
                "event: e1a":{},\
                "event: e1b":{},\
                "event: e1c":{},\
                "event: e1d":{},\
                "event: 2b":{},\
                "event: 2d":{},\
                "event: 2f":{},\
                "3g_rrc_cerv_cell_info":{},\
                "event: e1j":{},\
                "event: e1f":{},\
                "event: e1e":{},\
                "interFreqCell":{},\
                "interRATCell":{},\
                "intraFreqCell":{}
                }
       
        # ServCell, SIB5, SIB6, SIB8, Events = {},{},{},{},{}
        dictCell, foundPair, foundCervCell, primKey = {}, False, False, ()
        dict3gCell, found3gPair, prim3gKey = {}, False, ()
        measReport, measObj, reportConfig, table = {}, {}, {}, {}
        counter = 0
        print filename
        f = open(filename)
        for line in f:
            # print line
            line = line.rstrip()
            matchObj1 = re.match(r'\(\d*, \d*, \d*\)', line, re.M|re.I)
            matchObj2 = re.match(r'\(\d*, \d*\)', line, re.M|re.I)
            if matchObj1 or matchObj2:
                cellID = 0
                if matchObj2:
                    cellID, down3gFreq = eval(matchObj2.group(0))
                if cellID > 503:
                    found3gPair = True
                    prim3gKey = (cellID,down3gFreq)
                    if prim3gKey not in dict3gCell:
                        dict3gCell[prim3gKey] = {k:{} for k in dictWcdmaConfig}
                else:
                    foundPair = True
                    primKey = () # find the next pair
                    prim3gKey = ()
                    # print table
                    table = {"lte_measurement_report_config":{},"lte_measurement_object":{},"utra_3g_measurement_object":{}}
                    # if len(set(ServCell.values()))>1:
                    #     writeDB(ServCell,globalFileNames['ServCell'])

                    # Flush()
                    dictCell = {}
                continue

            if line == "-----------------------------------------------------------" or line == "{}" or line[:11] == "(MI)Unknown":
                if prim3gKey != ():
                    writeDB(utra_ServingCell,globalFileNames['utra_ServingCell']) 
                    writeDB(cellSelectReselectInfo,globalFileNames['cellSelectReselectInfo']) 
                    writeDB(threeg_rrc_cerv_cell_info,globalFileNames['threeg_rrc_cerv_cell_info']) 
                    writeDB(intraFreqCell,globalFileNames['intraFreqCell']) 
                    writeDB(interFreqCell,globalFileNames['interFreqCell']) 
                    writeDB(interRATCell,globalFileNames['interRATCell']) 
                    writeDB(EUTRA_FrequencyAndPriorityInfo,globalFileNames['EUTRA_FrequencyAndPriorityInfo']) 
                    for each in Events3g:
                        if Events3g[each]:
                            # print each,Events3g[each]
                            # sys.exit()
                            # 'PLMN': None, 'timestamp': None,'Cell ID': None,'LAC ID': None, 
                            Events3g[each]['PLMN'] = None
                            Events3g[each]['timestamp'] = None
                            Events3g[each]['Cell ID'] = None
                            Events3g[each]['LAC ID'] = None
                            Events3g[each] = copyVals(Events3g[each],threeg_rrc_cerv_cell_info)
                            if Eventsbool[each] == 0:
                                Eventsbool[each] =1
                                globalFileNames[each].write(",".join(Events3g[each].keys())+'\n')

                            writeDB(Events3g[each],globalFileNames[each])         

                prim3gKey = ()
                Flush()
                continue

            #  changed here
            # time to find next serving cell
            if foundCervCell == True and line[0] != '{': 
                foundCervCell, foundPair = False, False

            if foundPair == True and line == "lte_rrc_cerv_cell_info":
                # found pair and serving cell info
                currentMsgType = line
                currentRAT = "LTE"
                foundCervCell = True
                continue
            elif foundPair == True and line != "lte_rrc_cerv_cell_info":
                # found pair but not the serving cell info
                foundPair = False

            if foundCervCell == True:
                continue
                dictValue = eval(line)
                primKey = (dictValue['Cell Identity'],dictValue['Downlink frequency'])
                if primKey not in dictCell:
                    ServCell =  copyVals(ServCell,dictValue)
                    SIB5 = copyVals(SIB5,ServCell)
                    SIB6 = copyVals(SIB6,ServCell)
                    SIB8 = copyVals(SIB8,ServCell)
                    Events = copyVals(Events,ServCell)
                    dictCell[primKey] ={}
                else:
                    continue

            if line in dictLteConfig:
                continue
                currentMsgType = line
                currentRAT = "LTE"
                if primKey !=() and currentMsgType not in dictCell[primKey]:
                    dictCell[primKey][currentMsgType] = {}

            if line in dictWcdmaConfig:
                currentMsgType = line
                currentRAT = "WCDMA"
                if prim3gKey !=() and currentMsgType not in dict3gCell[prim3gKey]:
                    dict3gCell[prim3gKey][currentMsgType] = {}
                continue

            try:
                dictValue = eval(line)
            except Exception as e:
                # print line
                # print counter
                continue

            if primKey != () and currentMsgType in dictCell[primKey] and currentMsgType!="lte_rrc_cerv_cell_info":
                continue
                # if currentMsgType.startswith('[sib3]'):
                #     copyVals(ServCell,dictValue)
                processSibs(primKey,currentMsgType,line)

            if prim3gKey != () and currentMsgType in dict3gCell[prim3gKey]:
                process3g(prim3gKey,currentMsgType,line)

            counter +=1
            if counter % 10000==0: print counter


        # print dictCell
        # print dict3gCell

        # for writing to files
        # outFile = open('Data_Out/' + filename.split('/')[-1],'w+')
        # outFile.write(str(dictCell))
        # outFile.write('\n')
        # outFile.write(str(dict3gCell))
        # sys.exit()

