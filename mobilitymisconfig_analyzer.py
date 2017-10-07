#!/usr/bin/python
# Filename: mobilitymisconfig_analyzer.py
"""


Author: Jiayao Li
"""

from mobile_insight.analyzer.analyzer import *

import xml.etree.ElementTree as ET
import datetime
import re

__all__ = ["MobilityMisconfigAnalyzer"]

#Q-offset range mapping (6.3.4, TS36.331)
q_offset_range = {
    0:-24, 1:-22, 2:-20, 3:-18, 4:-16, 5:-14,
    6:-12, 7:-10, 8:-8, 9:-6, 10:-5, 11:-4,
    12:-3, 13:-2, 14:-1, 15:0, 16:1, 17:2,
    18:3, 19:4, 20:5, 21:6, 22:8, 23:10, 24:12,
    25:14, 26:16, 27:18, 28:20, 29:22, 30:24
}

class Span(object):
    def __init__(self, start, end, **additional_info):
        self.start = start
        self.end = end
        for k, v in additional_info.items():
            setattr(self, k, v)

    def __repr__(self):
        s = "<start=%s, end=%s" % (repr(self.start), repr(self.end))
        for k, v in vars(self).items():
            if k not in {"start", "end"}:
                s += ", %s=%s" % (k, repr(v))
        s += ">"
        return s


def in_span(service_log):
    return len(service_log) > 0 and service_log[-1].end is None

def start_span(service_log, log_item, **additional_info):
    if not in_span(service_log):
        service_log.append(Span(log_item["timestamp"], None, **additional_info))

def end_span(service_log, log_item):
    if in_span(service_log):
        service_log[-1].end = log_item["timestamp"]

#-----------------------------------------------------------------------------

