#!/usr/bin/python
# Filename: mobilitymisconfiggsmcdma_analyzer.py
"""
Author: Haotian Deng
"""

from mobile_insight.analyzer.analyzer import *
import ast
import subprocess
import xml.etree.ElementTree as ET
import datetime
import re
import geocoder

__all__ = ["MobilityMisconfigGsmCdmaAnalyzer"]

class MobilityMisconfigGsmCdmaAnalyzer(Analyzer):
    """
    Analyze the GSM/CDMA MobilityMisconfig of the phone.
    """

    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__filter)

        self.__gsm_mobility_misconfig_serving_cell_dict = {}
        self.__cdma_mobility_misconfig_serving_cell_dict = {}
        self.__evdo_mobility_misconfig_serving_cell_dict = {}

    def reset(self):
        self.__cdma_mobility_misconfig_serving_cell_dict = {}
        self.__gsm_last_geolocation = None
        self.__last_SID = None
        self.__last_NID = None
        self.__last_BaseID = None

        self.__gsm_mobility_misconfig_serving_cell_dict = {}
        self.__cdma_last_geolocation = None
        self.last_mcc = None
        self.last_mnc = None
        self.last_lac = None
        self.last_cid = None
        self.last_bsicncc = None
        self.last_bsicbcc = None

        self.__evdo_mobility_misconfig_serving_cell_dict = {}
        self.__evdo_last_geolocation = None
        self.__evdo_last_CountryCode = None
        self.__evdo_last_SubnetID = None
        self.__evdo_last_SectorID = None

    def set_source(self,source):
        """
        Set the trace source. Enable the WCDMA RRC messages.

        :param source: the trace source.
        :type source: trace collector
        """
        Analyzer.set_source(self,source)

        source.enable_log("GSM_RR_Cell_Information")
        # source.enable_log("GSM_RR_Cell_Reselection_Parameters")
        source.enable_log("GSM_DSDS_RR_Cell_Information")
        # source.enable_log("GSM_DSDS_RR_Cell_Reselection_Parameters")
        source.enable_log("CDMA_Paging_Channel_Message")
        source.enable_log("1xEV_Signaling_Control_Channel_Broadcast")

    def get_gsm_mobility_misconfig_serving_cell_dict(self):
        return self.__gsm_mobility_misconfig_serving_cell_dict

    def get_cdma_mobility_misconfig_serving_cell_dict(self):
        return self.__cdma_mobility_misconfig_serving_cell_dict

    def get_evdo_mobility_misconfig_serving_cell_dict(self):
        return self.__evdo_mobility_misconfig_serving_cell_dict

    def __filter(self, event):
        try:
            log_item = event.data.decode()
            decoded_event = Event(event.timestamp, event.type_id, log_item)

            if event.type_id == "GSM_RR_Cell_Information" or event.type_id == "GSM_DSDS_RR_Cell_Information":
                self.__callback_gsm_rr_cell_information(decoded_event)
            elif event.type_id == "GSM_RR_Cell_Reselection_Parameters" or event.type_id == "GSM_DSDS_RR_Cell_Reselection_Parameters":
                self.__callback_gsm_rr_cell_reselection_parameters(decoded_event)
            elif event.type_id == "CDMA_Paging_Channel_Message":
                self.__callback_cdma_paging_channel_message(decoded_event)
            elif event.type_id == "1xEV_Signaling_Control_Channel_Broadcast":
                self.__callback_evdo_signaling_control_channel_broadcast(decoded_event)

        except Exception as e:
            pass

    def __callback_gsm_rr_cell_information(self, event):
        log_item = event.data
        self.last_mcc = str(log_item['MCC'])
        self.last_mnc = str(log_item['MNC'])
        self.last_lac = str(log_item['LAC'])
        self.last_cid = str(log_item['Cell ID'])
        self.last_bsicncc = str(log_item['BSIC-NCC'])
        self.last_bsicbcc = str(log_item['BSIC-BCC'])
        if (self.last_mcc, self.last_mnc, self.last_lac, self.last_cid, self.last_bsicncc, self.last_bsicbcc) not in self.__gsm_mobility_misconfig_serving_cell_dict.keys():
            self.__gsm_mobility_misconfig_serving_cell_dict[(self.last_mcc, self.last_mnc, self.last_lac, self.last_cid, self.last_bsicncc, self.last_bsicbcc)] = {}
        if "gsm_geolocation" not in self.__gsm_mobility_misconfig_serving_cell_dict[(self.last_mcc, self.last_mnc, self.last_lac, self.last_cid, self.last_bsicncc, self.last_bsicbcc)]:
            command = ['python', '/home/deng164/milab-server/manage.py', 'query', 'GSM', self.last_mcc, self.last_mnc, self.last_lac, self.last_cid]
            output = subprocess.check_output(command)
            self.__gsm_last_geolocation = ast.literal_eval(output)

            if self.__gsm_last_geolocation['country'] is None:
                self.__gsm_last_geolocation['country'] = 'None'
            if self.__gsm_last_geolocation['state'] is None:
                self.__gsm_last_geolocation['state'] = 'None'
            if self.__gsm_last_geolocation['city'] is None:
                self.__gsm_last_geolocation['city'] = 'None'
            if self.__gsm_last_geolocation['lat'] is None:
                self.__gsm_last_geolocation['lat'] = 'None'
            if self.__gsm_last_geolocation['lon'] is None:
                self.__gsm_last_geolocation['lon'] = 'None'

            self.__gsm_mobility_misconfig_serving_cell_dict[(self.last_mcc, self.last_mnc, self.last_lac, self.last_cid, self.last_bsicncc, self.last_bsicbcc)]["gsm_geolocation"] = self.__gsm_last_geolocation
        log_item['timestamp'] = "'" + str(log_item['timestamp']) + "'"
        log_item.update(self.__gsm_last_geolocation)
        # command = ['python', '/home/deng164/milab-server/manage.py', 'update_gsm_cellinfo',
        #     self.last_mcc, self.last_mnc, self.last_lac, self.last_cid, self.last_bsicncc, self.last_bsicbcc,
        #     self.__gsm_last_geolocation['country'],
        #     self.__gsm_last_geolocation['state'],
        #     self.__gsm_last_geolocation['city'],
        #     self.__gsm_last_geolocation['lat'],
        #     self.__gsm_last_geolocation['lon'],
        #     str(log_item['BCCH ARFCN']),
        #     str(log_item['Cell Selection Priority']),
        #     str(log_item['timestamp']),
        #     ]
        # print command
        # output = subprocess.check_output(command)
        # print output

        # print "gsm_cellinfo, mcc: %s, mnc: %s, lac: %s, cid: %s, bsicncc: %s, bsicbcc: %s, country: %s, state: %s, city: %s, lat: %s, lon: %s" % (
        # self.last_mcc, self.last_mnc, self.last_lac, self.last_cid, self.last_bsicncc, self.last_bsicbcc,
        # self.__gsm_last_geolocation['country'],
        # self.__gsm_last_geolocation['state'],
        # self.__gsm_last_geolocation['city'],
        # self.__gsm_last_geolocation['lat'],
        # self.__gsm_last_geolocation['lon'])

        if "gsm_cell_information" not in self.__gsm_mobility_misconfig_serving_cell_dict[(self.last_mcc, self.last_mnc, self.last_lac, self.last_cid, self.last_bsicncc, self.last_bsicbcc)]:
            self.__gsm_mobility_misconfig_serving_cell_dict[(self.last_mcc, self.last_mnc, self.last_lac, self.last_cid, self.last_bsicncc, self.last_bsicbcc)]["gsm_cell_information"] = []
        self.__gsm_mobility_misconfig_serving_cell_dict[(self.last_mcc, self.last_mnc, self.last_lac, self.last_cid, self.last_bsicncc, self.last_bsicbcc)]["gsm_cell_information"].append(log_item)

    def __callback_gsm_rr_cell_reselection_parameters(self, event):
        log_item = event.data
        if self.last_cid is None:
            return
        log_item['timestamp'] = "'" + str(log_item['timestamp']) + "'"
        # command = ['python', '/home/deng164/milab-server/manage.py', 'update_gsm_reselectparms',
        #     self.last_mcc, self.last_mnc, self.last_lac, self.last_cid, self.last_bsicncc, self.last_bsicbcc,
        #     str(log_item['Cell Reselection Hysteresis']),
        #     str(log_item['MS_TXPWR_MAX_CCH']),
        #     str(log_item['RxLev Access Min']),
        #     str(log_item['Power Offset']),
        #     str(log_item['Cell Bar Qualify']),
        #     str(log_item['Cell Reselection Offset (dB)']),
        #     str(log_item['Temporary Offset (dB)']),
        #     str(log_item['Penalty Time']),
        #     str(log_item['timestamp']),
        #     ]
        # print command
        # output = subprocess.check_output(command)
        # print output

    def __callback_cdma_paging_channel_message(self, event):
        log_item = event.data
        if log_item['Message ID'] != 1:
            return
        self.__last_SID = str(log_item['SID'])
        self.__last_NID = str(log_item['NID'])
        self.__last_BaseID = str(log_item['Base ID'])
        if (self.__last_SID, self.__last_NID, self.__last_BaseID) not in self.__cdma_mobility_misconfig_serving_cell_dict.keys():
            self.__cdma_mobility_misconfig_serving_cell_dict[(self.__last_SID, self.__last_NID, self.__last_BaseID)] = {}
        if "cdma_geolocation" not in self.__cdma_mobility_misconfig_serving_cell_dict[(self.__last_SID, self.__last_NID, self.__last_BaseID)]:
            self.__cdma_last_geolocation = {
                    'lat': str(log_item['Base Latitude']),
                    'lon': str(log_item['Base Longitude']),
                    'city': "Unknown",
                    'state': "Unknown",
                    'country': "Unknown",
                    }
            g = geocoder.bing([
                        self.__cdma_last_geolocation['lat'], self.__cdma_last_geolocation['lon']
                        ], method='reverse')
            self.__cdma_last_geolocation['city'] = g.city
            self.__cdma_last_geolocation['state'] = g.state
            self.__cdma_last_geolocation['country'] = g.country
            if self.__cdma_last_geolocation['country'] is None:
                self.__cdma_last_geolocation['country'] = 'None'
            if self.__cdma_last_geolocation['state'] is None:
                self.__cdma_last_geolocation['state'] = 'None'
            if self.__cdma_last_geolocation['city'] is None:
                self.__cdma_last_geolocation['city'] = 'None'

            self.__cdma_mobility_misconfig_serving_cell_dict[(self.__last_SID, self.__last_NID, self.__last_BaseID)]["cdma_geolocation"] = self.__cdma_last_geolocation
        log_item['timestamp'] = "'" + str(log_item['timestamp']) + "'"
        log_item.update(self.__cdma_last_geolocation)
        # print "cdma_systemParameters, SID: %s, NID: %s, BaseID: %s, country: %s, state: %s, city: %s, lat: %s, lon: %s" % (
        # self.__last_SID, self.__last_NID, self.__last_BaseID,
        # self.__cdma_last_geolocation['country'],
        # self.__cdma_last_geolocation['state'],
        # self.__cdma_last_geolocation['city'],
        # self.__cdma_last_geolocation['lat'],
        # self.__cdma_last_geolocation['lon'])

        # command = ['python', '/home/deng164/milab-server/manage.py', 'update_cdma_systemparameters',
        #         self.__last_SID, self.__last_NID, self.__last_BaseID,
        #         self.__cdma_last_geolocation['country'],
        #         self.__cdma_last_geolocation['state'],
        #         self.__cdma_last_geolocation['city'],
        #         self.__cdma_last_geolocation['lat'],
        #         self.__cdma_last_geolocation['lon'],
        #         str(log_item['T_Add']),
        #         str(log_item['T_Drop']),
        #         str(log_item['T_Comp']),
        #         str(log_item['T_TDrop']),
        #         str(log_item['timestamp']),
        #     ]
        # print command
        # output = subprocess.check_output(command)
        # print output
        if "cdma_paging" not in self.__cdma_mobility_misconfig_serving_cell_dict[(self.__last_SID, self.__last_NID, self.__last_BaseID)]:
            self.__cdma_mobility_misconfig_serving_cell_dict[(self.__last_SID, self.__last_NID, self.__last_BaseID)]["cdma_paging"] = []
        self.__cdma_mobility_misconfig_serving_cell_dict[(self.__last_SID, self.__last_NID, self.__last_BaseID)]["cdma_paging"].append(log_item)

    def __callback_evdo_signaling_control_channel_broadcast(self, event):
        log_item = event.data
        if log_item['Message ID'] != 1 or log_item['Protocol Type'] != 15:
            return
        self.__evdo_last_CountryCode = str(log_item['Country Code'])
        self.__evdo_last_SubnetID = str(log_item['Subnet ID'])
        self.__evdo_last_SectorID = str(log_item['Sector ID'])
        if (self.__evdo_last_CountryCode, self.__evdo_last_SubnetID, self.__evdo_last_SectorID) not in self.__evdo_mobility_misconfig_serving_cell_dict.keys():
            self.__evdo_mobility_misconfig_serving_cell_dict[(self.__evdo_last_CountryCode, self.__evdo_last_SubnetID, self.__evdo_last_SectorID)] = {}
        if "evdo_geolocation" not in self.__evdo_mobility_misconfig_serving_cell_dict[(self.__evdo_last_CountryCode, self.__evdo_last_SubnetID, self.__evdo_last_SectorID)]:
            self.__evdo_last_geolocation = {
                    'lat': str(log_item['Latitude']),
                    'lon': str(log_item['Longitude']),
                    'city': "Unknown",
                    'state': "Unknown",
                    'country': "Unknown",
                    }
            g = geocoder.bing([
                        self.__evdo_last_geolocation['lat'], self.__evdo_last_geolocation['lon']
                        ], method='reverse')
            self.__evdo_last_geolocation['city'] = g.city
            self.__evdo_last_geolocation['state'] = g.state
            self.__evdo_last_geolocation['country'] = g.country
            if self.__evdo_last_geolocation['country'] is None:
                self.__evdo_last_geolocation['country'] = 'None'
            if self.__evdo_last_geolocation['state'] is None:
                self.__evdo_last_geolocation['state'] = 'None'
            if self.__evdo_last_geolocation['city'] is None:
                self.__evdo_last_geolocation['city'] = 'None'

            self.__evdo_mobility_misconfig_serving_cell_dict[(self.__evdo_last_CountryCode, self.__evdo_last_SubnetID, self.__evdo_last_SectorID)]["evdo_geolocation"] = self.__evdo_last_geolocation
        log_item['timestamp'] = "'" + str(log_item['timestamp']) + "'"
        log_item.update(self.__evdo_last_geolocation)

        if "evdo_signaling" not in self.__evdo_mobility_misconfig_serving_cell_dict[(self.__evdo_last_CountryCode, self.__evdo_last_SubnetID, self.__evdo_last_SectorID)]:
            self.__evdo_mobility_misconfig_serving_cell_dict[(self.__evdo_last_CountryCode, self.__evdo_last_SubnetID, self.__evdo_last_SectorID)]["evdo_signaling"] = []
        self.__evdo_mobility_misconfig_serving_cell_dict[(self.__evdo_last_CountryCode, self.__evdo_last_SubnetID, self.__evdo_last_SectorID)]["evdo_signaling"].append(log_item)

