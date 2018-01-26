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

try:
    filelist = [ f for f in os.listdir('Data_Out/') if f.endswith(".csv") ]
    for f in filelist:
        os.remove(os.path.join(mydir, f))
except Exception as e:
    pass

def processGSM(primKey,secKey,line):
    try:
        if 'gsm_reselection_parameters' in secKey:
            global GSM_Reselection_Parameters
            GSM_Reselection_Parameters =  copyVals(GSM_Reselection_Parameters,eval(line))
            writeDB(GSM_Reselection_Parameters,globalFileNames['GSM_Reselection_Parameters'])

    except Exception as e:
        print e
        pass

def processEVDO(primKey,secKey,line):
    try:
        if 'evdo_other_rat' in secKey:
            global EVDO_Other_RAT
            EVDO_Other_RAT =  copyVals(EVDO_Other_RAT,eval(line))
            writeDB(EVDO_Other_RAT,globalFileNames['EVDO_Other_RAT'])

    except Exception as e:
        print e
        pass

def processRTT(primKey, secKey, line):
    pass

def Flush():
    global GSM_Cell_Information
    global GSM_Reselection_Parameters
    global RTT_CDMA_Paging
    global EVDO_Sector_Parameters
    global EVDO_Other_RAT

    GSM_Cell_Information = {
            'Carrier': 'Null',
            'MCC': 'Null',
            'MNC': 'Null',
            'LAC': 'Null',
            'BSIC-NCC': 'Null',
            'BSIC-BCC': 'Null',
            'Cell ID': 'Null',
            'timestamp': 'Null',
            'lon': 'Null',
            'lat': 'Null',
            'country': 'Null',
            'state': 'Null',
            'city': 'Null',
            'Cell Selection Priority': 'Null',
            'BCCH ARFCN': 'Null',
            }

    GSM_Reselection_Parameters = {
            'MCC': 'Null',
            'MNC': 'Null',
            'LAC': 'Null',
            'BSIC-NCC': 'Null',
            'BSIC-BCC': 'Null',
            'Cell ID': 'Null',
            'timestamp': 'Null',
            'Penalty Time': 'Null',
            'RxLev Access Min': 'Null',
            'Temporary Offset (dB)': 'Null',
            'Cell Bar Qualify': 'Null',
            'Power Offset': 'Null',
            'Power Offset Valid': 'Null',
            'MS_TXPWR_MAX_CCH': 'Null',
            'Cell Reselection Offset (dB)': 'Null',
            'Cell Reselection Hysteresis': 'Null',
            }

    RTT_CDMA_Paging = {
            'Carrier': 'Null',
            'NID': 'Null',
            'SID': 'Null',
            'Base ID': 'Null',
            'timestamp': 'Null',
            'lon': 'Null',
            'lat': 'Null',
            'country': 'Null',
            'state': 'Null',
            'city': 'Null',
            'T_Add': 'Null',
            'T_Comp': 'Null',
            'T_Drop': 'Null',
            'T_TDrop': 'Null',
            }

    EVDO_Sector_Parameters = {
            'Carrier': 'Null',
            'Country Code': 'Null',
            'Subnet ID': 'Null',
            'Sector ID': 'Null',
            'timestamp': 'Null',
            'lon': 'Null',
            'lat': 'Null',
            'country': 'Null',
            'state': 'Null',
            'city': 'Null',
            'Band': 'Null',
            'Channel Number': 'Null',
            }

    EVDO_Other_RAT = {
            'Country Code': 'Null',
            'Subnet ID': 'Null',
            'Sector ID': 'Null',
            'timestamp': 'Null',
            'servPriority': 'Null',
            'threshServ': 'Null',
            'MaxReselectionTimer': 'Null',
            'EARFCN': 'Null',
            'EARFCNPriority': 'Null',
            'ThreshX': 'Null',
            'RxLevMinEUTRA': 'Null',
            'PeMax': 'Null',
            'RxLevMinOffset': 'Null',
            'MeasurementBandWidth': 'Null',
            }

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
        print "Usage: python Extract_Parameter_CSV_3G2G.py [/Folder_with_log_output]"
        exit()

    resultFile = []
    for root, dirs, files in os.walk(sys.argv[1]):
        for f in files:
            resultFile.append(os.path.join(root, f))

    Flush()
    print resultFile
    for filename in resultFile:
        foo = filename.split('.')[0]
        foo = 'Data_Out/'+foo.split('/')[1]
        globalFileNames = {
                'GSM_Cell_Information': open(foo+'GSM_Cell_Information.csv','a+'),
                'GSM_Reselection_Parameters':open(foo+'GSM_Reselection_Parameters.csv','a+'),
                'RTT_CDMA_Paging':open(foo+'RTT_CDMA_Paging.csv','a+'),
                'EVDO_Sector_Parameters':open(foo+'EVDO_Sector_Parameters.csv','a+'),
                'EVDO_Other_RAT':open(foo+'EVDO_Other_RAT.csv','a+')
                }
        globalFileNames['GSM_Cell_Information'].write(",".join(GSM_Cell_Information.keys())+'\n')
        globalFileNames['GSM_Reselection_Parameters'].write(",".join(GSM_Reselection_Parameters.keys())+'\n')
        globalFileNames['RTT_CDMA_Paging'].write(",".join(RTT_CDMA_Paging.keys())+'\n')
        globalFileNames['EVDO_Sector_Parameters'].write(",".join(EVDO_Sector_Parameters.keys())+'\n')
        globalFileNames['EVDO_Other_RAT'].write(",".join(EVDO_Other_RAT.keys())+'\n')
        currentMsgType = None
        currentRAT = None
        # Out

        dictGSMConfig = {
                "gsm_cell_information":{},
                "gsm_reselection_parameters":{},
                }
        dictEVDOConfig = {
                "evdo_sector_parameters":{},
                "evdo_other_rat":{},
                }
        dictRTTConfig = {
                "cdma_paging":{},
                }

        dictGSMCell, foundGSMPair, foundGSMServCell, primGSMKey = {}, False, False, ()
        dictEVDOCell, foundEVDOPair, foundEVDOServCell, primEVDOKey = {}, False, False, ()
        dictRTTCell, foundRTTPair, foundRTTServCell, primRTTKey = {}, False, False, ()

        counter = 0
        print filename
        f = open(filename)
        for line in f:
            # print line
            line = line.rstrip()
            matchObjGSM = re.match(r'\(.*, \'GSM\', .*, .*, .*, .*, .*\)', line, re.M|re.I)
            matchObjEVDO = re.match(r'\(.*, \'EVDO\', .*, .*, .*\)', line, re.M|re.I)
            matchObjRTT = re.match(r'\(.*, \'RTT\', .*, .*, .*\)', line, re.M|re.I)

            if matchObjGSM:
                Carrier, RAT, mcc, mnc, lac, cid, bsicncc, bsicbcc = eval(matchObjGSM.group(0))
                Carrier = str(Carrier).split('.')[0]
                foundGSMPair = True
                primGSMKey = (mcc, mnc, lac, cid, bsicncc, bsicbcc)
                if primGSMKey not in dictGSMCell:
                    dictGSMCell[primGSMKey] = {k:{} for k in dictGSMConfig}
                continue

            if matchObjEVDO:
                Carrier, RAT, countryCode, subnetID, sectorID = eval(matchObjEVDO.group(0))
                Carrier = str(Carrier).split('.')[0]
                foundEVDOPair = True
                primEVDOKey = (countryCode, subnetID, sectorID)
                if primEVDOKey not in dictEVDOCell:
                    dictEVDOCell[primEVDOKey] = {k:{} for k in dictEVDOConfig}
                continue

            if matchObjRTT:
                Carrier, RAT, sid, nid, baseId = eval(matchObjRTT.group(0))
                Carrier = str(Carrier).split('.')[0]
                foundRTTPair = True
                primRTTKey = (sid, nid, baseId)
                if primRTTKey not in dictRTTCell:
                    dictRTTCell[primRTTKey] = {k:{} for k in dictRTTConfig}
                continue

            # GSM
            if foundGSMPair == True and line == "gsm_cell_information":
                foundGSMServCell = True
                continue
            if foundGSMServCell == True and line[0] != '{':
                foundGSMServCell = False
                GSM_Cell_Information['Carrier'] = Carrier
                writeDB(GSM_Cell_Information,globalFileNames['GSM_Cell_Information'])

            if foundGSMServCell == True:
                dictValue = eval(line)
                GSM_Cell_Information = copyVals(GSM_Cell_Information, dictValue)
                GSM_Reselection_Parameters = copyVals(GSM_Reselection_Parameters, dictValue)
                continue

            if line in dictGSMConfig:
                currentMsgType = line
                currentRAT = "GSM"
                continue

            # EVDO
            if foundEVDOPair == True and line == "evdo_sector_parameters":
                foundEVDOServCell = True
                continue
            if foundEVDOServCell == True and line[0] != '{':
                foundEVDOServCell = False
                EVDO_Sector_Parameters['Carrier'] = Carrier
                writeDB(EVDO_Sector_Parameters,globalFileNames['EVDO_Sector_Parameters'])

            if foundEVDOServCell == True:
                dictValue = eval(line)
                EVDO_Sector_Parameters = copyVals(EVDO_Sector_Parameters, dictValue)
                EVDO_Other_RAT = copyVals(EVDO_Other_RAT, dictValue)
                continue

            if line in dictEVDOConfig:
                currentMsgType = line
                currentRAT = "EVDO"
                continue

            # RTT
            if foundRTTPair == True and line == "cdma_paging":
                foundRTTServCell = True
                continue
            if foundRTTServCell == True and line[0] != '{':
                foundRTTServCell = False
                RTT_CDMA_Paging['Carrier'] = Carrier
                writeDB(RTT_CDMA_Paging,globalFileNames['RTT_CDMA_Paging'])

            if foundRTTServCell == True:
                dictValue = eval(line)
                RTT_CDMA_Paging = copyVals(RTT_CDMA_Paging, dictValue)
                continue

            if line in dictRTTConfig:
                currentMsgType = line
                currentRAT = "RTT"
                continue

            if line == "-----------------------------------------------------------" or line == "{}" or line[:11] == "(MI)Unknown":
                foundGSMPair, foundEVDOPair, foundRTTPair = False,False,False
                foundGSMServCell, foundEVDOServCell, foundRTTServCell = False,False,False
                primGSMKey, primEVDOKey, primRTTKey = (), (), ()
                Flush()
                continue

            try:
                dictValue = eval(line)
            except Exception as e:
                print line
                print counter
                continue

            if foundGSMPair and primGSMKey != ():
                processGSM(primGSMKey,currentMsgType,line)

            if foundEVDOPair and primEVDOKey != ():
                processEVDO(primEVDOKey,currentMsgType,line)

            if foundRTTPair and primRTTKey != ():
                processRTT(primRTTKey,currentMsgType,line)

            counter +=1
            if counter % 10000==0: print counter

