#!/usr/bin/python
from mobile_insight.monitor import OfflineReplayer
from mobilitymisconfiggsm_analyzer import MobilityMisconfigGsmAnalyzer
import collections
import numpy as np
import os
import pickle
import re
import sys
import json

def get_sorted_logs(fileMi2logText):
    content = []
    with open(fileMi2logText) as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    return content

def parse_qmdl(plainTextFile):
    # Initialize an OfflineReplayer as monitor
    src = OfflineReplayer()
    m = MobilityMisconfigGsmAnalyzer()

    for f in get_sorted_logs(plainTextFile):
        print '=========' + f + '========'
        m.reset()
        m.set_source(src)
        src.set_input_path(f)

        # Start the monitoring
        src.run()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage python main_gsm.py [plain text file containing path to mi2log files]"
        exit()
    parse_qmdl(sys.argv[1])
