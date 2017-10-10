#!/usr/bin/python

import os
import sys
import matplotlib.pyplot as plt
import itertools
import re
import datetime
import pandas as pd
import collections
from collections import Counter
import sqlite3


def processCervCell(primKey,secKey, dictValue):
        # line = str(dictValue.items())
        currtimestamp = dictValue['timestamp']
        del dictValue['timestamp']
        line = str(dictValue)
        try:
            if "lasttimestamp" in dictCell[primKey][secKey]:
                if currtimestamp > dictCell[primKey][secKey]["lasttimestamp"]:
                    dictCell[primKey][secKey]["lasttimestamp"] = currtimestamp
            else:
                dictCell[primKey][secKey]["lasttimestamp"] = currtimestamp    
            if line not in dictCell[primKey][secKey]:
                dictCell[primKey][secKey][line] = 0
            if line in dictCell[primKey][secKey]:
                dictCell[primKey][secKey][line] += 1
        except Exception as e:
            pass

def processSibs(primKey,secKey,line):
        # line = str(dictValue.items())
        try:
            if line not in dictCell[primKey][secKey]:
                dictCell[primKey][secKey][line] = 0
            else:
                dictCell[primKey][secKey][line] += 1
        except Exception as e:
            pass
            # print tupleDict
            # sys.exit()

