#!/usr/bin/python
# Filename: online-analysis-example.py
import collections
import numpy as np
import os
import pickle
import re
import sys

#Import MobileInsight modules
from mobile_insight.monitor import OfflineReplayer
from active_handoff_analyzer import ActiveHandoffAnalyzer


def get_sorted_logs(directory):
    # logs = []
    # for root, d, filenames in os.walk(directory):
    #     for f in filenames:
    #         if (f.endswith(".mi2log") or f.endswith(".qmdl")):
    #             logs.append(os.path.join(root, f))
    # # sorted_logs = []
    # # for f in logs:
    # #     # print f
    # #     # location, rat, d, t, imsi, phone, carrier = re.match(r"(.+)_(.+)_diag_log_(\d+)_(\d+)_(\d+|null)_(samsung-SM-G900T|Huawei-Nexus6P|Google-Pixel)_(T-Mobile|null|AT&T-MicroCell|AT&T|VerizonWireless|Sprint)\.mi2log", f).groups()
    # #     d, t, imsi, phone, carrier = re.match(r"diag_log_(\d+)_(\d+)_(\d+|null)_(samsung-SM-G900T|Huawei-Nexus6P|Google-Pixel|Google-PixelXL)_(T-Mobile|null|AT&T-MicroCell|AT&T|VerizonWireless|Sprint|Project_Fi-310260|-)\.mi2log", f).groups()
    # #     if len(t) < 6:
    # #         t += '0'
    # #     key = d + t
    # #     sorted_logs.append((key, f))
    # # # sorted by date + time
    # # sorted_logs = [f for k, f in sorted(sorted_logs)]
    # # return sorted_logs
    # return logs

    content = []
    with open(directory) as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    return content


def parse_qmdl(path_input):
    # directory = "/home/moonsky219/ownCloud/mssn/misconfig_exp/data/Verizon/L714/"

    directory = path_input
    logs = get_sorted_logs(directory)

    # Initialize a 3G/4G monitor
    src = OfflineReplayer()
    m = ActiveHandoffAnalyzer()

    for f in logs:
        # print "=== %s ===" % f
        m.reset()
        m.set_source(src)
        src.set_input_path(f)

        # Start the monitoring
        src.run()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage python MobilityMisConfig-analysis.py [log directory]"
        exit()
    parse_qmdl(sys.argv[1])

    # try:
    #     fd = open("mmAnalyzer-result.pickle", "rb")
    #     umts_normal_service_log = pickle.load(fd)
    #     umts_plmn_search_log = pickle.load(fd)
    #     umts_attach_log = pickle.load(fd)
    #     umts_lu_log = pickle.load(fd)
    #     umts_rau_log = pickle.load(fd)

    #     lte_normal_service_log = pickle.load(fd)
    #     lte_plmn_search_log = pickle.load(fd)
    #     lte_attach_log = pickle.load(fd)
    #     lte_tau_log = pickle.load(fd)

    #     lte_tau_qos_info = pickle.load(fd)
    #     lte_cell_resel_to_umts_config = pickle.load(fd)
    #     lte_drx_config = pickle.load(fd)
    #     lte_tdd_config = pickle.load(fd)
    #     n_lte_rrc_reconfig = pickle.load(fd)
    #     lte_mobility_misconfig_serving_cell_dict = pickle.load(fd)
    #     utra_mobility_misconfig_serving_cell_dict = pickle.load(fd)
    #     fd.close()

    #     for CellIdentityCombine, CellInfo in lte_mobility_misconfig_serving_cell_dict.iteritems():
    #         print CellIdentityCombine
    #         for InfoKey, InfoValue in CellInfo.iteritems():
    #             print InfoKey
    #             if isinstance(InfoValue, list):
    #                 for InfoValueItem in InfoValue:
    #                     print InfoValueItem
    #             elif isinstance(InfoValue, dict):
    #                 for InfoValueKey, InfoValueItem in InfoValue:
    #                     print InfoValueKey
    #                     print InfoValueItem
    #         print "-----------------------------------------------------------"

    #     for CellIdentityCombine, CellInfo in utra_mobility_misconfig_serving_cell_dict.iteritems():
    #         print CellIdentityCombine
    #         for InfoKey, InfoValue in CellInfo.iteritems():
    #             print InfoKey
    #             if isinstance(InfoValue, list):
    #                 for InfoValueItem in InfoValue:
    #                     print InfoValueItem
    #             elif isinstance(InfoValue, dict):
    #                 for InfoValueKey, InfoValueItem in InfoValue:
    #                     print InfoValueKey
    #                     print InfoValueItem
    #         print "-----------------------------------------------------------"


    #     # print lte_mobility_misconfig_serving_cell_dict

    #     # print "# LTE RRC Reconfig: %d" % n_lte_rrc_reconfig
    #     # analyze(umts_normal_service_log, umts_plmn_search_log,
    #     #         umts_attach_log, umts_lu_log, umts_rau_log,
    #     #         lte_normal_service_log, lte_plmn_search_log,
    #     #         lte_attach_log, lte_tau_log,
    #     #         lte_tau_qos_info, lte_cell_resel_to_umts_config,
    #     #         lte_drx_config, lte_tdd_config)

    #     # print "*******************************************"
    #     # print "--------------------umts_normal_service_log"
    #     # print umts_normal_service_log
    #     # print "--------------------umts_plmn_search_log"
    #     # print umts_plmn_search_log
    #     # print "--------------------umts_attach_log"
    #     # print umts_attach_log
    #     # print "--------------------umts_lu_log"
    #     # print umts_lu_log
    #     # print "--------------------umts_rau_log"
    #     # print umts_rau_log
    #     # print "--------------------lte_normal_service_log"
    #     # print lte_normal_service_log
    #     # print "--------------------lte_plmn_search_log"
    #     # print lte_plmn_search_log
    #     # print "--------------------lte_attach_log"
    #     # print lte_attach_log
    #     # print "--------------------lte_tau_log"
    #     # print lte_tau_log
    #     # print "--------------------lte_tau_qos_info"
    #     # print lte_tau_qos_info
    #     # print "--------------------lte_cell_resel_to_umts_config"
    #     # print lte_cell_resel_to_umts_config
    #     # print "--------------------lte_drx_config"
    #     # print lte_drx_config
    #     # print "--------------------lte_tdd_config"
    #     # print lte_tdd_config
    #     # print "--------------------"

    # except IOError:
    #     print "IOError"
