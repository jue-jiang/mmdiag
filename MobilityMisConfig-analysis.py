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
from mobilitymisconfig_analyzer import MobilityMisconfigAnalyzer


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
    m = MobilityMisconfigAnalyzer()

    for f in logs:
        # print "=== %s ===" % f
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
                if InfoKey == "umts_geolocation":
                    continue
                print InfoKey
                if isinstance(InfoValue, list):
                    for InfoValueItem in InfoValue:
                        print InfoValueItem
                elif isinstance(InfoValue, dict):
                    for InfoValueKey, InfoValueItem in InfoValue:
                        print InfoValueKey
                        print InfoValueItem
            print "-----------------------------------------------------------"

    # fd = open("mmAnalyzer-result.pickle", "wb")
    # pickle.dump(m.get_umts_normal_service_log(), fd)
    # pickle.dump(m.get_umts_plmn_search_log(), fd)
    # pickle.dump(m.get_umts_attach_log(), fd)
    # pickle.dump(m.get_umts_lu_log(), fd)
    # pickle.dump(m.get_umts_rau_log(), fd)

    # pickle.dump(m.get_lte_normal_service_log(), fd)
    # pickle.dump(m.get_lte_plmn_search_log(), fd)
    # pickle.dump(m.get_lte_attach_log(), fd)
    # pickle.dump(m.get_lte_tau_log(), fd)

    # pickle.dump(m.get_lte_tau_qos_info(), fd)
    # pickle.dump(m.get_lte_cell_resel_to_umts_config(), fd)
    # pickle.dump(m.get_lte_drx_config(), fd)
    # pickle.dump(m.get_lte_tdd_config(), fd)
    # pickle.dump(m.get_n_lte_rrc_reconfig(), fd)
    # pickle.dump(m.get_lte_mobility_misconfig_serving_cell_dict(), fd)
    # pickle.dump(m.get_3g_mobility_misconfig_serving_cell_dict(), fd)
    # fd.flush()
    # fd.close()


def map_plmn(name):
    d = {   "": "Unknown",
            "WCDMA/Unknown": "Unknown",
            "LTE/310-120": "Sprint LTE",
            "WCDMA/310-410": "AT&T WCDMA",
            "WCDMA/310-260": "T-Mobile WCDMA",
            "LTE/310-260": "T-Mobile LTE",
            "LTE/311-490": "Sprint LTE"
            }
    if "T-Mobile" in d[name]:
        return 1
    elif "Sprint" in d[name]:
        return 2
    else:
        return 0


# Helpers
def sort_and_clear(log):
    log.sort(key=lambda s: s.start)
    i = 0
    while i < len(log) - 1:
        if log[i].end > log[i+1].start:
            log.pop(i + 1)
            i -= 1
        i += 1


def find_spans_between(spans, start, end):
    """
    Find tiem spans whose start point locates between [start, end]
    """
    i = 0
    res = []
    while i < len(spans) and not start <= spans[i].start:
        i += 1
    while i < len(spans) and spans[i].start <= end:
        res.append(spans[i])
        i += 1
    return res

def mid(lst):
    n = len(lst)
    if (n % 2) == 1:
        return lst[n / 2]
    else:
        return float(lst[n/2 - 1] + lst[n/2]) / 2.

def is_cdma_cell(cell_id):
    return cell_id.startswith("1x") or cell_id == "CDMA"


def is_att_or_verizon_cell(cell_id):
    return (cell_id.startswith("LTE/310-410")
            or cell_id.startswith("LTE/311-480")
            or cell_id.startswith("WCDMA/310-410"))


def print_percentile(fd, arr, mark):
    a = np.array(arr)
    for i in range(0, 100+1):
        p = np.percentile(a, i)
        print >> fd, p, i, mark


