import datetime
import os
import subprocess
import sys

def get_pcap_files(path):
    content = []
    with open(path) as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    return content

# In seconds
timeBin = 0.1

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage get_throughput.py [path_pcap_file]"
        exit()
    path = sys.argv[1]
    files_pcap = get_pcap_files(path)
    for file_pcap in files_pcap:
        cmd = "tcpdump -r %s src 2607:7700:0:1f:0:1:800a:7e20 -tttt"
        proc = subprocess.Popen(cmd%(file_pcap), \
                shell=True, stdout=subprocess.PIPE)

        firstline = str(proc.stdout.readline()).strip()
        tupleLine = firstline.split(' ')
        try:
            strTimestamp = tupleLine[0] + " " + tupleLine[1]
        except:
            continue
        datetimeStart = datetime.datetime.strptime(strTimestamp, "%Y-%m-%d %H:%M:%S.%f")
        tupleLine = firstline.split(',')
        try:
            accumulatedPayload = int(tupleLine[7].split(' ')[2][:-1])
        except:
            accumulatedPayload = 0

        for line in iter(proc.stdout.readline, ""):
            line = line.strip()
            tupleLine = line.split(' ')
            strTimestamp = tupleLine[0] + " " + tupleLine[1]
            datetimeTimestamp = datetime.datetime.strptime(strTimestamp, "%Y-%m-%d %H:%M:%S.%f")
            tupleLine = line.split(',')
            try:
                bytePayload = int(tupleLine[7].split(' ')[2][:-1])
            except:
                bytePayload = 0

            if datetimeTimestamp < datetimeStart + datetime.timedelta(seconds = timeBin):
                accumulatedPayload += bytePayload
            else:
                accumulatedPayload += bytePayload
                total_seconds = (datetimeTimestamp - datetimeStart).total_seconds()
                throughput = accumulatedPayload * 8.0 / total_seconds
                print datetimeTimestamp, throughput
                datetimeStart = datetimeTimestamp
                accumulatedPayload = 0