def process3g(primKey,secKey,line):

    # tupleDict = str(dict3gCell.items())
    try:
        if line not in dict3gCell[primKey][secKey]:
            dict3gCell[primKey][secKey][line] = 0
        else:
            dict3gCell[primKey][secKey][line] += 1
    except Exception as e:
        pass
        print line
        # print
    
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
    currentMsgType = None
    currentRAT = None


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
            }

    threshX_lte1xrtt_total = 0
    threshX_lte1xrtt_weird = 0

    threshX_lteumts_total = 0
    threshX_lteumts_weird = 0

    threshX_lteinter_total = 0
    threshX_lteinter_weird = 0

    eventA3_weird = 0
    eventA3_total = 0

    eventA5_weird = 0
    eventA5_total = 0

    for root, dirs, files in os.walk(sys.argv[1]):
        for f in files:
            # print f
            if f.endswith(".txt"):
                resultFile.append(os.path.join(root, f))

    dictCell, foundPair, foundCervCell, primKey = {}, False, False, ()
    dict3gCell, found3gPair, prim3gKey = {}, False, ()
    counter = 0
    for filename in resultFile:
        print filename
        f = open(filename)
        for line in f:
            line = line.rstrip()
            matchObj = re.match(r'\(\d*, \d*\)', line, re.M|re.I)
            if matchObj:
                cellID, down3gFreq = eval(matchObj.group(0))
                # print cellID
                if cellID > 503:
                    found3gPair = True
                    prim3gKey = (cellID,down3gFreq)
                    dict3gCell[prim3gKey] = {}
                else:
                    foundPair = True
                    primKey = () # find the next pair
                    prim3gKey = ()
                continue

            if line == "-----------------------------------------------------------" or line == "{}":
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
                dictValue = eval(line)
                primKey = (dictValue['Cell Identity'],dictValue['Downlink frequency'])
                if primKey not in dictCell:
                    dictCell[primKey] = {k:{} for k in dictLteConfig}
                    dictCell[primKey]["lte_rrc_cerv_cell_info"] ={}
                processCervCell(primKey,"lte_rrc_cerv_cell_info",dictValue)

            if line in dictLteConfig:
                currentMsgType = line
                currentRAT = "LTE"
                if primKey !=() and currentMsgType not in dictCell[primKey]:
                    dictCell[primKey][currentMsgType] = {}
                continue

            if line in dictWcdmaConfig:
                currentMsgType = line
                currentRAT = "WCDMA"
                if prim3gKey !=() and currentMsgType not in dict3gCell[prim3gKey]:
                    dict3gCell[prim3gKey][currentMsgType] = {}
                continue

            dictValue = eval(line)

            if primKey != () and currentMsgType in dictCell[primKey] and currentMsgType!="lte_rrc_cerv_cell_info":
                # counter += 1
                processSibs(primKey,currentMsgType,line)

            if prim3gKey != () and currentMsgType in dict3gCell[prim3gKey]:
                counter += 1
                process3g(prim3gKey,currentMsgType,line)

            if currentMsgType == "lte_report_configuration":
                if len(dictValue['event_list']) < 1:
                    continue
                event_list = dictValue['event_list'][0]
                event_type = "lte_" + event_list['event_type']
                event_list.pop('event_type')
                hyst = str(dictValue['hyst'])
                if 'hyst' not in dictLteConfig[event_type]:
                    dictLteConfig[event_type]['hyst'] = []
                dictLteConfig[event_type]['hyst'].append(hyst)
                for key in event_list:
                    if key not in dictLteConfig[event_type]:
                        dictLteConfig[event_type][key] = []
                    dictLteConfig[event_type][key].append(str(event_list[key]))
                if event_type == 'lte_a3':
                    offset = event_list['offset']
                    eventA3_total = eventA3_total + 1
                    if float(offset) - float(hyst) <= 0:
                        eventA3_weird = eventA3_weird + 1
                if event_type == 'lte_a5':
                    threshold1 = event_list['threshold1']
                    threshold2 = event_list['threshold2']
                    eventA5_total = eventA5_total + 1
                    if float(threshold1) - float(hyst) >= float(threshold2) + float(hyst):
                        eventA5_weird = eventA5_weird + 1
                # continue
            if currentMsgType == "2g3g_report_reconfiguration":
                if len(dictValue['event_list']) < 1:
                    continue
                event_list = dictValue['event_list'][0]
                event_type = "lte_interRAT_" + event_list['event_type']
                event_list.pop('event_type')
                hyst = str(dictValue['hyst'])
                if 'hyst' not in dictLteConfig[event_type]:
                    dictLteConfig[event_type]['hyst'] = []
                dictLteConfig[event_type]['hyst'].append(hyst)
                for key in event_list:
                    if key not in dictLteConfig[event_type]:
                        dictLteConfig[event_type][key] = []
                    dictLteConfig[event_type][key].append(str(event_list[key]))
                # continue
            if currentMsgType == "[sib8]":
                high = int(dictValue['threshX_High'])
                low = int(dictValue['threshX_Low'])
                if high > low:
                    threshX_lte1xrtt_weird = threshX_lte1xrtt_weird + 1
                threshX_lte1xrtt_total = threshX_lte1xrtt_total + 1
            if currentMsgType == "[sib5]InterFreqCarrierFreqInfo_element":
                high = int(dictValue['threshX_High'][:-2])
                low = int(dictValue['threshX_Low'][:-2])
                if high > low:
                    threshX_lteinter_weird = threshX_lteinter_weird + 1
                threshX_lteinter_total = threshX_lteinter_total + 1
            if currentMsgType == "[sib6]CarrierFreqUTRA_FDD_element":
                high = int(dictValue['threshX_High'][:-2])
                low = int(dictValue['threshX_Low'][:-2])
                if high > low:
                    threshX_lteumts_weird = threshX_lteumts_weird + 1
                threshX_lteumts_total = threshX_lteumts_total + 1

            if currentRAT == "LTE":
                for key in dictValue:
                    if key not in dictLteConfig[currentMsgType]:
                        dictLteConfig[currentMsgType][key] = []
                    dictLteConfig[currentMsgType][key].append(str(dictValue[key]))

            if currentRAT == "WCDMA":
                for key in dictValue:
                    if key not in dictWcdmaConfig[currentMsgType]:
                        dictWcdmaConfig[currentMsgType][key] = []
                    dictWcdmaConfig[currentMsgType][key].append(str(dictValue[key]))


    # print dict3gCell
    # print dictCell
    outFile = open('outdata.txt','w+')
    outFile.write(str(dictCell))

    # sortedConfigType = collections.OrderedDict(sorted(dictLteConfig.items()))
    # for configType, item in sortedConfigType.iteritems():
    #     print configType
    #     sortedItem = collections.OrderedDict(sorted(item.items()))
    #     for key in sortedItem:
    #         print key
    #         c = Counter(item[key])
    #         vallist = c.keys()
    #         vallist.sort(key=alphanum_key)
    #         for val in vallist:
    #             print val, c[val]
    #         print
    #     print

    # sortedConfigType = collections.OrderedDict(sorted(dictWcdmaConfig.items()))
    # for configType, item in sortedConfigType.iteritems():
    #     print configType
    #     sortedItem = collections.OrderedDict(sorted(item.items()))
    #     for key in sortedItem:
    #         print key
    #         c = Counter(item[key])
    #         vallist = c.keys()
    #         vallist.sort(key=alphanum_key)
    #         for val in vallist:
    #             print val, c[val]
    #         print
    #     print

    # print "threshXHigh greater than threshXLow (lte inter freq): " +  str(threshX_lteinter_weird) + " in total " + str(threshX_lteinter_total)
    # print "threshXHigh greater than threshXLow (lte to umts): " + str(threshX_lteumts_weird) + " in total " + str(threshX_lteumts_total)
    # print "threshXHigh greater than threshXLow (lte to 1xRTT): " + str(threshX_lte1xrtt_weird) + " in total " + str(threshX_lte1xrtt_total)
    # print
    # print "LTE - event A3, offset - hyst less than or equal to 0: " + str(eventA3_weird) + " in total " + str(eventA3_total)
    # print
    # print "LTE - event A5, threshold1 - hyst greater than or equal to threshold2 + hyst: " + str(eventA5_weird) + " in total " + str(eventA5_total)
