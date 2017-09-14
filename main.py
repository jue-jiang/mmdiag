#!/usr/bin/python
from mobile_insight.monitor import OfflineReplayer
from mobilitymisconfig_analyzer import MobilityMisconfigAnalyzer
import collections
import numpy as np
import os
import pickle
import re
import sys

def get_sorted_logs(fileMi2logText):
    content = []
    with open(fileMi2logText) as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    return content

def parse_qmdl(plainTextFile):
    # Initialize an OfflineReplayer as monitor
    src = OfflineReplayer()

    for f in get_sorted_logs(plainTextFile):
        print '=========' + f + '========'
        m = MobilityMisconfigAnalyzer()
        m.reset()
        m.set_source(src)
        src.set_input_path(f)

        # Start the monitoring
        src.run()

        umts_normal_service_log = m.get_umts_normal_service_log()
        umts_plmn_search_log = m.get_umts_plmn_search_log()
        umts_attach_log = m.get_umts_attach_log()
        umts_lu_log = m.get_umts_lu_log()
        umts_rau_log = m.get_umts_rau_log()

        lte_normal_service_log = m.get_lte_normal_service_log()
        lte_plmn_search_log = m.get_lte_plmn_search_log()
        lte_attach_log = m.get_lte_attach_log()
        lte_tau_log = m.get_lte_tau_log()
        lte_tau_qos_info = m.get_lte_tau_qos_info()
        lte_cell_resel_to_umts_config = m.get_lte_cell_resel_to_umts_config()
        lte_drx_config = m.get_lte_drx_config()
        lte_tdd_config = m.get_lte_tdd_config()
        n_lte_rrc_reconfig = m.get_n_lte_rrc_reconfig()
        lte_mobility_misconfig_serving_cell_dict = m.get_lte_mobility_misconfig_serving_cell_dict()
        utra_mobility_misconfig_serving_cell_dict = m.get_3g_mobility_misconfig_serving_cell_dict()

        for CellIdentityCombine, CellInfo in lte_mobility_misconfig_serving_cell_dict.iteritems():
            print CellIdentityCombine
            InfoKey = "lte_rrc_cerv_cell_info"
            if InfoKey in CellInfo:
                print InfoKey
                for InfoValueItem in CellInfo[InfoKey]:
                    print InfoValueItem
            InfoKey = "[sib3]cellReselectionInfoCommon_element"
            if InfoKey in CellInfo:
                print InfoKey
                for InfoValueItem in CellInfo[InfoKey]:
                    print InfoValueItem
            InfoKey = "[sib3]cellReselectionServingFreqInfo_element"
            if InfoKey in CellInfo:
                print InfoKey
                for InfoValueItem in CellInfo[InfoKey]:
                    print InfoValueItem
            InfoKey = "[sib3]intraFreqCellReselectionInfo_element"
            if InfoKey in CellInfo:
                print InfoKey
                for InfoValueItem in CellInfo[InfoKey]:
                    print InfoValueItem
            InfoKey = "[sib4]intraFreqBlackCellList"
            if InfoKey in CellInfo:
                print InfoKey
                for InfoValueItem in CellInfo[InfoKey]:
                    print InfoValueItem
            InfoKey = "[sib5]InterFreqCarrierFreqInfo_element"
            if InfoKey in CellInfo:
                print InfoKey
                for InfoValueItem in CellInfo[InfoKey]:
                    print InfoValueItem
            InfoKey = "[sib5]interFreqBlackCellList"
            if InfoKey in CellInfo:
                print InfoKey
                for InfoValueItem in CellInfo[InfoKey]:
                    print InfoValueItem
            InfoKey = "[sib6]CarrierFreqUTRA_FDD_element"
            if InfoKey in CellInfo:
                print InfoKey
                for InfoValueItem in CellInfo[InfoKey]:
                    print InfoValueItem
            InfoKey = "[sib8]"
            if InfoKey in CellInfo:
                print InfoKey
                for InfoValueItem in CellInfo[InfoKey]:
                    print InfoValueItem
            InfoKey = "lte_rrc_measurement_report"
            if InfoKey in CellInfo:
                print InfoKey
                for InfoValueItem in CellInfo[InfoKey]:
                    print InfoValueItem
            InfoKey = "lte_measurement_report_config"
            if InfoKey in CellInfo:
                print InfoKey
                for InfoValueItem in CellInfo[InfoKey]:
                    print InfoValueItem
            InfoKey = "lte_measurement_object"
            if InfoKey in CellInfo:
                print InfoKey
                for InfoValueItem in CellInfo[InfoKey]:
                    print InfoValueItem
            InfoKey = "utra_3g_measurement_object"
            if InfoKey in CellInfo:
                print InfoKey
                for InfoValueItem in CellInfo[InfoKey]:
                    print InfoValueItem
            InfoKey = "lte_report_configuration"
            if InfoKey in CellInfo:
                print InfoKey
                for InfoValueItem in CellInfo[InfoKey]:
                    print InfoValueItem
            InfoKey = "2g3g_report_reconfiguration"
            if InfoKey in CellInfo:
                print InfoKey
                for InfoValueItem in CellInfo[InfoKey]:
                    print InfoValueItem

            print "-----------------------------------------------------------"

        for CellIdentityCombine, CellInfo in utra_mobility_misconfig_serving_cell_dict.iteritems():
            print CellIdentityCombine
            for InfoKey, InfoValue in CellInfo.iteritems():
                print InfoKey
                if isinstance(InfoValue, list):
                    for InfoValueItem in InfoValue:
                        print InfoValueItem
                elif isinstance(InfoValue, dict):
                    print "\n\n\n\nHaotian\n\n\n\n"
                    for InfoValueKey, InfoValueItem in InfoValue:
                        print InfoValueKey
                        print InfoValueItem
            print "-----------------------------------------------------------"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage python main.py [plain text file containing path to mi2log files]"
        exit()
    parse_qmdl(sys.argv[1])
