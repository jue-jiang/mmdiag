#!/usr/bin/python
# Filename: mobilitymisconfigcdma_analyzer.py
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

__all__ = ["MobilityMisconfigCdmaAnalyzer"]

class MobilityMisconfigCdmaAnalyzer(Analyzer):
    """
    Analyze the CDMA MobilityMisconfig of the phone.
    """

    def __init__(self):
        Analyzer.__init__(self)
        self.add_source_callback(self.__filter)

        self.__cdma_mobility_misconfig_serving_cell_dict = {}

    def reset(self):
        self.__cdma_mobility_misconfig_serving_cell_dict = {}
        self.__last_SID = None
        self.__last_NID = None
        self.__last_BaseID = None

    def set_source(self,source):
        """
        Set the trace source. Enable the WCDMA RRC messages.

        :param source: the trace source.
        :type source: trace collector
        """
        Analyzer.set_source(self,source)

        source.enable_log("CDMA_Paging_Channel_Message")

    def get_cdma_mobility_misconfig_serving_cell_dict(self):
        return self.__cdma_mobility_misconfig_serving_cell_dict


    def __filter(self, event):
        try:
            log_item = event.data.decode()
            decoded_event = Event(event.timestamp, event.type_id, log_item)

            if event.type_id == "CDMA_Paging_Channel_Message":
                self.__callback_cdma_paging_channel_message(decoded_event)
        except Exception as e:
            pass

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
            self.__last_geolocation = {
                    'lat': str(log_item['Base Latitude']),
                    'lon': str(log_item['Base Longitude']),
                    'city': "Unknown",
                    'state': "Unknown",
                    'country': "Unknown",
                    }
            g = geocoder.bing([
                        self.__last_geolocation['lat'], self.__last_geolocation['lon']
                        ], method='reverse')
            self.__last_geolocation['city'] = g.city
            self.__last_geolocation['state'] = g.state
            self.__last_geolocation['country'] = g.country
            self.__cdma_mobility_misconfig_serving_cell_dict[(self.__last_SID, self.__last_NID, self.__last_BaseID)]["cdma_geolocation"] = self.__last_geolocation
        log_item['timestamp'] = "'" + str(log_item['timestamp']) + "'"
        command = ['python', '/home/deng164/milab-server/manage.py', 'update_cdma_systemparameters',
                self.__last_SID, self.__last_NID, self.__last_BaseID,
                self.__last_geolocation['country'],
                self.__last_geolocation['state'],
                self.__last_geolocation['city'],
                self.__last_geolocation['lat'],
                self.__last_geolocation['lon'],
                str(log_item['T_Add']),
                str(log_item['T_Drop']),
                str(log_item['T_Comp']),
                str(log_item['T_TDrop']),
                str(log_item['timestamp']),
            ]
        print command
        output = subprocess.check_output(command)
        print output