def analyze(umts_normal_service_log, umts_plmn_search_log,
            umts_attach_log, umts_lu_log, umts_rau_log,
            lte_normal_service_log, lte_plmn_search_log, lte_attach_log,
            lte_tau_log, lte_tau_qos_info, lte_cell_resel_to_umts_config,
            lte_drx_config, lte_tdd_config):
    sort_and_clear(umts_plmn_search_log)
    sort_and_clear(lte_plmn_search_log)
    sort_and_clear(lte_tau_log)
    sort_and_clear(lte_attach_log)

    merged_plmn_search_log = []
    i = 0
    j = 0
    while i < len(umts_plmn_search_log) or j < len(lte_plmn_search_log):
        if i == len(umts_plmn_search_log):
            merged_plmn_search_log.append(lte_plmn_search_log[j])
            j += 1
        elif j == len(lte_plmn_search_log):
            merged_plmn_search_log.append(umts_plmn_search_log[i])
            i += 1
        else:
            log1 = umts_plmn_search_log[i]
            log2 = lte_plmn_search_log[j]
            if log1.end < log2.start:
                merged_plmn_search_log.append(log1)
                i += 1
            elif log2.end < log1.start:
                merged_plmn_search_log.append(log2)
                j += 1
            else:
                assert log1.end == log2.end
                if log1.start < log2.start:
                    merged_plmn_search_log.append(log1)
                else:
                    merged_plmn_search_log.append(log2)
                i += 1
                j += 1

    print_plmn_search_log(merged_plmn_search_log)
    # analyze_plmn_percentile(merged_plmn_search_log)
    # analyze_plmn_cells(merged_plmn_search_log)

    # Print all possible cells
    # cell_set = reduce(lambda s1, s2: s1 | s2,
    #                     [set([s.cell_id for s in span.search_log]) for span in merged_plmn_search_log)
    # print sorted(list(cell_set))

    analyze_plmn_cells2(merged_plmn_search_log)
    analyze_plmn_cells_time(merged_plmn_search_log)
    # analyze_plmn_time(merged_plmn_search_log)
    analyze_plmn_misc(merged_plmn_search_log, umts_attach_log, lte_attach_log)

    analyze_attach(umts_attach_log, lte_attach_log, lte_tau_log)
    analyze_qos(lte_tau_qos_info, lte_cell_resel_to_umts_config, lte_drx_config, lte_tdd_config)
    return


def print_plmn_search_log(log):
    # analyze
    for span in log:
        assert span.end
        sec = (span.end - span.start).total_seconds()
        print span.start, sec, span.network, (span.from_where if span.from_where else "None")
        for span2 in span.search_log:
            assert span2.end
            sec2 = (span2.end - span2.start).total_seconds()
            print " " * 3, span2.start, sec2, span2.cell_id

        # WCDMA Attach
        umts_attaches = find_spans_between(umts_attach_log, span.start, span.end)
        for span2 in umts_attaches:
            assert span2.end
            sec2 = (span2.end - span2.start).total_seconds()
            print " " * 7, span2.start, sec2, "WCDMA " + span2.response

        # WCDMA RAU
        lus = find_spans_between(umts_lu_log, span.start, span.end)
        for span2 in lus:
            assert span2.end
            sec2 = (span2.end - span2.start).total_seconds()
            print " " * 7, span2.start, sec2, span2.response

        # WCDMA RAU
        raus = find_spans_between(umts_rau_log, span.start, span.end)
        for span2 in raus:
            assert span2.end
            sec2 = (span2.end - span2.start).total_seconds()
            print " " * 7, span2.start, sec2, span2.response

        # LTE Attach
        lte_attaches = find_spans_between(lte_attach_log, span.start, span.end)
        for span2 in lte_attaches:
            assert span2.end
            sec2 = (span2.end - span2.start).total_seconds()
            print " " * 7, span2.start, sec2, "LTE " + span2.response

        # LTE TAU
        taus = find_spans_between(lte_tau_log, span.start, span.end)
        for span2 in taus:
            assert span2.end
            sec2 = (span2.end - span2.start).total_seconds()
            print " " * 7, span2.start, sec2, span2.response


def analyze_plmn_percentile(merged_plmn_search_log):
    duration = [((span.end - span.start).total_seconds(), span.from_where)
                for span in merged_plmn_search_log]
    duration.sort()
    print len(duration)
    print duration

    with open("plmn_percentile.txt", "w") as fd:
        filtered = [(s, where) for s, where in duration if 0 < s < 1200]
        a = np.array([s for s, where in filtered])
        b = np.array([s for s, where in filtered if map_plmn(where) == 1])
        c = np.array([s for s, where in filtered if map_plmn(where) == 2])
        for i in range(0, 100+1):
            p = np.percentile(a, i)
            print >> fd, p, i, 0
        for i in range(0, 100+1):
            p = np.percentile(b, i)
            print >> fd, p, i, 1
        for i in range(0, 100+1):
            p = np.percentile(c, i)
            print >> fd, p, i, 2

    # with open("plmn_searches.txt", "w") as fd:
    #     for s, where in duration:
    #         print >> fd, s, map_plmn(where)


