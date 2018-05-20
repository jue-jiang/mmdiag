#!/usr/bin/python
# Filename: mobilitymisconfig_analyzer.py
"""
Author: Haotian Deng
"""

from mobile_insight.analyzer.analyzer import *
import ast
import subprocess
import xml.etree.ElementTree as ET
import datetime
import re
from datetime import datetime
import datetime

__all__ = ["IdleHandoffAnalyzer"]

#-----------------------------------------------------------------------------

class IdleHandoffAnalyzer(Analyzer):
    """
    Analyze the MobilityMisconfig of the phone.
    """

    def __init__(self):
        self.reset()
        Analyzer.__init__(self)
        self.add_source_callback(self.__filter)
        self.__waiting_for_signal = {}

    def reset(self):
        self.__current_LTE_shortCellID = None
        self.__current_LTE_freq = None
        self.__current_LTE_sib1 = {}
        self.__current_LTE_sib3_cellReselectionInfoCommon = {}
        self.__current_LTE_sib3_cellReselectionServingFreqInfo = {}
        self.__current_LTE_sib3_intraFreqCellReselectionInfo = {}
        self.__current_LTE_sib5 = {}
        self.__signal_strength = {}


    def set_source(self,source):
        """
        Set the trace source. Enable the WCDMA RRC messages.

        :param source: the trace source.
        :type source: trace collector
        """
        Analyzer.set_source(self,source)

        # source.enable_log("CDMA_Paging_Channel_Message")

        # # source.enable_log("1xEV_Signaling_Control_Channel_Broadcast")

        # source.enable_log("UMTS_NAS_GMM_State")
        # source.enable_log("UMTS_NAS_MM_State")
        # source.enable_log("UMTS_NAS_OTA_Packet")
        # source.enable_log("WCDMA_RRC_Serv_Cell_Info")
        # source.enable_log("WCDMA_RRC_OTA_Packet")

        source.enable_log("LTE_RRC_OTA_Packet")
        # source.enable_log("LTE_RRC_MIB_Message_Log_Packet")
        # source.enable_log("LTE_RRC_Serv_Cell_Info")
        source.enable_log("LTE_PHY_Serv_Cell_Measurement")
        # source.enable_log("LTE_NAS_EMM_State")
        # source.enable_log("LTE_NAS_ESM_OTA_Incoming_Packet")
        # source.enable_log("LTE_NAS_ESM_OTA_Outgoing_Packet")
        # source.enable_log("LTE_NAS_EMM_OTA_Incoming_Packet")
        # source.enable_log("LTE_NAS_EMM_OTA_Outgoing_Packet")

    def __filter(self, event):
        try:
            log_item = event.data.decode()
            decoded_event = Event(event.timestamp, event.type_id, log_item)

            if event.type_id == "LTE_RRC_OTA_Packet":
                self.__callback_lte_rrc_ota(decoded_event)
            elif event.type_id == "LTE_PHY_Serv_Cell_Measurement":
                self.__callback_lte_phy_serv_cell_measurement(decoded_event)

            # elif event.type_id == "LTE_RRC_Serv_Cell_Info":
            #     self.__callback_lte_rrc_serv_cell_info(decoded_event)
        except Exception as e:
            print "Exception", e
            pass

    def print_by_format(self, dict_info):
        oldCell = dict_info['oldCell']
        rsrp_oldCell = str(oldCell['RSRP'])
        rsrq_oldCell = str(oldCell['RSRQ'])
        rssi_oldCell = str(oldCell['RSSI'])
        newCell = dict_info['newCell']
        rsrp_newCell = str(newCell['RSRP'])
        rsrq_newCell = str(newCell['RSRQ'])
        rssi_newCell = str(newCell['RSSI'])

        newPriority = str(dict_info['newPriority'])

        strTimestamp = str(dict_info['timestamp'])
        if "." in strTimestamp:
            dateTimestamp = datetime.datetime.strptime(strTimestamp, '%Y-%m-%d %H:%M:%S.%f')
        else:
            dateTimestamp = datetime.datetime.strptime(strTimestamp, '%Y-%m-%d %H:%M:%S')
        timestampEST = dateTimestamp - datetime.timedelta(hours=5)
        strTimestamp = timestampEST.strftime("%Y/%m/%d/%H:%M:%S.%f")

        sib1_q_RxLevMin = "Unknown"
        sib1_q_RxLevMinOffset = "Unknown"
        sib3_s_NonIntraSearch = "Unknown"
        sib3_threshServingLow = "Unknown"
        sib3_q_RxLevMin = "Unknown"
        sib3_s_IntraSearch = "Unknown"
        sib3_t_ReselectionEUTRA = "Unknown"
        sib5_q_RxLevMin = "Unknown"
        sib5_threshX_High = "Unknown"
        sib5_threshX_Low = "Unknown"
        oldPriority = "Unknown"
        if 'sib1' in dict_info:
            tupleData = dict_info['sib1']
            if 'q_RxLevMin' in tupleData:
                sib1_q_RxLevMin = str(tupleData['q_RxLevMin'])
            if 'q_RxLevMinOffset' in tupleData:
                sib1_q_RxLevMinOffset = str(tupleData['q_RxLevMinOffset'])
                if sib1_q_RxLevMinOffset == "Not Present":
                    sib1_q_RxLevMinOffset = "Unknown"
        if 'sib3_cellReselectionServingFreqInfo' in dict_info:
            tupleData = dict_info['sib3_cellReselectionServingFreqInfo']
            if 's_NonIntraSearch' in tupleData:
                sib3_s_NonIntraSearch = str(tupleData['s_NonIntraSearch'])
            if 'threshServingLow' in tupleData:
                sib3_threshServingLow = str(tupleData['threshServingLow'])
            if 'cellReselectionPriority' in tupleData:
                oldPriority = str(tupleData['cellReselectionPriority'])
        if 'sib3_intraFreqCellReselectionInfo' in dict_info:
            tupleData = dict_info['sib3_intraFreqCellReselectionInfo']
            if 'q_RxLevMin' in tupleData:
                sib3_q_RxLevMin = str(tupleData['q_RxLevMin'])
            if 's_IntraSearch' in tupleData:
                sib3_s_IntraSearch = str(tupleData['s_IntraSearch'])
            if 't_ReselectionEUTRA' in tupleData:
                sib3_t_ReselectionEUTRA = str(tupleData['t_ReselectionEUTRA'])
        if 'sib5' in dict_info:
            tupleData = dict_info['sib5']
            if 'q_RxLevMin' in tupleData:
                sib5_q_RxLevMin = str(tupleData['q_RxLevMin'])
            if 'threshX_High' in tupleData:
                sib5_threshX_High = str(tupleData['threshX_High'])
            if 'threshX_Low' in tupleData:
                sib5_threshX_Low = str(tupleData['threshX_Low'])

        title = "# timestamp rsrp_before rsrq_before rssi_before rsrp_after rsrq_after rssi_after " + \
                "sib1_q_RxLevMin sib1_q_RxLevMinOffset sib3_q_RxLevMin sib3_s_IntraSearch sib3_s_NonIntraSearch sib3_threshServingLow sib3_t_ReselectionEUTRA " + \
                "sib5_q_RxLevMin sib5_threshX_High sib5_threshX_Low " + \
                "isIntraHandoff " + \
                "oldPriority newPriority"
        # print title
        output = strTimestamp + " " + rsrp_oldCell + " " + rsrq_oldCell + " " + rssi_oldCell + " " + rsrp_newCell + " " + rsrq_newCell + " " + rssi_newCell + " " + \
                sib1_q_RxLevMin + " " + sib1_q_RxLevMinOffset + " " + \
                sib3_q_RxLevMin + " " + sib3_s_IntraSearch + " " + sib3_s_NonIntraSearch + " " + \
                sib3_threshServingLow + " " + sib3_t_ReselectionEUTRA + " " + \
                sib5_q_RxLevMin + " " + sib5_threshX_High + " " + sib5_threshX_Low + " " + \
                str(dict_info['isIntra']) + " " + \
                oldPriority + " " + newPriority
        print output
        # for signal in dict_info['signal_before']:
        #     print signal['timestamp'], signal['RSRP'], signal['RSRQ'], signal['RSSI']


    def handle_handoff(self, oldCellID, oldFreq, newCellID, newFreq, timestamp):

        # print "sib1", self.__current_LTE_sib1
        # print "sib3 cellReselectionInfoCommon", self.__current_LTE_sib3_cellReselectionInfoCommon
        # print "sib3 intraFreqCellReselectionInfo", self.__current_LTE_sib3_intraFreqCellReselectionInfo
        # print "sib3 cellReselectionServingFreqInfo", self.__current_LTE_sib3_cellReselectionServingFreqInfo
        # print "sib5", self.__current_LTE_sib5

        oldCellID = str(oldCellID)
        oldFreq = str(oldFreq)
        newCellID = str(newCellID)
        newFreq = str(newFreq)
        if (oldCellID, oldFreq) not in self.__signal_strength:
            # print "no signal info for old cell", (oldCellID, oldFreq)
            self.reset()
            return

        if (newCellID, newFreq) in self.__signal_strength:
            self.__waiting_for_signal = {(newCellID, newFreq): {"oldCell": self.__signal_strength[(oldCellID, oldFreq)][-1], "newCell": self.__signal_strength[(newCellID, newFreq)][0]}}
            self.__waiting_for_signal[(newCellID, newFreq)]["timestamp"] = timestamp
            self.__waiting_for_signal[(newCellID, newFreq)]["sib1"] = self.__current_LTE_sib1
            self.__waiting_for_signal[(newCellID, newFreq)]["sib3_cellReselectionInfoCommon"] = self.__current_LTE_sib3_cellReselectionInfoCommon
            self.__waiting_for_signal[(newCellID, newFreq)]["sib3_intraFreqCellReselectionInfo"] = self.__current_LTE_sib3_intraFreqCellReselectionInfo
            self.__waiting_for_signal[(newCellID, newFreq)]["sib3_cellReselectionServingFreqInfo"] = self.__current_LTE_sib3_cellReselectionServingFreqInfo
            self.__waiting_for_signal[(newCellID, newFreq)]["sib5"] = self.__current_LTE_sib5
            self.__waiting_for_signal[(newCellID, newFreq)]["isIntra"] = (oldFreq == newFreq)
            self.__waiting_for_signal[(newCellID, newFreq)]["signal_before"] = self.__signal_strength[(oldCellID, oldFreq)]

            if "newPriority" in self.__waiting_for_signal[(newCellID, newFreq)]:
                self.print_by_format(self.__waiting_for_signal[(newCellID, newFreq)])
                self.__waiting_for_signal = {}
        else:
            self.__waiting_for_signal = {(newCellID, newFreq): {"oldCell": self.__signal_strength[(oldCellID, oldFreq)][-1]}}
            self.__waiting_for_signal[(newCellID, newFreq)]["timestamp"] = timestamp
            self.__waiting_for_signal[(newCellID, newFreq)]["sib1"] = self.__current_LTE_sib1
            self.__waiting_for_signal[(newCellID, newFreq)]["sib3_cellReselectionInfoCommon"] = self.__current_LTE_sib3_cellReselectionInfoCommon
            self.__waiting_for_signal[(newCellID, newFreq)]["sib3_intraFreqCellReselectionInfo"] = self.__current_LTE_sib3_intraFreqCellReselectionInfo
            self.__waiting_for_signal[(newCellID, newFreq)]["sib3_cellReselectionServingFreqInfo"] = self.__current_LTE_sib3_cellReselectionServingFreqInfo
            self.__waiting_for_signal[(newCellID, newFreq)]["sib5"] = self.__current_LTE_sib5
            self.__waiting_for_signal[(newCellID, newFreq)]["isIntra"] = (oldFreq == newFreq)
            self.__waiting_for_signal[(newCellID, newFreq)]["signal_before"] = self.__signal_strength[(oldCellID, oldFreq)]
            # print self.__waiting_for_signal

        self.reset()

    def __callback_lte_phy_serv_cell_measurement(self, event):
        log_item = event.data
        subpkt = log_item['Subpackets'][0]
        CellID = str(subpkt['Physical Cell ID'])
        DLFreq = str(subpkt['E-ARFCN'])
        RSRP = subpkt['RSRP']
        RSRQ = subpkt['RSRQ']
        RSSI = subpkt['RSSI']
        dateTimestamp = log_item['timestamp']
        # print strTimestamp
        # if "." in strTimestamp:
        #     dateTimestamp = datetime.datetime.strptime(strTimestamp, '%Y-%m-%d %H:%M:%S.%f')
        # else:
        #     dateTimestamp = datetime.datetime.strptime(strTimestamp, '%Y-%m-%d %H:%M:%S')
        timestampEST = dateTimestamp - datetime.timedelta(hours=5)
        strTimestamp = timestampEST.strftime("%Y/%m/%d/%H:%M:%S.%f")

        if (CellID, DLFreq) not in self.__signal_strength:
            self.__signal_strength[(CellID, DLFreq)] = []
        self.__signal_strength[(CellID, DLFreq)].append({"timestamp": strTimestamp, "RSRP": RSRP, "RSRQ": RSRQ, "RSSI": RSSI})
        if self.__waiting_for_signal != None and (CellID, DLFreq) in self.__waiting_for_signal:
            self.__waiting_for_signal[(CellID, DLFreq)]["newCell"] = self.__signal_strength[(CellID, DLFreq)][0]
            if "newPriority" in self.__waiting_for_signal[(CellID, DLFreq)]:
                self.print_by_format(self.__waiting_for_signal[(CellID, DLFreq)])
                self.__waiting_for_signal = {}

    def __callback_lte_rrc_ota(self, event):
        log_item = event.data
        log_xml = ET.fromstring(log_item["Msg"])

        is_sib1 = False
        is_sib3 = False
        is_sib4 = False
        is_sib5 = False
        is_sib6 = False
        is_sib7 = False
        is_sib8 = False
        is_rrc_conn_reconfig = False

        CellID = log_item["Physical Cell ID"]
        DLFreq = log_item["Freq"]
        if self.__current_LTE_shortCellID != None:
            if self.__current_LTE_shortCellID != CellID or self.__current_LTE_freq != DLFreq:
                if ((log_item["Pkt Version"] < 15 and (log_item["PDU Number"] == 2 or log_item["PDU Number"] == 9)) or (log_item["Pkt Version"] >= 15 and log_item["PDU Number"] == 2)):
                    self.handle_handoff(self.__current_LTE_shortCellID, self.__current_LTE_freq, CellID, DLFreq, log_item['timestamp'])
        self.__current_LTE_shortCellID = CellID
        self.__current_LTE_freq = DLFreq

        if ((log_item["Pkt Version"] < 15 and (log_item["PDU Number"] == 2 or log_item["PDU Number"] == 9)) or (log_item["Pkt Version"] >= 15 and log_item["PDU Number"] == 2)):
            # BCCH_DL_SCH, orignal 2
            for val in log_xml.iter("field"):
                if val.get("name") == "lte-rrc.systemInformationBlockType1_element":
                    is_sib1 = True
                elif val.get("name") == "lte-rrc.sib3_element":
                    is_sib3 = True
                elif val.get("name") == "lte-rrc.sib4_element":
                    is_sib4 = True
                elif val.get("name") == "lte-rrc.sib5_element":
                    is_sib5 = True
                elif val.get("name") == "lte-rrc.sib6_element":
                    is_sib6 = True
                elif val.get("name") == "lte-rrc.sib7_element":
                    is_sib7 = True
                elif val.get("name") == "lte-rrc.sib8_element":
                    is_sib8 = True

                # elif val.get("name") == "lte-rrc.plmn_Identity_element":
                #     mcc_mnc = ""
                #     for digit in val.iter("field"):
                #         if digit.get("name") == "lte-rrc.MCC_MNC_Digit":
                #             mcc_mnc += digit.get("show")
                #     cell_info["plmn"] = mcc_mnc[0:3] + "-" + mcc_mnc[3:]
                # elif val.get("name") == "lte-rrc.trackingAreaCode":
                #     cell_info["tac"] = int(val.get("value"), base=16)
                # elif val.get("name") == "lte-rrc.cellIdentity":
                #     cell_info["cell_id"] = int(val.get("value"), base=16) / 16

        elif (log_item["Pkt Version"] < 15 and (log_item["PDU Number"] == 6 or log_item["PDU Number"] == 13)) or (log_item["Pkt Version"] >=15 and log_item["PDU Number"] == 7):
            # LTE-RRC_DL_DCCH
            for val in log_xml.iter("field"):
                if val.get("name") == "lte-rrc.rrcConnectionReconfiguration_element":
                    is_rrc_conn_reconfig = True
                    break

        # elif (log_item["Pkt Version"] < 15 and (log_item["PDU Number"] == 8 or log_item["PDU Number"] == 15)) or (log_item["Pkt Version"] >= 15 and log_item["PDU Number"] == 9):
        #     # UL_DCCH
        #     for val in log_xml.iter("field"):
        #         if val.get("name") == "lte-rrc.measurementReport_r8_element":
        #             field_val = {}
        #             field_val["lte-rrc.measId"] = None
        #             field_val["lte-rrc.rsrpResult"] = None
        #             field_val["lte-rrc.rsrqResult"] = None
        #             neighborCells = []
        #             for attr in val.iter("field"):
        #                 field_val[attr.get("name")] = attr.get("show")
        #                 if attr.get("name") == "lte-rrc.MeasResultEUTRA_element":
        #                     subfield_val = {}
        #                     subfield_val["lte-rrc.physCellId"] = 0
        #                     subfield_val["lte-rrc.rsrpResult"] = 0
        #                     subfield_val["lte-rrc.rsrqResult"] = 0
        #                     for subattr in attr.iter("field"):
        #                         subfield_val[subattr.get("name")] = subattr.get("show")

        #                     Pattern2 = re.compile(r": '(.*)'$")
        #                     neighborCells.append(
        #                             {
        #                                 "lte-rrc.physCellId":int(subfield_val['lte-rrc.physCellId']),
        #                                 "lte-rrc.rsrpResult":int(subfield_val["lte-rrc.rsrpResult"])-140,
        #                                 "lte-rrc.rsrqResult":(int(subfield_val["lte-rrc.rsrqResult"])-40)/2.0,
        #                                 }
        #                             )
        #                     break
        #             info = {"lte-rrc.measId":field_val["lte-rrc.measId"],\
        #                     "lte-rrc.rsrpResult":int(field_val["lte-rrc.rsrpResult"])-140,\
        #                     "lte-rrc.rsrqResult":(int(field_val["lte-rrc.rsrqResult"])-40)/2.0,\
        #                     "neighborLTECells": neighborCells}
        #             try:
        #                 self.__current_LTE_shortCellID
        #             except AttributeError:
        #                 pass
        #             else:
        #                 self.__current_LTE_measurementReport.append(info)
        #             break

        if is_sib1 or is_sib3 or is_sib4 or is_sib5 or is_sib6 or is_sib7 or is_sib8 or is_rrc_conn_reconfig:
            Pattern1 = re.compile(r": (.*) \([-\d]+\)$")
            Pattern2 = re.compile(r": (.*)$")

        if is_sib1:
            info = {"q_RxLevMin": "Not Present", "q_RxLevMinOffset": "Not Present", "p_Max": "Not Present"}
            for val in log_xml.iter("field"):
                if val.get("name") == "lte-rrc.cellSelectionInfo_element":
                    for attr in val.iter("field"):
                        s = attr.get("showname")
                        if attr.get("name") in ("lte-rrc.q_RxLevMin", "lte-rrc.q_RxLevMinOffset"):
                            info[attr.get("name")[8:]] = re.findall(Pattern1, s)[0]
                if val.get("name") == "lte-rrc.p_Max":
                    attr = val
                    s = attr.get("showname")
                    info[attr.get("name")[8:]] = re.findall(Pattern2, s)[0]
            try:
                self.__current_LTE_shortCellID
            except AttributeError:
                pass
            else:
                self.__current_LTE_sib1 = info

        if is_sib3:
            # Iter over all cellReselectionInfoCommon_element
            for val in log_xml.iter("field"):
                if val.get("name") == "lte-rrc.cellReselectionInfoCommon_element":
                    info = dict()
                    for attr in val.iter("field"):
                        s = attr.get("showname")
                        if attr.get("name") in ("lte-rrc.q_Hyst"):
                            info[attr.get("name")[8:]] = re.findall(Pattern1, s)[0]
                    try:
                        self.__current_LTE_shortCellID
                    except AttributeError:
                        pass
                    else:
                        self.__current_LTE_sib3_cellReselectionInfoCommon = info

                if val.get("name") == "lte-rrc.cellReselectionServingFreqInfo_element":
                    info = dict()
                    for attr in val.iter("field"):
                        s = attr.get("showname")
                        if attr.get("name") in ("lte-rrc.s_NonIntraSearch", "lte-rrc.threshServingLow"):
                            info[attr.get("name")[8:]] = re.findall(Pattern1, s)[0]
                        if attr.get("name") in ("lte-rrc.cellReselectionPriority"):
                            info[attr.get("name")[8:]] = re.findall(Pattern2, s)[0]
                            # TODO
                            if self.__waiting_for_signal != None and (str(CellID), str(DLFreq)) in self.__waiting_for_signal:
                                self.__waiting_for_signal[(str(CellID), str(DLFreq))]["newPriority"] = info["cellReselectionPriority"]
                                if "newCell" in self.__waiting_for_signal[(str(CellID), str(DLFreq))]:
                                    self.print_by_format(self.__waiting_for_signal[(str(CellID), str(DLFreq))])
                                    self.__waiting_for_signal = {}
                    try:
                        self.__current_LTE_shortCellID
                    except AttributeError:
                        pass
                    else:
                        self.__current_LTE_sib3_cellReselectionServingFreqInfo = info

                if val.get("name") == "lte-rrc.intraFreqCellReselectionInfo_element":
                    info = dict()
                    for attr in val.iter("field"):
                        s = attr.get("showname")
                        if attr.get("name") in ("lte-rrc.q_RxLevMin", "lte-rrc.s_IntraSearch"):
                            info[attr.get("name")[8:]] = re.findall(Pattern1, s)[0]
                        if attr.get("name") in ("lte-rrc.p_Max", "lte-rrc.t_ReselectionEUTRA"):
                            info[attr.get("name")[8:]] = re.findall(Pattern2, s)[0]
                    try:
                        self.__current_LTE_shortCellID
                    except AttributeError:
                        pass
                    else:
                        self.__current_LTE_sib3_intraFreqCellReselectionInfo = info

        # if is_sib4:
        #     for val in log_xml.iter("field"):
        #         if val.get("name") == "lte-rrc.PhysCellIdRange_element":
        #             info = {"start": "Not Present", "range": "Not Present"}
        #             # Iter over all attrs
        #             for attr in val.iter("field"):
        #                 s = attr.get("showname")
        #                 if attr.get("name") in ("lte-rrc.start"):
        #                     info[attr.get("name")[8:]] = re.findall(Pattern2, s)[0]
        #                 if attr.get("name") in ("lte-rrc.range"):
        #                     info[attr.get("name")[8:]] = re.findall(Pattern1, s)[0]

        #             try:
        #                 self.__last_CellID
        #             except AttributeError:
        #                 pass
        #             else:
        #                 if "[sib4]intraFreqBlackCellList" in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq,self.__last_lte_distinguisher)].keys():
        #                     if info not in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq,self.__last_lte_distinguisher)]["[sib4]intraFreqBlackCellList"]:
        #                         self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq,self.__last_lte_distinguisher)]["[sib4]intraFreqBlackCellList"].append(info)
        #                 else:
        #                     self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq,self.__last_lte_distinguisher)]["[sib4]intraFreqBlackCellList"] = [info]
        #         if val.get("name") == "lte-rrc.IntraFreqNeighCellInfo_element":
        #             info = {"physCellId": "Not Present", "q_OffsetCell": "Not Present"}
        #             # Iter over all attrs
        #             for attr in val.iter("field"):
        #                 s = attr.get("showname")
        #                 if attr.get("name") in ("lte-rrc.physCellId"):
        #                     info[attr.get("name")[8:]] = re.findall(Pattern2, s)[0]
        #                 elif attr.get("name") in ("lte-rrc.q_OffsetCell"):
        #                     info[attr.get("name")[8:]] = re.findall(Pattern1, s)[0]
        #             try:
        #                 self.__last_CellID
        #             except AttributeError:
        #                 pass
        #             else:
        #                 if "[sib4]intraFreqNeighCellList" in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq,self.__last_lte_distinguisher)].keys():
        #                     if info not in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq,self.__last_lte_distinguisher)]["[sib4]intraFreqNeighCellList"]:
        #                         self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq,self.__last_lte_distinguisher)]["[sib4]intraFreqNeighCellList"].append(info)
        #                 else:
        #                     self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq,self.__last_lte_distinguisher)]["[sib4]intraFreqNeighCellList"] = [info]

        if is_sib5:
            for val in log_xml.iter("field"):
                if val.get("name") == "lte-rrc.InterFreqCarrierFreqInfo_element":
                    info = dict()
                    # Iter over all attrs
                    for attr in val.iter("field"):
                        s = attr.get("showname")
                        if attr.get("name") in ("lte-rrc.q_RxLevMin", "lte-rrc.threshX_High", "lte-rrc.threshX_Low", "lte-rrc.allowedMeasBandwidth", "lte-rrc.q_OffsetFreq"):
                            info[attr.get("name")[8:]] = re.findall(Pattern1, s)[0]
                        elif attr.get("name") in ("lte-rrc.dl_CarrierFreq", "lte-rrc.p_Max", "lte-rrc.t_ReselectionEUTRA", "lte-rrc.cellReselectionPriority"):
                            info[attr.get("name")[8:]] = re.findall(Pattern2, s)[0]
                        # elif attr.get("name") == "lte-rrc.PhysCellIdRange_element" and "dl_CarrierFreq" in info:
                        #     blackCellListInfo = {"start": "Not Present", "range": "Not Present"}
                        #     blackCellListInfo["dl_CarrierFreq"] = info["dl_CarrierFreq"]
                        #     # Iter over all attrs
                        #     for subAttr in attr.iter("field"):
                        #         if subAttr.get("name") in ("lte-rrc.start"):
                        #             s = subAttr.get("showname")
                        #             blackCellListInfo[subAttr.get("name")[8:]] = re.findall(Pattern2, s)[0]
                        #         if subAttr.get("name") in ("lte-rrc.range"):
                        #             s = subAttr.get("showname")
                        #             blackCellListInfo[subAttr.get("name")[8:]] = re.findall(Pattern1, s)[0]
                        #     try:
                        #         self.__last_CellID
                        #     except AttributeError:
                        #         pass
                        #     else:
                        #         if "[sib5]interFreqBlackCellList" in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq,self.__last_lte_distinguisher)].keys():
                        #             if blackCellListInfo not in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq,self.__last_lte_distinguisher)]["[sib5]interFreqBlackCellList"]:
                        #                 self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq,self.__last_lte_distinguisher)]["[sib5]interFreqBlackCellList"].append(blackCellListInfo)
                        #         else:
                        #             self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq,self.__last_lte_distinguisher)]["[sib5]interFreqBlackCellList"] = [blackCellListInfo]
                        # elif attr.get("name") == "lte-rrc.InterFreqNeighCellInfo_element" and "dl_CarrierFreq" in info:
                        #     neighCellListInfo = dict()
                        #     neighCellListInfo["dl_CarrierFreq"] = info["dl_CarrierFreq"]
                        #     # Iter over all attrs
                        #     for subAttr in attr.iter("field"):
                        #         if subAttr.get("name") in ("lte-rrc.physCellId"):
                        #             s = subAttr.get("showname")
                        #             neighCellListInfo[subAttr.get("name")[8:]] = re.findall(Pattern2, s)[0]
                        #         elif subAttr.get("name") in ("lte-rrc.q_OffsetCell"):
                        #             s = subAttr.get("showname")
                        #             neighCellListInfo[subAttr.get("name")[8:]] = re.findall(Pattern1, s)[0]
                        #     try:
                        #         self.__last_CellID
                        #     except AttributeError:
                        #         pass
                        #     else:
                        #         if "[sib5]interFreqNeighCellList" in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq,self.__last_lte_distinguisher)].keys():
                        #             if neighCellListInfo not in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq,self.__last_lte_distinguisher)]["[sib5]interFreqNeighCellList"]:
                        #                 self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq,self.__last_lte_distinguisher)]["[sib5]interFreqNeighCellList"].append(neighCellListInfo)
                        #         else:
                        #             self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq,self.__last_lte_distinguisher)]["[sib5]interFreqNeighCellList"] = [neighCellListInfo]
                    try:
                        self.__current_LTE_shortCellID
                    except AttributeError:
                        pass
                    else:
                        self.__current_LTE_sib5 = info

        # if is_sib6:
        #     # Iter over all CarrierFreqUTRA_FDD elements
        #     for val in log_xml.iter("field"):
        #         if val.get("name") == "lte-rrc.CarrierFreqUTRA_FDD_element":
        #             info = dict()
        #             # Iter over all attrs
        #             for attr in val.iter("field"):
        #                 s = attr.get("showname")
        #                 if attr.get("name") in ("lte-rrc.threshX_High", "lte-rrc.threshX_Low", "lte-rrc.q_RxLevMin"):
        #                     info[attr.get("name")[8:]] = re.findall(Pattern1, s)[0]
        #                 elif attr.get("name") in ("lte-rrc.carrierFreq", "lte-rrc.cellReselectionPriority", "lte-rrc.p_MaxUTRA", "lte-rrc.q_QualMin"):
        #                     info[attr.get("name")[8:]] = re.findall(Pattern2, s)[0]
        #             info["lte_rrc_freq"] = log_item["Freq"]
        #             try:
        #                 self.__last_CellID
        #             except AttributeError:
        #                 pass
        #             else:
        #                 if "[sib6]CarrierFreqUTRA_FDD_element" in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq,self.__last_lte_distinguisher)].keys():
        #                     if info not in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq,self.__last_lte_distinguisher)]["[sib6]CarrierFreqUTRA_FDD_element"]:
        #                         self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq,self.__last_lte_distinguisher)]["[sib6]CarrierFreqUTRA_FDD_element"].append(info)
        #                 else:
        #                     self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq,self.__last_lte_distinguisher)]["[sib6]CarrierFreqUTRA_FDD_element"] = [info]
        #             self.__lte_cell_resel_to_umts_config.append(info)
        # if is_sib7:
        #     info = {}
        #     for val in log_xml.iter("field"):
        #         if val.get("name") == "lte-rrc.t_ReselectionGERAN":
        #             attr = val
        #             s = attr.get("showname")
        #             info[attr.get("name")[8:]] = re.findall(Pattern2, s)[0]

        #         if val.get("name") == "lte-rrc.CarrierFreqsInfoGERAN_element":
        #             # Iter over all attrs
        #             for attr in val.iter("field"):
        #                 s = attr.get("showname")
        #                 if attr.get("name") in ("lte-rrc.bandIndicator", "lte-rrc.q_RxLevMin", "lte-rrc.threshX_High", "lte-rrc.threshX_Low"):
        #                     info[attr.get("name")[8:]] = re.findall(Pattern1, s)[0]
        #                 elif attr.get("name") in ("lte-rrc.cellReselectionPriority", "lte-rrc.p_MaxGERAN", "lte-rrc.startingARFCN"):
        #                     info[attr.get("name")[8:]] = re.findall(Pattern2, s)[0]
        #             try:
        #                 self.__last_CellID
        #             except AttributeError:
        #                 pass
        #             else:
        #                 if "[sib7]" in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq,self.__last_lte_distinguisher)].keys():
        #                     if info not in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq,self.__last_lte_distinguisher)]["[sib7]"]:
        #                         self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq,self.__last_lte_distinguisher)]["[sib7]"].append(info)
        #                 else:
        #                     self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq,self.__last_lte_distinguisher)]["[sib7]"] = [info]
        #             self.__lte_cell_resel_to_umts_config.append(info)
        # if is_sib8:
        #     # Iter over all CarrierFreqUTRA_FDD elements
        #     for val in log_xml.iter("field"):
        #         if val.get("name") == "lte-rrc.BandClassInfoCDMA2000_element":
        #             info = dict()
        #             # Iter over all attrs
        #             for attr in val.iter("field"):
        #                 s = attr.get("showname")
        #                 if attr.get("name") in ("lte-rrc.bandClass"):
        #                     info[attr.get("name")[8:]] = re.findall(Pattern1, s)[0]
        #                 elif attr.get("name") in ("lte-rrc.threshX_High", "lte-rrc.threshX_Low", "lte-rrc.cellReselectionPriority"):
        #                     info[attr.get("name")[8:]] = re.findall(Pattern2, s)[0]
        #             try:
        #                 self.__last_CellID
        #             except AttributeError:
        #                 pass
        #             else:
        #                 if "[sib8]" in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq,self.__last_lte_distinguisher)].keys():
        #                     if info not in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq,self.__last_lte_distinguisher)]["[sib8]"]:
        #                         self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq,self.__last_lte_distinguisher)]["[sib8]"].append(info)
        #                 else:
        #                     self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq,self.__last_lte_distinguisher)]["[sib8]"] = [info]
        #             self.__lte_cell_resel_to_umts_config.append(info)

        # if is_rrc_conn_reconfig:
        #     try:
        #         self.__current_LTE_shortCellID
        #     except AttributeError:
        #         pass
        # #********************LTE Reconfiguration*******************************
        #     else:
        #         measobj_id = -1
        #         report_id = -1

        #         for field in log_xml.iter('field'):
        #             if field.get('name') == "lte-rrc.measObjectId":
        #                 measobj_id = field.get('show')

        #             if field.get('name') == "lte-rrc.reportConfigId":
        #                 report_id = field.get('show')

        #             #Add a LTE measurement object
        #             if field.get('name') == "lte-rrc.measObjectEUTRA_element":
        #                 field_val = {}

        #                 for val in field.iter('field'):
        #                     field_val[val.get('name')] = val.get('showname')

        #                 freq = 0
        #                 offsetFreq = "Not Present"

        #                 if ('lte-rrc.offsetFreq' in field_val):
        #                     offsetFreq = re.findall(Pattern1, field_val['lte-rrc.offsetFreq'])[0]

        #                 if ('lte-rrc.carrierFreq' in field_val):
        #                     freq = re.findall(Pattern2, field_val['lte-rrc.carrierFreq'])[0]

        #                 new_info = {}
        #                 new_info = {"measobj_id":measobj_id,"freq":freq,"offsetFreq":offsetFreq}
        #                 new_info["cell_list"] = []

        #                 #2nd round: handle cell individual offset
        #                 for val in field.iter('field'):
        #                     if val.get('name') == 'lte-rrc.CellsToAddMod_element':
        #                         cell_val = {}
        #                         for item in val.iter('field'):
        #                             cell_val[item.get('name')] = item.get('showname')

        #                         if 'lte-rrc.physCellId' in cell_val:
        #                             cell_id = re.findall(Pattern2, cell_val['lte-rrc.physCellId'])[0]
        #                             cell_offset = re.findall(Pattern1, cell_val['lte-rrc.cellIndividualOffset'])[0]
        #                             new_info["cell_list"].append({"cell_id":cell_id,"cell_offset":cell_offset})

        #                 self.__current_LTE_measurementObject.append(new_info)

        #             #Add a LTE report configuration
        #             if field.get('name') == "lte-rrc.reportConfigEUTRA_element":
        #                 hyst = 0
        #                 timeToTrigger = "Not Present"
        #                 reportInterval = "Not Present"
        #                 reportAmount = "Not Present"
        #                 for val in field.iter('field'):
        #                     if val.get('name') == 'lte-rrc.hysteresis':
        #                         hyst = int(val.get('show'))
        #                     if val.get('name') == 'lte-rrc.timeToTrigger':
        #                         timeToTrigger = val.get('showname').split(':')[1].split('(')[0].replace(" ", "")
        #                     if val.get('name') == 'lte-rrc.reportInterval':
        #                         reportInterval = val.get('showname').split(':')[1].split('(')[0].replace(" ", "")
        #                     if val.get('name') == 'lte-rrc.reportAmount':
        #                         reportAmount = val.get('showname').split(':')[1].split('(')[0].replace(" ", "")

        #                 new_info = {"report_id":report_id, "hyst":hyst/2.0, "timeToTrigger":timeToTrigger, "reportInterval":reportInterval, "reportAmount":reportAmount}
        #                 new_info["event_list"] = []

        #                 for val in field.iter('field'):

        #                     if val.get('name') == 'lte-rrc.eventA1_element':
        #                         for item in val.iter('field'):
        #                             if item.get('name') == 'lte-rrc.threshold_RSRP':
        #                                 new_info["event_list"].append({"event_type":"a1","threshold":int(item.get('show'))-140})
        #                                 break
        #                             if item.get('name') == 'lte-rrc.threshold_RSRQ':
        #                                 new_info["event_list"].append({"event_type":"a1","threshold":(int(item.get('show'))-140)/2.0})
        #                                 break

        #                     if val.get('name') == 'lte-rrc.eventA2_element':
        #                         for item in val.iter('field'):
        #                             if item.get('name') == 'lte-rrc.threshold_RSRP':
        #                                 new_info["event_list"].append({"event_type":"a2","threshold":int(item.get('show'))-140})
        #                                 break
        #                             if item.get('name') == 'lte-rrc.threshold_RSRQ':
        #                                 new_info["event_list"].append({"event_type":"a2","threshold":(int(item.get('show'))-40)/2.0})
        #                                 break

        #                     if val.get('name') == 'lte-rrc.eventA3_element':
        #                         for item in val.iter('field'):
        #                             if item.get('name') == 'lte-rrc.a3_Offset':
        #                                 new_info["event_list"].append({"event_type":"a3","offset":int(item.get('show'))/2.0})
        #                                 break

        #                     if val.get('name') == 'lte-rrc.eventA4_element':
        #                         for item in val.iter('field'):
        #                             if item.get('name') == 'lte-rrc.threshold_RSRP':
        #                                 new_info["event_list"].append({"event_type":"a4","threshold":int(item.get('show'))-140})
        #                                 break
        #                             if item.get('name') == 'lte-rrc.threshold_RSRQ':
        #                                 report_config.add_event('a4',(int(item.get('show'))-40)/2.0)
        #                                 new_info["event_list"].append({"event_type":"a4","threshold":(int(item.get('show'))-40)/2.0})
        #                                 break

        #                     if val.get('name') == 'lte-rrc.eventA5_element':
        #                         threshold1 = None
        #                         threshold2 = None
        #                         for item in val.iter('field'):
        #                             if item.get('name') == 'lte-rrc.a5_Threshold1':
        #                                 for item2 in item.iter('field'):
        #                                     if item2.get('name') == 'lte-rrc.threshold_RSRP':
        #                                         threshold1 = int(item2.get('show'))-140
        #                                         break
        #                                     if item2.get('name') == 'lte-rrc.threshold_RSRQ':
        #                                         threshold1 = (int(item2.get('show'))-40)/2.0
        #                                         break
        #                             if item.get('name') == 'lte-rrc.a5_Threshold2':
        #                                 for item2 in item.iter('field'):
        #                                     if item2.get('name') == 'lte-rrc.threshold_RSRP':
        #                                         threshold2 = int(item2.get('show'))-140
        #                                         break
        #                                     if item2.get('name') == 'lte-rrc.threshold_RSRQ':
        #                                         threshold2 = (int(item2.get('show'))-40)/2.0
        #                                         break
        #                         new_info["event_list"].append({"event_type":"a5","threshold1":threshold1,"threshold2":threshold2})

        #                     if val.get('name') == 'lte-rrc.eventB2_element':

        #                         threshold1 = None
        #                         threshold2 = None
        #                         for item in val.iter('field'):
        #                             if item.get('name') == 'lte-rrc.b2_Threshold1':
        #                                 for item2 in item.iter('field'):
        #                                     if item2.get('name') == 'lte-rrc.threshold_RSRP':
        #                                         threshold1 = int(item2.get('show'))-140
        #                                         break
        #                                     if item2.get('name') == 'lte-rrc.threshold_RSRQ':
        #                                         threshold1 = (int(item2.get('show'))-40)/2.0
        #                                         break
        #                             if item.get('name') == 'lte-rrc.b2_Threshold2':
        #                                 for item2 in item.iter('field'):
        #                                     if item2.get('name') == 'lte-rrc.threshold_RSRP':
        #                                         threshold2 = int(item2.get('show'))-140
        #                                         break
        #                                     if item2.get('name') == 'lte-rrc.threshold_RSRQ':
        #                                         threshold2 = (int(item2.get('show'))-40)/2.0
        #                                         break
        #                                     if item2.get('name') == 'lte-rrc.utra_RSCP':
        #                                         threshold2 = int(item2.get('show'))-115
        #                                         break
        #                         new_info["event_list"].append({"event_type":"b2","threshold1":threshold1,"threshold2":threshold2})

        #                 self.__current_LTE_reportConfig.append(new_info)

        #             #Add a LTE measurement report config
        #             if field.get('name') == "lte-rrc.MeasIdToAddMod_element":
        #                 field_val = {}
        #                 for val in field.iter('field'):
        #                     field_val[val.get('name')] = val.get('show')

        #                 meas_id = int(field_val['lte-rrc.measId'])
        #                 obj_id = int(field_val['lte-rrc.measObjectId'])
        #                 config_id = int(field_val['lte-rrc.reportConfigId'])

        #                 new_info = {"measId":meas_id,"measObjectId":obj_id,"reportConfigId":config_id}

        #                 self.__current_LTE_measurementReportConfig.append(new_info)

        self.__last_lte_rrc_freq = log_item["Freq"]

