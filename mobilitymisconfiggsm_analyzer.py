#!/usr/bin/python
# Filename: mobilitymisconfiggsm_analyzer.py
"""
Author: Haotian Deng
"""

from mobile_insight.analyzer.analyzer import *
import ast
import subprocess
import xml.etree.ElementTree as ET
import datetime
import re

__all__ = ["MobilityMisconfigGsmAnalyzer"]

class MobilityMisconfigGsmAnalyzer(Analyzer):
    """
    Analyze the GSM MobilityMisconfig of the phone.
    """

    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__filter)

        self.__gsm_mobility_misconfig_serving_cell_dict = {}

    def reset(self):
        self.__lte_mobility_misconfig_serving_cell_dict = {}
        self.__3g_mobility_misconfig_serving_cell_dict = {}
        self.__last_CellID = None
        self.__last_DLFreq = None
        self.__last_3g_cellId = None
        self.__last_3g_UtraDLFreq = None

    def set_source(self,source):
        """
        Set the trace source. Enable the WCDMA RRC messages.

        :param source: the trace source.
        :type source: trace collector
        """
        Analyzer.set_source(self,source)

        source.enable_log("GSM_RR_Cell_Information")
        source.enable_log("GSM_RR_Cell_Reselection_Parameters")
        source.enable_log("GSM_DSDS_RR_Cell_Information")
        source.enable_log("GSM_DSDS_RR_Cell_Reselection_Parameters")

    def get_gsm_mobility_misconfig_serving_cell_dict(self):
        return self.__gsm_mobility_misconfig_serving_cell_dict


    def __filter(self, event):
        try:
            log_item = event.data.decode()
            decoded_event = Event(event.timestamp, event.type_id, log_item)

            if event.type_id == "GSM_RR_Cell_Information" or event.type_id == "GSM_DSDS_RR_Cell_Information":
                self.__callback_gsm_rr_cell_information(decoded_event)
            elif event.type_id == "GSM_RR_Cell_Reselection_Parameters" or event.type_id == "GSM_DSDS_RR_Cell_Reselection_Parameters":
                self.__callback_gsm_rr_cell_reselection_parameters(decoded_event)
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
            print command
            output = subprocess.check_output(command)
            print "query end"
            print output
            self.__last_geolocation = ast.literal_eval(output)
            self.__gsm_mobility_misconfig_serving_cell_dict[(self.last_mcc, self.last_mnc, self.last_lac, self.last_cid, self.last_bsicncc, self.last_bsicbcc)]["gsm_geolocation"] = self.__last_geolocation
        log_item['timestamp'] = "'" + str(log_item['timestamp']) + "'"
        command = ['python', '/home/deng164/milab-server/manage.py', 'update_gsm_cellinfo',
            self.last_mcc, self.last_mnc, self.last_lac, self.last_cid, self.last_bsicncc, self.last_bsicbcc,
            self.__last_geolocation['country'],
            self.__last_geolocation['state'],
            self.__last_geolocation['city'],
            self.__last_geolocation['lat'],
            self.__last_geolocation['lon'],
            str(log_item['BCCH ARFCN']),
            str(log_item['Cell Selection Priority']),
            str(log_item['timestamp']),
            ]
        print command
        output = subprocess.check_output(command)
        print output


    def __callback_gsm_rr_cell_reselection_parameters(self, event):
        log_item = event.data
        if self.last_cid is None:
            return
        log_item['timestamp'] = "'" + str(log_item['timestamp']) + "'"
        command = ['python', '/home/deng164/milab-server/manage.py', 'update_gsm_reselectparms',
            self.last_mcc, self.last_mnc, self.last_lac, self.last_cid, self.last_bsicncc, self.last_bsicbcc,
            str(log_item['Cell Reselection Hysteresis']),
            str(log_item['MS_TXPWR_MAX_CCH']),
            str(log_item['RxLev Access Min']),
            str(log_item['Power Offset']),
            str(log_item['Cell Bar Qualify']),
            str(log_item['Cell Reselection Offset (dB)']),
            str(log_item['Temporary Offset (dB)']),
            str(log_item['Penalty Time']),
            str(log_item['timestamp']),
            ]
        print command
        output = subprocess.check_output(command)
        print output