def analyze_plmn_cells(merged_plmn_search_log):
    n_cells = []
    # n_xxxxxx = []
    for span in merged_plmn_search_log:
        cells = set([s.cell_id for s in span.search_log
                        if not s.cell_id.startswith("1x")])
        # att or verizon
        # not_tmo_nor_sprint_cells = set([c for c in cells
        #                                 if c.startswith("LTE/310-410") or c.startswith("LTE/311-480")])
        n_cells.append( (len(cells), map_plmn(span.from_where)) )
        # n_xxxxxx.append(len(not_tmo_nor_sprint_cells))

    with open("plmn_cells.txt", "w") as fd:
        a = np.array([n for n, where in n_cells if where == 1]) # tmo
        b = np.array([n for n, where in n_cells if where == 2]) # sprin
        # b = np.array(n_xxxxxx)
        for i in range(0, 100+1):
        #     print >> fd, i, np.percentile(a, i), np.percentile(b, i)
            print >> fd, i, np.percentile(a, i), np.percentile(b, i)


def analyze_plmn_cells2(merged_plmn_search_log):
    lst = []
    for span in merged_plmn_search_log:
        sec = (span.end - span.start).total_seconds()
        # substract cdma time from total time
        for s in span.search_log:
            if is_cdma_cell(s.cell_id):
                sec -= max((s.end - s.start).total_seconds(), 0)
        cells = set([s.cell_id for s in span.search_log
                    if not is_cdma_cell(s.cell_id)])
        not_tmo_nor_sprint_cells = set([c for c in cells
                                        if is_att_or_verizon_cell(c)])
        ntnsc_time = [(s.end - s.start).total_seconds() for s in span.search_log
                        if s.cell_id in not_tmo_nor_sprint_cells]
        ntnsc_time = [t for t in ntnsc_time if t >= 0]
        lst.append( (len(cells),
                    len(not_tmo_nor_sprint_cells),
                    sec,
                    sum(ntnsc_time),
                    map_plmn(span.from_where)) )
    # Sort by total number of cells
    lst.sort(key=lambda t: (t[-1], t[0]))
    with open("plmn_cells2_1.txt", "w") as fd:
        for a, b, c, d, where in lst:
            if where != 0:
                print >> fd, a, b, c, d, where
    # Sort by total time
    lst.sort(key=lambda t: (t[-1], t[2]))
    with open("plmn_cells2_2.txt", "w") as fd:
        for a, b, c, d, where in lst:
            if where != 0:
                print >> fd, a, b, c, d, where

    all_cells = collections.Counter()
    for span in merged_plmn_search_log:
        all_cells.update([s.cell_id for s in span.search_log])
    for k, v in sorted(all_cells.items()):
        print k, v
    # print "# WCDMA Cells: %d" % len([c for c in all_cells if c.startswith("WCDMA")])
    # print "# LTE Cells: %d" % len([c for c in all_cells if c.startswith("LTE")])



def analyze_plmn_cells_time(merged_plmn_search_log):
    wcdma_cell_time = []
    lte_cell_time = []
    _1xev_cell_time = []
    for s in reduce(lambda s1, s2: s1 + s2,
                    [span.search_log for span in merged_plmn_search_log],
                    []):
        sec = max((s.end - s.start).total_seconds(), 0)
        if s.cell_id.startswith("WCDMA"):
            wcdma_cell_time.append(sec)
        elif s.cell_id.startswith("LTE"):
            lte_cell_time.append(sec)
        elif s.cell_id.startswith("1xEV"):
            _1xev_cell_time.append(sec)
    wcdma_cell_time.sort()
    lte_cell_time.sort()
    _1xev_cell_time.sort()

    for time_lst in [wcdma_cell_time, lte_cell_time, _1xev_cell_time]:
        # print time_lst
        n = int(len(time_lst) * 0.98)
        time_lst = time_lst[0:n]
        if time_lst:
            print len(time_lst), min(time_lst), max(time_lst), sum(time_lst) / len(time_lst), mid(time_lst)

    with open("plmn_cells_time.txt", "w") as fd:
        for span in merged_plmn_search_log:
            for span2 in span.search_log:
                assert span2.end
                sec2 = (span2.end - span2.start).total_seconds()
                print >> fd, span2.start, sec2, span2.cell_id