class MobilityMisconfigAnalyzer(Analyzer):
    """
    Analyze the MobilityMisconfig of the phone.
    """

    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__filter)

        self.__umts_normal_service = []
        self.__umts_plmn_search = []
        self.__umts_attach = []
        self.__umts_lu = []
        self.__umts_rau = []
        self.__lte_normal_service = []
        self.__lte_plmn_search = []
        self.__lte_attach = []
        self.__lte_tau = []
        self.__lte_tau_qos_info = []
        self.__lte_cell_resel_to_umts_config = []
        self.__lte_drx_config = []
        self.__lte_tdd_config = []

        self.__last_normal_service = ""
        self.__last_lte_rrc_freq = 0
        self.__last_valid_timestamp = None
        self.__last_wcdma_rrc_mib_info = None
        self.__n_lte_rrc_reconfig = 0

        self.__lte_mobility_misconfig_serving_cell_dict = {}
        self.__3g_mobility_misconfig_serving_cell_dict = {}


    def set_source(self,source):
        """
        Set the trace source. Enable the WCDMA RRC messages.

        :param source: the trace source.
        :type source: trace collector
        """
        Analyzer.set_source(self,source)

        source.enable_log("CDMA_Paging_Channel_Message")

        # source.enable_log("1xEV_Signaling_Control_Channel_Broadcast")

        source.enable_log("UMTS_NAS_GMM_State")
        source.enable_log("UMTS_NAS_MM_State")
        source.enable_log("UMTS_NAS_OTA_Packet")
        source.enable_log("WCDMA_RRC_Serv_Cell_Info")
        source.enable_log("WCDMA_RRC_OTA_Packet")

        source.enable_log("LTE_RRC_OTA_Packet")
        # source.enable_log("LTE_RRC_MIB_Message_Log_Packet")
        source.enable_log("LTE_RRC_Serv_Cell_Info")
        source.enable_log("LTE_NAS_EMM_State")
        source.enable_log("LTE_NAS_ESM_OTA_Incoming_Packet")
        source.enable_log("LTE_NAS_ESM_OTA_Outgoing_Packet")
        source.enable_log("LTE_NAS_EMM_OTA_Incoming_Packet")
        source.enable_log("LTE_NAS_EMM_OTA_Outgoing_Packet")


    def get_umts_normal_service_log(self):
        """
        Return the normal service time span of WCDMA network.
        """
        return self.__umts_normal_service

    def get_umts_plmn_search_log(self):
        """
        Return the PLMN search time span of WCDMA network.
        """
        return self.__umts_plmn_search

    def get_umts_attach_log(self):
        """
        Return the attach time span of WCDMA network.
        """
        return self.__umts_attach

    def get_umts_lu_log(self):
        """
        Return the Location Update time span of WCDMA network.
        """
        return self.__umts_lu

    def get_umts_rau_log(self):
        """
        Return the RAU (Routing Area Update) time span of WCDMA network.
        """
        return self.__umts_rau

    def get_lte_normal_service_log(self):
        """
        Return the normal service time span of LTE network.
        """
        return self.__lte_normal_service

    def get_lte_plmn_search_log(self):
        """
        Return the PLMN search time span of LTE network, as well as how long the
        phone spends on searching each cell.
        """
        return self.__lte_plmn_search

    def get_lte_attach_log(self):
        """
        Return the attach time span of LTE network.
        """
        return self.__lte_attach

    def get_lte_tau_log(self):
        """
        Return the TAU (Tracking Area Upate) time span of LTE network.
        """
        return self.__lte_tau

    def get_lte_tau_qos_info(self):
        return self.__lte_tau_qos_info

    def get_lte_cell_resel_to_umts_config(self):
        return self.__lte_cell_resel_to_umts_config

    def get_lte_drx_config(self):
        return self.__lte_drx_config

    def get_lte_tdd_config(self):
        return self.__lte_tdd_config

    def get_n_lte_rrc_reconfig(self):
        return self.__n_lte_rrc_reconfig

    def get_lte_mobility_misconfig_serving_cell_dict(self):
        return self.__lte_mobility_misconfig_serving_cell_dict

    def get_3g_mobility_misconfig_serving_cell_dict(self):
        return self.__3g_mobility_misconfig_serving_cell_dict


    def __filter(self, event):
        log_item = event.data.decode()
        decoded_event = Event(event.timestamp, event.type_id, log_item)

        # Deal with out-of-order timestamps
        this_ts = log_item["timestamp"]
        if this_ts.year != 1980:    # Ignore undefined timestamp
            if self.__last_valid_timestamp:
                sec = (this_ts - self.__last_valid_timestamp).total_seconds()
                if sec >= 1200 or sec <= -120:
                    self.__pause(self.__last_valid_timestamp)
            self.__last_valid_timestamp = this_ts

        if event.type_id == "CDMA_Paging_Channel_Message":
            self.__callback_cdma_paging_chann(decoded_event)
        elif event.type_id == "1xEV_Signaling_Control_Channel_Broadcast":
            self.__callback_1xev_broadcast_chann(decoded_event)
        elif event.type_id == "UMTS_NAS_MM_State":
            # Ignore
            pass
        elif event.type_id == "UMTS_NAS_GMM_State":
            self.__callback_umts_nas_gmm(decoded_event)
        elif event.type_id == "UMTS_NAS_OTA_Packet":
            self.__callback_umts_nas(decoded_event)
        elif event.type_id == "WCDMA_RRC_Serv_Cell_Info":
            self.__callback_wcdma_cell_id(decoded_event)
        elif event.type_id == "WCDMA_RRC_OTA_Packet":
            if "Msg" in log_item:
                self.__callback_wcdma_rrc_ota(decoded_event)
        elif event.type_id == "LTE_NAS_EMM_State":
            self.__callback_lte_nas_emm(decoded_event)
        elif event.type_id.startswith("LTE_NAS_ESM_Plain_OTA_") or event.type_id.startswith("LTE_NAS_EMM_Plain_OTA_"):
            self.__callback_lte_nas(decoded_event)
        elif event.type_id == "LTE_RRC_OTA_Packet":
            self.__callback_lte_rrc_ota(decoded_event)
        elif event.type_id == "LTE_RRC_Serv_Cell_Info":
            self.__callback_lte_rrc_serv_cell_info(decoded_event)


    def __pause(self, last_valid_timestamp):
        log_item = {"timestamp": last_valid_timestamp}

        self.__last_normal_service = ""
        end_span(self.__umts_normal_service, log_item)
        end_span(self.__lte_normal_service, log_item)
        self.__end_plmn_search(log_item)


    def __start_plmn_search(self, network, last_normal_service, log_item):
        if network == "LTE":
            start_span(self.__lte_plmn_search, log_item,
                        search_log=[],
                        from_where=last_normal_service,
                        network=network)
        elif network == "UMTS":
            start_span(self.__umts_plmn_search, log_item,
                        search_log=[],
                        from_where=last_normal_service,
                        network=network)
        else:
            raise RuntimeError("wtf")


    def __add_plmn_search_cell(self, cell_id, log_item):
        if in_span(self.__umts_plmn_search):
            l = self.__umts_plmn_search[-1].search_log
            if in_span(l) and l[-1].cell_id != cell_id:
                end_span(l, log_item)
                start_span(l, log_item, cell_id=cell_id)
            elif not in_span(l):
                start_span(l, log_item, cell_id=cell_id)
        if in_span(self.__lte_plmn_search):
            l = self.__lte_plmn_search[-1].search_log
            if in_span(l) and l[-1].cell_id != cell_id:
                end_span(l, log_item)
                start_span(l, log_item, cell_id=cell_id)
            elif not in_span(l):
                start_span(l, log_item, cell_id=cell_id)


    def __end_plmn_search(self, log_item):
        # end potential WCDMA PLMN search
        if in_span(self.__umts_plmn_search):
            end_span(self.__umts_plmn_search[-1].search_log, log_item)
            end_span(self.__umts_plmn_search, log_item)
        # end potential LTE PLMN search
        if in_span(self.__lte_plmn_search):
            end_span(self.__lte_plmn_search[-1].search_log, log_item)
            end_span(self.__lte_plmn_search, log_item)


    def __callback_cdma_paging_chann(self, event):
        log_item = event.data

        s = "CDMA"
        self.__add_plmn_search_cell(s, log_item)


    def __callback_1xev_broadcast_chann(self, event):
        log_item = event.data

        s = "1xEV/B%(Band)d-%(HSTR)d" % log_item
        self.__add_plmn_search_cell(s, log_item)


    def __callback_umts_nas_gmm(self, event):
        log_item = event.data

        last_normal_service = self.__last_normal_service

        # Normal service span
        if log_item["GMM State"] == "GMM_REGISTERED" and log_item["GMM Substate"] == "GMM_NORMAL_SERVICE":
            start_span(self.__umts_normal_service, log_item)
            # This msg does not provide detailed information about the current
            # serving provider, so if we have extracted more detailed information
            # from other msgs, we do not update __last_normal_service.
            if not self.__last_normal_service:
                self.__last_normal_service = "WCDMA/Unknown"
        elif {log_item["GMM State"], log_item["GMM Substate"]} & {"Unknown", "Undefined"}:
            pass
        else:
            end_span(self.__umts_normal_service, log_item)

        # PLMN service span
        if log_item["GMM Substate"] == "GMM_PLMN_SEARCH":
            self.__start_plmn_search("UMTS", last_normal_service, log_item)
        elif log_item["GMM State"] == "GMM_REGISTERED" and log_item["GMM Substate"] == "GMM_NORMAL_SERVICE":
            self.__end_plmn_search(log_item)


    def __callback_wcdma_rrc_ota(self, event):
        log_item = event.data
        log_xml = ET.fromstring(log_item["Msg"])

        self.__last_3g_newMsg_mcc = None
        self.__last_3g_newMsg_mnc = None
        self.__last_3g_newMsg_cellId = None


        mib = None
        sib3 = None
        for val in log_xml.iter("field"):
            if val.get("name") == "rrc.MasterInformationBlock_element":
                mib = val
            if val.get("name") == "rrc.SysInfoType3_element":
                sib3 = val

        if mib is not None:
            self.__callback_wcdma_rrc_ota_mib(event, mib)

        if sib3 is not None:
            self.__callback_wcdma_rrc_ota_sib3(event, sib3)

        # print (self.__last_3g_newMsg_cellId,self.__last_3g_newMsg_mcc,self.__last_3g_newMsg_mnc)
        try:
            self.__last_3g_cellId
        except AttributeError:
            # print "not initialized"
            return

        if self.__last_3g_newMsg_cellId is not None:
            if self.__last_3g_newMsg_cellId != self.__last_3g_cellId:
                # print "Something changed"
                del self.__last_3g_plmn
                del self.__last_3g_cellId
                del self.__last_3g_LAC_id
                del self.__last_3g_RAC_id
                del self.__last_3g_UtraDLFreq
                return
        if self.__last_3g_newMsg_mcc is not None:
            temp = self.__last_3g_newMsg_mcc + '-' + self.__last_3g_newMsg_mnc
            if temp != self.__last_3g_plmn:
                # print "Something changed"
                del self.__last_3g_plmn
                del self.__last_3g_cellId
                del self.__last_3g_LAC_id
                del self.__last_3g_RAC_id
                del self.__last_3g_UtraDLFreq
                return

        #----------------------------------------------------------------------
        for field in log_xml.iter('field'):
            if field.get('name') == "rrc.utra_ServingCell_element":
                field_val = {}

                #Default value setting
                #FIXME: set default to those in TS25.331
                field_val['rrc.priority'] = None    #mandatory
                field_val['rrc.threshServingLow'] = None    #mandatory
                field_val['rrc.s_PrioritySearch1'] = None    #mandatory
                field_val['rrc.s_PrioritySearch2'] = 0    #optional

                for val in field.iter('field'):
                    field_val[val.get('name')] = val.get('show')

                if "utra_ServingCell" not in self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId,self.__last_3g_UtraDLFreq)].keys():
                    self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId,self.__last_3g_UtraDLFreq)]["utra_ServingCell"] = []

                info3g = {\
                        "priority":field_val['rrc.priority'],\
                        "threshServingLow":int(field_val['rrc.threshServingLow'])*2,\
                        "s_PrioritySearch1":int(field_val['rrc.s_PrioritySearch1'])*2,\
                        "s_PrioritySearch2":field_val['rrc.s_PrioritySearch2']\
                        }
                if info3g not in self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId,self.__last_3g_UtraDLFreq)]["utra_ServingCell"]:
                    self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId,self.__last_3g_UtraDLFreq)]["utra_ServingCell"].append(info3g)

            #intra-freq info
            if field.get('name') == "rrc.cellSelectReselectInfo_element":
                field_val = {}

                #default value based on TS25.331
                field_val['rrc.s_Intrasearch'] = 0
                field_val['rrc.s_Intersearch'] = 0
                field_val['rrc.q_RxlevMin'] = None #mandatory
                field_val['rrc.q_QualMin'] = None #mandatory
                field_val['rrc.q_Hyst_l_S'] = None #mandatory
                field_val['rrc.t_Reselection_S'] = None #mandatory
                field_val['rrc.q_HYST_2_S'] = None #optional, default=q_Hyst_l_S
                field_val['rat_List'] = []

                # handle rrc.RAT_FDD_Info_element (p1530, TS25.331)
                # s-SearchRAT is the RAT-specific threshserv
                for val in field.iter('field'):
                    if val.get('name') == 'rrc.RAT_FDD_Info_element':
                        rat_info = {}
                        for item in val.iter('field'):
                            if item.get('name') == 'rrc.rat_Identifier':
                                rat_info[item.get('name')] = item.get('showname').split(': ')[1]
                            elif item.get("name") == "rrc.s_SearchRAT" or item.get("name") == "rrc.s_Limit_SearchRAT":
                                rat_info[item.get('name')] = int(item.get('show'))
                            elif item.get("name") == "rrc.s_HCS_RAT":
                                rat_info[item.get('name')] = int(item.get('show')) * 2
                        field_val['rat_List'].append(rat_info)
                    else:
                        field_val[val.get('name')] = val.get('show')

                #TODO: handle FDD and TDD

                #TS25.331: if qHyst-2s is missing, the default is qHyst-1s
                if not field_val['rrc.q_HYST_2_S']:
                    field_val['rrc.q_HYST_2_S'] = field_val['rrc.q_Hyst_l_S']

                if "cellSelectReselectInfo" not in self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId,self.__last_3g_UtraDLFreq)].keys():
                    self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId,self.__last_3g_UtraDLFreq)]["cellSelectReselectInfo"] = []

                info3g = {\
                        "t_Reselection_S":field_val['rrc.t_Reselection_S'],\
                        "q_RxlevMin":int(field_val['rrc.q_RxlevMin'])*2,\
                        "q_QualMin":int(field_val['rrc.q_QualMin']),\
                        "s_Intersearch":int(field_val['rrc.s_Intersearch'])*2,\
                        "s_Intrasearch":int(field_val['rrc.s_Intrasearch'])*2,\
                        "q_Hyst_1_S":int(field_val['rrc.q_Hyst_l_S'])*2,\
                        "q_HYST_2_S":int(field_val['rrc.q_HYST_2_S'])*2,\
                        "maxAllowedUL_Tx_Power":int(field_val['rrc.maxAllowedUL_TX_Power']),\
                        "rat_List":field_val['rat_List']\
                        }
                if info3g not in self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId,self.__last_3g_UtraDLFreq)]["cellSelectReselectInfo"]:
                    self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId,self.__last_3g_UtraDLFreq)]["cellSelectReselectInfo"].append(info3g)


            #inter-RAT cell info (LTE)
            if field.get('name') == "rrc.EUTRA_FrequencyAndPriorityInfo_element":
                field_val = {}

                #FIXME: set to the default value based on TS36.331
                field_val['rrc.earfcn'] = None
                #field_val['lte-rrc.t_ReselectionEUTRA'] = None
                field_val['rrc.priority'] = None
                field_val['rrc.qRxLevMinEUTRA'] = -140
                #field_val['lte-rrc.p_Max'] = None
                field_val['rrc.threshXhigh'] = None
                field_val['rrc.threshXlow'] = None

                for val in field.iter('field'):
                    field_val[val.get('name')] = val.get('show')

                if "EUTRA_FrequencyAndPriorityInfo" not in self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId,self.__last_3g_UtraDLFreq)].keys():
                    self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId,self.__last_3g_UtraDLFreq)]["EUTRA_FrequencyAndPriorityInfo"] = []

                info3g = {\
                        "earfcn":field_val['rrc.earfcn'],\
                        "qRxLevMinEUTRA":int(field_val['rrc.qRxLevMinEUTRA'])*2,\
                        "priority":int(field_val['rrc.priority']),\
                        "threshXhigh":int(field_val['rrc.threshXhigh'])*2,\
                        "threshXlow":int(field_val['rrc.threshXlow'])*2,\
                        }
                if info3g not in self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId,self.__last_3g_UtraDLFreq)]["EUTRA_FrequencyAndPriorityInfo"]:
                    self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId,self.__last_3g_UtraDLFreq)]["EUTRA_FrequencyAndPriorityInfo"].append(info3g)

            #-------------3G-Measurement Report Event--------------------------

            if field.get('name') == "rrc.e1a_element":
                field_val = {}

                for val in field.iter('field'):
                    if val.get('name') == field.get('name'):
                        continue
                    if len((val.get('showname')).split(' ')) == 3 and (val.get('showname')).split(' ')[2][0] == '(':
                        field_val[val.get('name')] = (val.get('showname')).split(' ')[1]
                    else:
                        field_val[val.get('name')] = val.get('show')

                if "event: e1a" not in self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId, self.__last_3g_UtraDLFreq)].keys():
                    self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId,self.__last_3g_UtraDLFreq)]["event: e1a"] = []
                if field_val not in self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId,self.__last_3g_UtraDLFreq)]["event: e1a"]:
                    self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId,self.__last_3g_UtraDLFreq)]["event: e1a"].append(field_val)


            if field.get('name') == "rrc.e1b_element":
                field_val = {}

                for val in field.iter('field'):
                    if val.get('name') == field.get('name'):
                        continue
                    if len((val.get('showname')).split(' ')) == 3 and (val.get('showname')).split(' ')[2][0] == '(':
                        field_val[val.get('name')] = (val.get('showname')).split(' ')[1]
                    else:
                        field_val[val.get('name')] = val.get('show')

                if "event: e1b" not in self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId, self.__last_3g_UtraDLFreq)].keys():
                    self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId,self.__last_3g_UtraDLFreq)]["event: e1b"] = []

                if field_val not in self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId,self.__last_3g_UtraDLFreq)]["event: e1b"]:
                    self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId,self.__last_3g_UtraDLFreq)]["event: e1b"].append(field_val)

            if field.get('name') == "rrc.e1c_element":
                field_val = {}

                for val in field.iter('field'):
                    if val.get('name') == field.get('name'):
                        continue
                    if len((val.get('showname')).split(' ')) == 3 and (val.get('showname')).split(' ')[2][0] == '(':
                        field_val[val.get('name')] = (val.get('showname')).split(' ')[1]
                    else:
                        field_val[val.get('name')] = val.get('show')

                if "event: e1c" not in self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId, self.__last_3g_UtraDLFreq)].keys():
                    self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId,self.__last_3g_UtraDLFreq)]["event: e1c"] = []

                if field_val not in self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId,self.__last_3g_UtraDLFreq)]["event: e1c"]:
                    self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId,self.__last_3g_UtraDLFreq)]["event: e1c"].append(field_val)

            if field.get('name') == "rrc.e1d_element":
                field_val = {}

                for val in field.iter('field'):
                    if val.get('name') == field.get('name'):
                        continue
                    if len((val.get('showname')).split(' ')) == 3 and (val.get('showname')).split(' ')[2][0] == '(':
                        field_val[val.get('name')] = (val.get('showname')).split(' ')[1]
                    else:
                        field_val[val.get('name')] = val.get('show')

                if "event: e1d" not in self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId, self.__last_3g_UtraDLFreq)].keys():
                    self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId,self.__last_3g_UtraDLFreq)]["event: e1d"] = []

                if field_val not in self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId,self.__last_3g_UtraDLFreq)]["event: e1d"]:
                    self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId,self.__last_3g_UtraDLFreq)]["event: e1d"].append(field_val)

            if field.get('name') == "rrc.event2b_element":
                field_val = {}

                for val in field.iter('field'):
                    if val.get('name') == field.get('name'):
                        continue
                    if len((val.get('showname')).split(' ')) == 3 and (val.get('showname')).split(' ')[2][0] == '(':
                        field_val[val.get('name')] = (val.get('showname')).split(' ')[1]
                        # print val.get('name') + "|" + (val.get('showname')).split(' ')[1]
                    else:
                        field_val[val.get('name')] = val.get('show')
                        # print val.get('name') + "|" + val.get('showname')

                if "event: 2b" not in self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId, self.__last_3g_UtraDLFreq)].keys():
                    self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId,self.__last_3g_UtraDLFreq)]["event: 2b"] = []

                if field_val not in self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId,self.__last_3g_UtraDLFreq)]["event: 2b"]:
                    self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId,self.__last_3g_UtraDLFreq)]["event: 2b"].append(field_val)

            if field.get('name') == "rrc.event2d_element":
                field_val = {}

                for val in field.iter('field'):
                    if val.get('name') == field.get('name'):
                        continue
                    if len((val.get('showname')).split(' ')) == 3 and (val.get('showname')).split(' ')[2][0] == '(':
                        field_val[val.get('name')] = (val.get('showname')).split(' ')[1]
                        # print val.get('name') + "|" + (val.get('showname')).split(' ')[1]
                    else:
                        field_val[val.get('name')] = val.get('show')
                        # print val.get('name') + "|" + val.get('showname')

                if "event: 2d" not in self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId, self.__last_3g_UtraDLFreq)].keys():
                    self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId,self.__last_3g_UtraDLFreq)]["event: 2d"] = []

                if field_val not in self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId,self.__last_3g_UtraDLFreq)]["event: 2d"]:
                    self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId,self.__last_3g_UtraDLFreq)]["event: 2d"].append(field_val)

            if field.get('name') == "rrc.event2f_element":
                field_val = {}

                for val in field.iter('field'):
                    if val.get('name') == field.get('name'):
                        continue
                    if len((val.get('showname')).split(' ')) == 3 and (val.get('showname')).split(' ')[2][0] == '(':
                        field_val[val.get('name')] = (val.get('showname')).split(' ')[1]
                        # print val.get('name') + "|" + (val.get('showname')).split(' ')[1]
                    else:
                        field_val[val.get('name')] = val.get('show')
                        # print val.get('name') + "|" + val.get('showname')

                if "event: 2f" not in self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId, self.__last_3g_UtraDLFreq)].keys():
                    self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId,self.__last_3g_UtraDLFreq)]["event: 2f"] = []

                if field_val not in self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId,self.__last_3g_UtraDLFreq)]["event: 2f"]:
                    self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId,self.__last_3g_UtraDLFreq)]["event: 2f"].append(field_val)

    def __callback_wcdma_rrc_ota_mib(self, event, mib):
        log_item = event.data

        info = {"mcc": None, "mnc": None}
        for val in mib.iter("field"):
            if val.get("name") == "rrc.mcc":
                mcc = ""
                for digit in val.iter("field"):
                    if digit.get("name") == "rrc.Digit":
                        mcc += digit.get("show")
                info["mcc"] = mcc
                self.__last_3g_newMsg_mcc = mcc
            elif val.get("name") == "rrc.mnc":
                mnc = ""
                for digit in val.iter("field"):
                    if digit.get("name") == "rrc.Digit":
                        mnc += digit.get("show")
                info["mnc"] = mnc
                self.__last_3g_newMsg_mnc = mnc

        self.__last_wcdma_rrc_mib_info = info

    def __callback_wcdma_rrc_ota_sib3(self, event, sib3):
        log_item = event.data

        if not self.__last_wcdma_rrc_mib_info:
            return

        cell_id = ""
        for val in sib3.iter("field"):
            if val.get("name") == "rrc.cellIdentity":
                c = int(val.get("value"), base=16) / 16
                mcc = "%(mcc)s" %self.__last_wcdma_rrc_mib_info
                mnc = "%(mnc)s" %self.__last_wcdma_rrc_mib_info
                self.__last_3g_newMsg_cellId = int(val.get("value")[0:-1],16)
                cell_id = "WCDMA/%(mcc)s-%(mnc)s" % self.__last_wcdma_rrc_mib_info
                cell_id += "-%d" % c
                break

        if cell_id:
            self.__add_plmn_search_cell(cell_id, log_item)

    def __callback_umts_nas(self, event):
        log_item = event.data
        log_xml = ET.fromstring(log_item["Msg"])
        NasTypePattern = re.compile(r": (.*) \(0x[\da-fA-F]+\)$")

        nas_type = ""
        for val in log_xml.iter("field"):
            if val.get("name") in {"gsm_a.dtap.msg_mm_type", "gsm_a.dtap.msg_gmm_type", "gsm_a.dtap.msg_sm_type"}:
                s = val.get("showname")
                nas_type = re.findall(NasTypePattern, s)[0]
                break
        # print nas_type

        # WCDMA Attach
        if nas_type == "Attach Request":
            start_span(self.__umts_attach, log_item, request=nas_type, response=None)
        elif nas_type in {"Attach Complete", "Attach Reject"}:
            if in_span(self.__umts_attach):
                end_span(self.__umts_attach, log_item)
                self.__umts_attach[-1].response = nas_type

        # WCDMA Routing Area Update
        if nas_type == "Routing Area Update Request":
            start_span(self.__umts_rau, log_item, request=nas_type, response=None)
        elif nas_type in {"Routing Area Update Complete", "Routing Area Update Reject"}:
            if in_span(self.__umts_rau):
                end_span(self.__umts_rau, log_item)
                self.__umts_rau[-1].response = nas_type

        # WCDMA Location Update
        if nas_type == "Location Updating Request":
            start_span(self.__umts_lu, log_item, request=nas_type, response=None)
        elif nas_type in {"Location Updating Accept", "Location Updating Reject"}:
            if in_span(self.__umts_lu):
                end_span(self.__umts_lu, log_item)
                self.__umts_lu[-1].response = nas_type


    def __callback_wcdma_cell_id(self, event):
        log_item = event.data
        # print "[Haotian] wcdma_cell_id"
        # print log_item
        # print "[Haotian-end]"

        self.__last_normal_service = "WCDMA/%s" % log_item["PLMN"]
        self.__last_3g_plmn = log_item["PLMN"]
        self.__last_3g_UtraDLFreq = log_item["Download RF channel number"]
        self.__last_3g_cellId = log_item["Cell ID"]
        self.__last_3g_LAC_id = log_item["LAC"]
        self.__last_3g_RAC_id = log_item["RAC"]
        wcdma_cell_info = {"Cell ID":self.__last_3g_cellId,\
                "PLMN":self.__last_3g_plmn,\
                "UtraDLFreq":self.__last_3g_UtraDLFreq,\
                "LAC ID":self.__last_3g_LAC_id,\
                "RAC ID":self.__last_3g_RAC_id}
        # print (self.__last_3g_plmn,self.__last_3g_UtraDLFreq,self.__last_3g_cellId,self.__last_3g_LAC_id,self.__last_3g_RAC_id)
        if (self.__last_3g_cellId,self.__last_3g_UtraDLFreq) in self.__3g_mobility_misconfig_serving_cell_dict.keys():
            if wcdma_cell_info not in self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId,self.__last_3g_UtraDLFreq)]["3g_rrc_cerv_cell_info"]:
                self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId,self.__last_3g_UtraDLFreq)]["3g_rrc_cerv_cell_info"].append(wcdma_cell_info)
        else:
            self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId,self.__last_3g_UtraDLFreq)] = {}
            self.__3g_mobility_misconfig_serving_cell_dict[(self.__last_3g_cellId,self.__last_3g_UtraDLFreq)]["3g_rrc_cerv_cell_info"] = [wcdma_cell_info]

    def __callback_lte_nas_emm(self, event):
        log_item = event.data
        last_normal_service = self.__last_normal_service

        # Normal service span
        if log_item["EMM Substate"] == "EMM_REGISTERED_NORMAL_SERVICE":
            start_span(self.__lte_normal_service, log_item)
            self.__last_normal_service = "LTE/%s" % log_item["PLMN"]
        elif log_item["EMM Substate"] in {"Unknown", "Undefined"}:
            pass
        else:
            end_span(self.__lte_normal_service, log_item)
            # if self.__last_normal_service.startswith("LTE"):
            #     self.__last_normal_service = ""

        # PLMN service span
        if log_item["EMM Substate"] in {"EMM_DEREGISTERED_PLMN_SEARCH", "EMM_REGISTERED_PLMN_SEARCH"}:
            self.__start_plmn_search("LTE", last_normal_service, log_item)
        elif log_item["EMM Substate"] == "EMM_REGISTERED_NORMAL_SERVICE":
            self.__end_plmn_search(log_item)


    def __callback_lte_nas(self, event):
        log_item = event.data
        log_xml = ET.fromstring(log_item["Msg"])
        NasTypePattern = re.compile(r": (.*) \(0x[\da-fA-F]+\)")

        nas_type = ""
        for val in log_xml.iter("field"):
            if val.get("name") in {"nas_eps.nas_msg_emm_type", "nas_eps.nas_msg_esm_type"}:
                s = val.get("showname")
                nas_type = re.findall(NasTypePattern, s)[0]
                break
        # print nas_type

        # LTE Attach
        if nas_type in {"Attach request"}:
            start_span(self.__lte_attach, log_item, request=nas_type, response=None)
        elif nas_type in {"Attach complete", "Attach reject"}:
            if in_span(self.__lte_attach):
                end_span(self.__lte_attach, log_item)
                self.__lte_attach[-1].response = nas_type

        # LTE Tracking Area Update
        if nas_type in {"Tracking area update request"}:
            start_span(self.__lte_tau, log_item, request=nas_type, response=None)
        elif nas_type in {"Tracking area update complete", "Tracking area update reject"}:
            if in_span(self.__lte_tau):
                end_span(self.__lte_tau, log_item)
                self.__lte_tau[-1].response = nas_type

        if nas_type == "Activate default EPS bearer context request":
            keys = ("qci", "delay_class", "traffic_class", "delivery_err_sdu", "traffic_hand_pri", "traffic_hand_pri", "traffic_hand_pri", "apn_ambr_dl_ext", "apn_ambr_ul_ext", "apn_ambr_dl_ext2", "apn_ambr_ul_ext2")
            info = dict([(k, None) for k in keys])
            Pattern1 = re.compile(r": (.*) \((\d+)\)$")
            Pattern2 = re.compile(r": (\d+ \w+)$")
            for val in log_xml.iter("field"):
                s = val.get("showname")
                if val.get("name") == "nas_eps.emm.qci":
                    info["qci"] = re.findall(Pattern1, s)[0][0]
                elif val.get("name") == "gsm_a.gm.sm.qos.delay_cls":
                    info["delay_class"] = re.findall(Pattern1, s)[0][0]
                elif val.get("name") == "gsm_a.gm.sm.qos.traffic_cls":
                    info["traffic_class"] = "%s (%s)" % re.findall(Pattern1, s)[0]
                elif val.get("name") == "gsm_a.gm.sm.qos.del_of_err_sdu":
                    info["delivery_err_sdu"] = "%s (%s)" % re.findall(Pattern1, s)[0]
                elif val.get("name") == "gsm_a.gm.sm.qos.traff_hdl_pri":
                    info["traffic_hand_pri"] = "%s (%s)" % re.findall(Pattern1, s)[0]
                elif val.get("name") == "gsm_a.gm.sm.qos.max_bitrate_downl_ext":
                    info["traffic_hand_pri"] = "%s (%s)" % re.findall(Pattern1, s)[0]
                elif val.get("name") == "gsm_a.gm.sm.qos.max_bitrate_upl_ext":
                    info["traffic_hand_pri"] = "%s (%s)" % re.findall(Pattern1, s)[0]
                elif val.get("name") == "nas_eps.emm.apn_ambr_dl_ext":
                    info["apn_ambr_dl_ext"] = re.findall(Pattern2, s)[0]
                elif val.get("name") == "nas_eps.emm.apn_ambr_ul_ext":
                    info["apn_ambr_ul_ext"] = re.findall(Pattern2, s)[0]
                elif val.get("name") == "nas_eps.emm.apn_ambr_dl_ext2":
                    info["apn_ambr_dl_ext2"] = re.findall(Pattern2, s)[0]
                elif val.get("name") == "nas_eps.emm.apn_ambr_ul_ext2":
                    info["apn_ambr_ul_ext2"] = re.findall(Pattern2, s)[0]
            info["last_lte_rrc_freq"] = self.__last_lte_rrc_freq
            self.__lte_tau_qos_info.append(info)


    def __callback_lte_rrc_ota(self, event):
        log_item = event.data
        log_xml = ET.fromstring(log_item["Msg"])

        is_sib1 = False
        is_sib3 = False
        is_sib4 = False
        is_sib5 = False
        is_sib6 = False
        is_sib8 = False
        is_rrc_conn_reconfig = False

        CellID = log_item["Physical Cell ID"]
        DLFreq = log_item["Freq"]
        if (CellID,DLFreq) not in self.__lte_mobility_misconfig_serving_cell_dict.keys():
            self.__lte_mobility_misconfig_serving_cell_dict[(CellID,DLFreq)] = {}

        self.__last_CellID = CellID
        self.__last_DLFreq = DLFreq

        cell_info = {"plmn": None, "tac": None, "cell_id": None}
        if log_item["PDU Number"] == 2 or log_item["PDU Number"] == 9: # BCCH_DL_SCH, orignal 2
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
                elif val.get("name") == "lte-rrc.sib8_element":
                    is_sib8 = True

                elif val.get("name") == "lte-rrc.plmn_Identity_element":
                    mcc_mnc = ""
                    for digit in val.iter("field"):
                        if digit.get("name") == "lte-rrc.MCC_MNC_Digit":
                            mcc_mnc += digit.get("show")
                    cell_info["plmn"] = mcc_mnc[0:3] + "-" + mcc_mnc[3:]
                elif val.get("name") == "lte-rrc.trackingAreaCode":
                    cell_info["tac"] = int(val.get("value"), base=16)
                elif val.get("name") == "lte-rrc.cellIdentity":
                    cell_info["cell_id"] = int(val.get("value"), base=16) / 16

            if cell_info['cell_id'] != None:
                if "plmn_Identity_element" in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)].keys():
                    if cell_info not in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["plmn_Identity_element"]:
                        self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["plmn_Identity_element"].append(cell_info)
                else:
                    self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["plmn_Identity_element"] = [cell_info]

        elif log_item["PDU Number"] == 6 or log_item["PDU Number"] == 13: # LTE-RRC_DL_DCCH
            for val in log_xml.iter("field"):
                if val.get("name") == "lte-rrc.rrcConnectionReconfiguration_element":
                    is_rrc_conn_reconfig = True
                    break

        elif log_item["PDU Number"] == 8 or log_item["PDU Number"] == 15: # UL_DCCH
            for val in log_xml.iter("field"):
                if val.get("name") == "lte-rrc.measurementReport_r8_element":
                    field_val = {}
                    field_val["lte-rrc.measId"] = None
                    field_val["lte-rrc.rsrpResult"] = None
                    field_val["lte-rrc.rsrqResult"] = None
                    for attr in val.iter("field"):
                        field_val[attr.get("name")] = attr.get("show")
                    info = {"lte-rrc.measId":field_val["lte-rrc.measId"],\
                            "lte-rrc.rsrpResult":int(field_val["lte-rrc.rsrpResult"])-140,\
                            "lte-rrc.rsrqResult":(int(field_val["lte-rrc.rsrqResult"])-40)/2.0}
                    try:
                        self.__last_CellID
                    except AttributeError:
                        pass
                    else:
                        if "lte_rrc_measurement_report" not in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID, self.__last_DLFreq)]:
                            self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["lte_rrc_measurement_report"] = []
                        if info not in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["lte_rrc_measurement_report"]:
                            self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["lte_rrc_measurement_report"].append(info)
                    break

        if is_sib1 or is_sib3 or is_sib4 or is_sib5 or is_sib6 or is_sib8 or is_rrc_conn_reconfig:
            Pattern1 = re.compile(r": (.*) \([-\d]+\)$")
            Pattern2 = re.compile(r": (.*)$")

        if is_sib1:
            s = "LTE/%(plmn)s-%(tac)d-%(cell_id)d" % cell_info
            self.__add_plmn_search_cell(s, log_item)
            info = {"subframeAssignment": None,
                    "specialSubframePatterns": None,
                    "si_WindowLength": None,
                    "systemInfoValueTag": None
                    }
            for attr in log_xml.iter("field"):
                ss = attr.get("showname")
                if attr.get("name") in ("lte-rrc.subframeAssignment", "lte-rrc.specialSubframePatterns", "lte-rrc.si_WindowLength"):
                    info[attr.get("name")[8:]] = re.findall(Pattern1, ss)[0]
                elif attr.get("name") == "lte-rrc.systemInfoValueTag":
                    info[attr.get("name")[8:]] = re.findall(Pattern2, ss)[0]
            info["lte_rrc_freq"] = log_item["Freq"]
            self.__lte_tdd_config.append(info)

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
                        self.__last_CellID
                    except AttributeError:
                        pass
                    else:
                        if "[sib3]cellReselectionInfoCommon_element" in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)].keys():
                            if info not in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["[sib3]cellReselectionInfoCommon_element"]:
                                self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["[sib3]cellReselectionInfoCommon_element"].append(info)
                        else:
                            self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["[sib3]cellReselectionInfoCommon_element"] = [info]
                if val.get("name") == "lte-rrc.cellReselectionServingFreqInfo_element":
                    info = dict()
                    for attr in val.iter("field"):
                        s = attr.get("showname")
                        if attr.get("name") in ("lte-rrc.s_NonIntraSearch", "lte-rrc.threshServingLow"):
                            info[attr.get("name")[8:]] = re.findall(Pattern1, s)[0]
                        if attr.get("name") in ("lte-rrc.cellReselectionPriority"):
                            info[attr.get("name")[8:]] = re.findall(Pattern2, s)[0]
                    try:
                        self.__last_CellID
                    except AttributeError:
                        pass
                    else:
                        if "[sib3]cellReselectionServingFreqInfo_element" in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)].keys():
                            if info not in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["[sib3]cellReselectionServingFreqInfo_element"]:
                                self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["[sib3]cellReselectionServingFreqInfo_element"].append(info)
                        else:
                            self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["[sib3]cellReselectionServingFreqInfo_element"] = [info]
                if val.get("name") == "lte-rrc.intraFreqCellReselectionInfo_element":
                    info = dict()
                    for attr in val.iter("field"):
                        s = attr.get("showname")
                        if attr.get("name") in ("lte-rrc.q_RxLevMin", "lte-rrc.s_IntraSearch"):
                            info[attr.get("name")[8:]] = re.findall(Pattern1, s)[0]
                        if attr.get("name") in ("lte-rrc.p_Max", "lte-rrc.t_ReselectionEUTRA"):
                            info[attr.get("name")[8:]] = re.findall(Pattern2, s)[0]
                    try:
                        self.__last_CellID
                    except AttributeError:
                        pass
                    else:
                        if "[sib3]intraFreqCellReselectionInfo_element" in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)].keys():
                            if info not in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["[sib3]intraFreqCellReselectionInfo_element"]:
                                self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["[sib3]intraFreqCellReselectionInfo_element"].append(info)
                        else:
                            self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["[sib3]intraFreqCellReselectionInfo_element"] = [info]

        if is_sib4:
            for val in log_xml.iter("field"):
                if val.get("name") == "lte-rrc.PhysCellIdRange_element":
                    info = dict()
                    # Iter over all attrs
                    for attr in val.iter("field"):
                        s = attr.get("showname")
                        if attr.get("name") in ("lte-rrc.start"):
                            info[attr.get("name")[8:]] = re.findall(Pattern2, s)[0]
                    try:
                        self.__last_CellID
                    except AttributeError:
                        pass
                    else:
                        if "[sib4]intraFreqBlackCellList" in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)].keys():
                            if info not in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["[sib4]intraFreqBlackCellList"]:
                                self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["[sib4]intraFreqBlackCellList"].append(info)
                        else:
                            self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["[sib4]intraFreqBlackCellList"] = [info]

        if is_sib5:
            for val in log_xml.iter("field"):
                if val.get("name") == "lte-rrc.InterFreqCarrierFreqInfo_element":
                    info = dict()
                    # Iter over all attrs
                    for attr in val.iter("field"):
                        s = attr.get("showname")
                        if attr.get("name") in ("lte-rrc.q_RxLevMin", "lte-rrc.threshX_High", "lte-rrc.threshX_Low", "lte-rrc.allowedMeasBandwidth"):
                            info[attr.get("name")[8:]] = re.findall(Pattern1, s)[0]
                        elif attr.get("name") in ("lte-rrc.dl_CarrierFreq", "lte-rrc.p_Max", "lte-rrc.t_ReselectionEUTRA", "lte-rrc.cellReselectionPriority"):
                            info[attr.get("name")[8:]] = re.findall(Pattern2, s)[0]
                    try:
                        self.__last_CellID
                    except AttributeError:
                        pass
                    else:
                        if "[sib5]InterFreqCarrierFreqInfo_element" in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)].keys():
                            if info not in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["[sib5]InterFreqCarrierFreqInfo_element"]:
                                self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["[sib5]InterFreqCarrierFreqInfo_element"].append(info)
                        else:
                            self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["[sib5]InterFreqCarrierFreqInfo_element"] = [info]
                if val.get("name") == "lte-rrc.PhysCellIdRange_element":
                    info = dict()
                    # Iter over all attrs
                    for attr in val.iter("field"):
                        if attr.get("name") in ("lte-rrc.start"):
                            s = attr.get("showname")
                            info[attr.get("name")[8:]] = re.findall(Pattern2, s)[0]
                    try:
                        self.__last_CellID
                    except AttributeError:
                        pass
                    else:
                        if "[sib5]interFreqBlackCellList" in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)].keys():
                            if info not in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["[sib5]interFreqBlackCellList"]:
                                self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["[sib5]interFreqBlackCellList"].append(info)
                        else:
                            self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["[sib5]interFreqBlackCellList"] = [info]

        if is_sib6:
            # Iter over all CarrierFreqUTRA_FDD elements
            for val in log_xml.iter("field"):
                if val.get("name") == "lte-rrc.CarrierFreqUTRA_FDD_element":
                    info = dict()
                    # Iter over all attrs
                    for attr in val.iter("field"):
                        s = attr.get("showname")
                        if attr.get("name") in ("lte-rrc.threshX_High", "lte-rrc.threshX_Low", "lte-rrc.q_RxLevMin"):
                            info[attr.get("name")[8:]] = re.findall(Pattern1, s)[0]
                        elif attr.get("name") in ("lte-rrc.carrierFreq", "lte-rrc.cellReselectionPriority", "lte-rrc.p_MaxUTRA", "lte-rrc.q_QualMin"):
                            info[attr.get("name")[8:]] = re.findall(Pattern2, s)[0]
                    info["lte_rrc_freq"] = log_item["Freq"]
                    try:
                        self.__last_CellID
                    except AttributeError:
                        pass
                    else:
                        if "[sib6]CarrierFreqUTRA_FDD_element" in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)].keys():
                            if info not in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["[sib6]CarrierFreqUTRA_FDD_element"]:
                                self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["[sib6]CarrierFreqUTRA_FDD_element"].append(info)
                        else:
                            self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["[sib6]CarrierFreqUTRA_FDD_element"] = [info]
                    self.__lte_cell_resel_to_umts_config.append(info)

        if is_sib8:
            # Iter over all CarrierFreqUTRA_FDD elements
            for val in log_xml.iter("field"):
                if val.get("name") == "lte-rrc.BandClassInfoCDMA2000_element":
                    info = dict()
                    # Iter over all attrs
                    for attr in val.iter("field"):
                        s = attr.get("showname")
                        if attr.get("name") in ("lte-rrc.bandClass"):
                            info[attr.get("name")[8:]] = re.findall(Pattern1, s)[0]
                        elif attr.get("name") in ("lte-rrc.threshX_High", "lte-rrc.threshX_Low", "lte-rrc.cellReselectionPriority"):
                            info[attr.get("name")[8:]] = re.findall(Pattern2, s)[0]
                    try:
                        self.__last_CellID
                    except AttributeError:
                        pass
                    else:
                        if "[sib8]" in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)].keys():
                            if info not in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["[sib8]"]:
                                self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["[sib8]"].append(info)
                        else:
                            self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["[sib8]"] = [info]
                    self.__lte_cell_resel_to_umts_config.append(info)

        if is_rrc_conn_reconfig:
            # Find drx-Config setup
            for val in log_xml.iter("field"):
                if val.get("name") == "lte-rrc.drx_Config" and val.get("show") == "1":
                    info = {"shortDRX_Cycle": None, "drxShortCycleTimer": None}
                    for attr in val.iter("field"):
                        s = attr.get("showname")
                        if attr.get("name") in ("lte-rrc.onDurationTimer",
                                                "lte-rrc.drx_InactivityTimer",
                                                "lte-rrc.drx_RetransmissionTimer",
                                                "lte-rrc.shortDRX_Cycle"):
                            info[attr.get("name")[8:]] = re.findall(Pattern1, s)[0]
                        elif attr.get("name") == "lte-rrc.drxShortCycleTimer":
                            info[attr.get("name")[8:]] = re.findall(Pattern2, s)[0]
                    info["lte_rrc_freq"] = log_item["Freq"]
                    self.__lte_drx_config.append(info)
                    break
            self.__n_lte_rrc_reconfig += 1
            # extract configurations from RRCReconfiguration Message
            try:
                self.__last_CellID
            except AttributeError:
                pass
        #********************LTE Reconfiguration*******************************
            else:
                measobj_id = -1
                report_id = -1

                for field in log_xml.iter('field'):

                    if field.get('name') == "lte-rrc.measObjectId":
                        measobj_id = field.get('show')

                    if field.get('name') == "lte-rrc.reportConfigId":
                        report_id = field.get('show')

                    #Add a LTE measurement object
                    if field.get('name') == "lte-rrc.measObjectEUTRA_element":
                        field_val = {}

                        field_val['lte-rrc.carrierFreq'] = None
                        field_val['lte-rrc.offsetFreq'] = 0

                        for val in field.iter('field'):
                            field_val[val.get('name')] = val.get('show')

                        freq = int(field_val['lte-rrc.carrierFreq'])
                        offsetFreq = int(field_val['lte-rrc.offsetFreq'])
                        new_info = {}
                        new_info = {"measobj_id":measobj_id,"freq":freq,"offsetFreq":offsetFreq}
                        new_info["cell_list"] = []

                        #2nd round: handle cell individual offset
                        for val in field.iter('field'):
                            if val.get('name') == 'lte-rrc.CellsToAddMod_element':
                                cell_val = {}
                                for item in val.iter('field'):
                                    cell_val[item.get('name')] = item.get('show')

                                if 'lte-rrc.physCellId' in cell_val:
                                    cell_id = int(cell_val['lte-rrc.physCellId'])
                                    cell_offset = q_offset_range[int(cell_val['lte-rrc.cellIndividualOffset'])]
                                    new_info["cell_list"].append({"cell_id":cell_id,"cell_offset":cell_offset})
                        if "lte_measurement_object" not in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID, self.__last_DLFreq)]:
                            self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["lte_measurement_object"] = []
                        if new_info not in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["lte_measurement_object"]:
                            self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["lte_measurement_object"].append(new_info)

                    #Add a UTRA (3G) measurement object:
                    if field.get('name') == "lte-rrc.measObjectUTRA_element":
                        field_val = {}

                        field_val['lte-rrc.carrierFreq'] = None
                        field_val['lte-rrc.offsetFreq'] = 0

                        for val in field.iter('field'):
                            field_val[val.get('name')] = val.get('show')

                        freq = int(field_val['lte-rrc.carrierFreq'])
                        offsetFreq = int(field_val['lte-rrc.offsetFreq'])
                        new_info = {"measobj_id":measobj_id,"freq":freq,"offsetFreq":offsetFreq}

                        if "utra_3g_measurement_object" not in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID, self.__last_DLFreq)]:
                            self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["utra_3g_measurement_object"] = []
                        if new_info not in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["utra_3g_measurement_object"]:
                            self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["utra_3g_measurement_object"].append(new_info)

                    #Add a LTE report configuration
                    if field.get('name') == "lte-rrc.reportConfigEUTRA_element":
                        hyst = 0
                        for val in field.iter('field'):
                            if val.get('name') == 'lte-rrc.hysteresis':
                                hyst = int(val.get('show'))

                        new_info = {"report_id":report_id,"hyst":hyst/2.0}
                        new_info["event_list"] = []

                        for val in field.iter('field'):

                            if val.get('name') == 'lte-rrc.eventA1_element':
                                for item in val.iter('field'):
                                    if item.get('name') == 'lte-rrc.threshold_RSRP':
                                        new_info["event_list"].append({"event_type":"a1","threshold":int(item.get('show'))-140})
                                        break
                                    if item.get('name') == 'lte-rrc.threshold_RSRQ':
                                        new_info["event_list"].append({"event_type":"a1","threshold":(int(item.get('show'))-140)/2.0})
                                        break

                            if val.get('name') == 'lte-rrc.eventA2_element':
                                for item in val.iter('field'):
                                    if item.get('name') == 'lte-rrc.threshold_RSRP':
                                        new_info["event_list"].append({"event_type":"a2","threshold":int(item.get('show'))-140})
                                        break
                                    if item.get('name') == 'lte-rrc.threshold_RSRQ':
                                        new_info["event_list"].append({"event_type":"a2","threshold":(int(item.get('show'))-40)/2.0})
                                        break

                            if val.get('name') == 'lte-rrc.eventA3_element':
                                for item in val.iter('field'):
                                    if item.get('name') == 'lte-rrc.a3_Offset':
                                        new_info["event_list"].append({"event_type":"a3","offset":int(item.get('show'))/2.0})
                                        break

                            if val.get('name') == 'lte-rrc.eventA4_element':
                                for item in val.iter('field'):
                                    if item.get('name') == 'lte-rrc.threshold_RSRP':
                                        new_info["event_list"].append({"event_type":"a4","threshold":int(item.get('show'))-140})
                                        break
                                    if item.get('name') == 'lte-rrc.threshold_RSRQ':
                                        report_config.add_event('a4',(int(item.get('show'))-40)/2.0)
                                        new_info["event_list"].append({"event_type":"a4","threshold":(int(item.get('show'))-40)/2.0})
                                        break

                            if val.get('name') == 'lte-rrc.eventA5_element':
                                threshold1 = None
                                threshold2 = None
                                for item in val.iter('field'):
                                    if item.get('name') == 'lte-rrc.a5_Threshold1':
                                        for item2 in item.iter('field'):
                                            if item2.get('name') == 'lte-rrc.threshold_RSRP':
                                                threshold1 = int(item2.get('show'))-140
                                                break
                                            if item2.get('name') == 'lte-rrc.threshold_RSRQ':
                                                threshold1 = (int(item2.get('show'))-40)/2.0
                                                break
                                    if item.get('name') == 'lte-rrc.a5_Threshold2':
                                        for item2 in item.iter('field'):
                                            if item2.get('name') == 'lte-rrc.threshold_RSRP':
                                                threshold2 = int(item2.get('show'))-140
                                                break
                                            if item2.get('name') == 'lte-rrc.threshold_RSRQ':
                                                threshold2 = (int(item2.get('show'))-40)/2.0
                                                break
                                new_info["event_list"].append({"event_type":"a5","threshold1":threshold1,"threshold2":threshold2})

                            if val.get('name') == 'lte-rrc.eventB2_element':

                                threshold1 = None
                                threshold2 = None
                                for item in val.iter('field'):
                                    if item.get('name') == 'lte-rrc.b2_Threshold1':
                                        for item2 in item.iter('field'):
                                            if item2.get('name') == 'lte-rrc.threshold_RSRP':
                                                threshold1 = int(item2.get('show'))-140
                                                break
                                            if item2.get('name') == 'lte-rrc.threshold_RSRQ':
                                                threshold1 = (int(item2.get('show'))-40)/2.0
                                                break
                                    if item.get('name') == 'lte-rrc.b2_Threshold2':
                                        for item2 in item.iter('field'):
                                            if item2.get('name') == 'lte-rrc.threshold_RSRP':
                                                threshold2 = int(item2.get('show'))-140
                                                break
                                            if item2.get('name') == 'lte-rrc.threshold_RSRQ':
                                                threshold2 = (int(item2.get('show'))-40)/2.0
                                                break
                                            if item2.get('name') == 'lte-rrc.utra_RSCP':
                                                threshold2 = int(item2.get('show'))-115
                                                break
                                new_info["event_list"].append({"event_type":"b2","threshold1":threshold1,"threshold2":threshold2})

                        if "lte_report_configuration" not in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]:
                            self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["lte_report_configuration"] = []
                        if new_info not in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["lte_report_configuration"]:
                            self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["lte_report_configuration"].append(new_info)


                    #Add a 2G/3G report configuration
                    if field.get('name') == "lte-rrc.reportConfigInterRAT_element":

                        hyst=0
                        for val in field.iter('field'):
                            if val.get('name') == 'lte-rrc.hysteresis':
                                hyst = int(val.get('show'))

                        new_info = {}
                        new_info = {"report_id":report_id,"hyst":hyst/2.0}
                        new_info["event_list"] = []


                        for val in field.iter('field'):

                            if val.get('name') == 'lte-rrc.eventB1_element':
                                for item in val.iter('field'):
                                    if item.get('name') == 'lte-rrc.threshold_RSRP':
                                        new_info["event_list"].append({"event_type":"b1","threshold":int(item.get('show'))-140})
                                        break
                                    if item.get('name') == 'lte-rrc.threshold_RSRQ':
                                        new_info["event_list"].append({"event_type":"b1","threshold":(int(item.get('show'))-40)/2.0})
                                        break
                                    if item.get('name') == 'lte-rrc.threshold_RSCP':
                                        new_info["event_list"].append({"event_type":"b1","threshold":int(item.get('show'))-115})
                                        break

                            if val.get('name') == 'lte-rrc.eventB2_element':

                                threshold1 = None
                                threshold2 = None
                                for item in val.iter('field'):
                                    if item.get('name') == 'lte-rrc.b2_Threshold1':
                                        for item2 in item.iter('field'):
                                            if item2.get('name') == 'lte-rrc.threshold_RSRP':
                                                threshold1 = int(item2.get('show'))-140
                                                break
                                            if item2.get('name') == 'lte-rrc.threshold_RSRQ':
                                                threshold1 = (int(item2.get('show'))-40)/2.0
                                                break
                                    if item.get('name') == 'lte-rrc.b2_Threshold2':
                                        for item2 in item.iter('field'):
                                            if item2.get('name') == 'lte-rrc.threshold_RSRP':
                                                threshold2 = int(item2.get('show'))-140
                                                break
                                            if item2.get('name') == 'lte-rrc.threshold_RSRQ':
                                                threshold2 = (int(item2.get('show'))-40)/2.0
                                                break
                                            if item2.get('name') == 'lte-rrc.utra_RSCP':
                                                threshold2 = int(item2.get('show'))-115
                                                break
                                new_info["event_list"].append({"event_type":"b2","threshold1":threshold1,"threshold2":threshold2})

                        if "2g3g_report_reconfiguration" not in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]:
                            self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["2g3g_report_reconfiguration"] = []
                        if new_info not in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["2g3g_report_reconfiguration"]:
                            self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["2g3g_report_reconfiguration"].append(new_info)

                    #Add a LTE measurement report config
                    if field.get('name') == "lte-rrc.MeasIdToAddMod_element":
                        field_val = {}
                        for val in field.iter('field'):
                            field_val[val.get('name')] = val.get('show')

                        meas_id = int(field_val['lte-rrc.measId'])
                        obj_id = int(field_val['lte-rrc.measObjectId'])
                        config_id = int(field_val['lte-rrc.reportConfigId'])

                        new_info = {"measId":meas_id,"measObjectId":obj_id,"reportConfigId":config_id}

                        if "lte_measurement_report_config" not in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID, self.__last_DLFreq)]:
                            self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["lte_measurement_report_config"] = []
                        if new_info not in self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["lte_measurement_report_config"]:
                            self.__lte_mobility_misconfig_serving_cell_dict[(self.__last_CellID,self.__last_DLFreq)]["lte_measurement_report_config"].append(new_info)

        self.__last_lte_rrc_freq = log_item["Freq"]


    def __callback_lte_rrc_serv_cell_info(self, event):
        log_item = event.data
        # print "[Haotian] lte_rrc_cerv_cell_info"
        # print log_item
        # print "[Haotian-end]"

        if log_item["MNC Digit"] == 3:
            s = "LTE/%(MCC)03d-%(MNC)03d-%(TAC)d-%(Cell Identity)d" % log_item
        elif log_item["MNC Digit"] == 2:
            s = "LTE/%(MCC)03d-%(MNC)02d-%(TAC)d-%(Cell Identity)d" % log_item

        CellID = int("%(Cell ID)d" % log_item)
        DLFreq = int("%(Downlink frequency)d" % log_item)
        self.__add_plmn_search_cell(s, log_item)
        if (CellID,DLFreq) not in self.__lte_mobility_misconfig_serving_cell_dict.keys():
            self.__lte_mobility_misconfig_serving_cell_dict[(CellID,DLFreq)] = {}
        if "lte_rrc_cerv_cell_info" not in self.__lte_mobility_misconfig_serving_cell_dict[(CellID,DLFreq)]:
            self.__lte_mobility_misconfig_serving_cell_dict[(CellID,DLFreq)]["lte_rrc_cerv_cell_info"] = []
        log_item['timestamp'] = str(log_item['timestamp'].now())
        self.__lte_mobility_misconfig_serving_cell_dict[(CellID,DLFreq)]["lte_rrc_cerv_cell_info"].append(log_item)
        self.__last_CellID = CellID
        self.__last_DLFreq = DLFreq
