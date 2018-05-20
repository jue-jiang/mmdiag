import os
import sys
from datetime import datetime
import datetime
import collections
from numpy import median

# strSearch = "2018/01/25/05:15:02.241674"
margin = datetime.timedelta(seconds=2)

def check_throughput(datetimeSearch, content, index):
    strDate = datetimeSearch.strftime("%b_%d")
    listthroughput = []
    for x in range(index, len(content)):
        line = content[x]
        data = line.split(' ')
        strTimestamp = data[0] + " " + data[1]
        throughput = float(data[2])
        datetimeLine = datetime.datetime.strptime(strTimestamp, "%Y-%m-%d %H:%M:%S.%f")
        if datetimeLine < datetimeSearch - margin:
            continue
        elif datetimeLine < datetimeSearch + margin:
            listthroughput.append(throughput)
        else:
            index = x - 40
            break
    if len(listthroughput) > 0:
        return min(listthroughput), index
    else:
        return -1, index



if __name__ == "__main__":

    if len(sys.argv) != 3:
        print "usage match_throughput [throughput file (sorted in timestamp)] [active event file]"
        exit()

    file_throughput = sys.argv[1]
    file_active = sys.argv[2]

    with open(file_throughput) as f:
        content = f.readlines()
    content_throughput = [x.strip() for x in content]

    with open(file_active) as f:
        events = f.readlines()
    events = [x.strip() for x in events]

    dictEvents = {}
    for event in events:
        line = event.split(' ')
        strSearch = line[16]
        datetimeSearch = datetime.datetime.strptime(strSearch, "%Y/%m/%d/%H:%M:%S.%f")
        dictEvents[datetimeSearch] = event

    orderedDictEvents = collections.OrderedDict(sorted(dictEvents.items()))
    events = []
    for key, value in orderedDictEvents.iteritems():
        events.append(value)

    index = 0
    for event in events:
        line = event.split(' ')
        strSearch = line[16]
        datetimeSearch = datetime.datetime.strptime(strSearch, "%Y/%m/%d/%H:%M:%S.%f")
        throughput, index = check_throughput(datetimeSearch, content_throughput, index)
        if throughput == -1:
            throughput = "Unknown"
        print event, throughput