def analyze_plmn_time(merged_plmn_search_log):
    lst1 = []   # manual, from tmo
    lst2 = []   # manual, from spr
    lst3 = []   # automatic, from tmo
    lst4 = []   # automatic, from spr
    for span in merged_plmn_search_log:
        if any([is_att_or_verizon_cell(s.cell_id) for s in span.search_log]):
            if map_plmn(span.from_where) == 1:
                lst3.append(span)
            elif map_plmn(span.from_where) == 2:
                lst4.append(span)
        else:
            if map_plmn(span.from_where) == 1:
                lst1.append(span)
            elif map_plmn(span.from_where) == 2:
                lst2.append(span)
    print len(lst1), len(lst2), len(lst3), len(lst4)
    def filtered_duration_array(log):
        duration = [(span.end - span.start).total_seconds()
                    for span in log]
        filtered = [t for t in duration if 0.1 < t < 1200]
        return filtered

    print_plmn_search_log(lst1)

    with open("plmn_time.txt", "w") as fd:
        print_percentile(fd, filtered_duration_array(lst1), 1)
        print_percentile(fd, filtered_duration_array(lst2), 2)
        print_percentile(fd, filtered_duration_array(lst3), 3)
        print_percentile(fd, filtered_duration_array(lst4), 4)


def analyze_plmn_misc(merged_plmn_search_log, umts_attach_log, lte_attach_log):
    with open("plmn_misc.txt", "w") as fd:
        for span in merged_plmn_search_log:
            sec = (span.end - span.start).total_seconds()
            umts_attaches = find_spans_between(umts_attach_log, span.start, span.end)
            lte_attaches = find_spans_between(lte_attach_log, span.start, span.end)
            attach_time = sum([(s.end - s.start).total_seconds() for s in umts_attaches
                                if s.response == "Attach Complete"])
            attach_time2 = sum([(s.end - s.start).total_seconds() for s in lte_attaches
                                if s.response == "Attach complete"])
            if sec > 0:
                print >> fd, sec, len(span.search_log), attach_time + attach_time2


def analyze_attach(umts_attach_log, lte_attach_log, lte_tau_log):
    print "# UMTS Attach: %d" % len(umts_attach_log)
    print "# LTE Attach: %d" % len(lte_attach_log)
    print "# LTE TAU: %d" % len(lte_tau_log)


def analyze_qos(lte_tau_qos_info, lte_cell_resel_to_umts_config,
                lte_drx_config, lte_tdd_config):
    print set([info["last_lte_rrc_freq"] for info in lte_tau_qos_info])
    import itertools
    keyfunc = lambda info: info["last_lte_rrc_freq"]
    print "LTE TAU QoS Info"
    infos = sorted(lte_tau_qos_info, key=keyfunc)
    for k, g in itertools.groupby(infos, keyfunc):
        print "Freq: %d" % k
        l = list(g)
        for k2 in ("qci", "delay_class", "traffic_class", "delivery_err_sdu", "traffic_hand_pri", "traffic_hand_pri", "traffic_hand_pri", "apn_ambr_dl_ext", "apn_ambr_ul_ext", "apn_ambr_dl_ext2", "apn_ambr_ul_ext2"):
            print "    " + k2, collections.Counter([info[k2] for info in l])
    print ""

    keyfunc2 = lambda info: info["carrierFreq"]
    print "LTE to UMTS Cell Resel Config"
    infos = sorted(lte_cell_resel_to_umts_config, key=keyfunc2)
    for k, g in itertools.groupby(infos, keyfunc2):
        print "Carrier Freq: %s" % k
        l = list(g)
        for k2 in ( # "lte_rrc_freq",
                    "cellReselectionPriority", "threshX_High", "threshX_Low", "q_RxLevMin", "p_MaxUTRA", "q_QualMin"):
            print "    " + k2, collections.Counter([info[k2] for info in l])
    print ""

    keyfunc3 = lambda info: info["lte_rrc_freq"]
    print "LTE DRX Config"
    infos = sorted(lte_drx_config, key=keyfunc3)
    for k, g in itertools.groupby(infos, keyfunc3):
        print "Freq: %d" % k
        l = list(g)
        for k2 in ("onDurationTimer", "drx_InactivityTimer", "drx_RetransmissionTimer", "shortDRX_Cycle", "drxShortCycleTimer"):
            print "    " + k2, collections.Counter([info[k2] for info in l])
    print ""

    print "LTE TDD Config"
    infos = sorted(lte_tdd_config, key=keyfunc3)
    for k, g in itertools.groupby(infos, keyfunc3):
        print "Freq: %d" % k
        l = list(g)
        for k2 in ("subframeAssignment", "specialSubframePatterns", "si_WindowLength"):
            print "    " + k2, collections.Counter([info[k2] for info in l])
    print ""


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
