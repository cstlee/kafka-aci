#!/usr/bin/env python

# ISC License
#
# Copyright (c) 2017, Stanford University
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE
# OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.



'''Deploy Kafka clusters with one command.

Usage:
    cluster.py start
    cluster.py stop
    cluster.py ssh <ssh_arg>...
'''

from docopt import docopt
import subprocess
import os
import time
import StringIO
import re
import pickle

from localconfig import *

def start():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    root_dir = os.path.dirname(script_dir)
    ids = {}

    for ip in (zookeeper_ip, broker_ip):
        print("******** Sync to {0} ********".format(ip))
        subprocess.call(["rsync", "-r",
                         "{0}/aci/".format(root_dir),
                         "{0}:/tmp/kafka/".format(ip)])

    # Start Zookeeper
    print("******** Start Zookeeper at {0} ********".format(zookeeper_ip))
    proc = subprocess.Popen(["ssh", "root@{0}".format(zookeeper_ip),
            "systemd-run", "rkt", "run", "--insecure-options=image",
            "--net=host", "/tmp/kafka/zookeeper.aci"], stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
    proc.wait()
    out, err = proc.communicate()
    print(out)
    ids[zookeeper_ip] = getUnitId(out)

    time.sleep(5)

    # Start Broker
    print("******** Start Broker at {0} ********".format(broker_ip))
    proc = subprocess.Popen(["ssh", "root@{0}".format(broker_ip),
            "systemd-run", "rkt", "run", "--insecure-options=image",
            "--net=host", "/tmp/kafka/kafka.aci", "--",
            "--override broker.id=0",
            "--override listeners=PLAINTEXT://{0}:9092".format(broker_ip),
            "--override zookeeper.connect={0}:2181".format(zookeeper_ip)],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    proc.wait()
    out, err = proc.communicate()
    print(out)
    ids[broker_ip] = getUnitId(out)

    outfile = open("{0}/clusterpid".format(script_dir), 'wb')
    pickle.dump(ids, outfile)
    outfile.close()

def getUnitId(output):
    return re.search('Running as unit (run-[0-9]*\.service)\.', output).group(1)

def stop():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    infile = open("{0}/clusterpid".format(script_dir), 'rb')
    ids = pickle.load(infile)
    infile.close()

    print("******** Stop Broker at {0} ********".format(broker_ip))
    subprocess.call(["ssh", "root@{0}".format(broker_ip), "systemctl",
            "stop", ids[broker_ip]])

    time.sleep(5)

    print("******** Stop Zookeeper at {0} ********".format(zookeeper_ip))
    subprocess.call(["ssh", "root@{0}".format(zookeeper_ip), "systemctl",
            "stop", ids[zookeeper_ip]])

def ssh(args):
    for ip in (zookeeper_ip, broker_ip):
        print("******** Output from {0} ********".format(ip))
        subprocess.call(["ssh", "root@{0}".format(ip)] + args)

if __name__ == '__main__':
    arguments = docopt(__doc__, version='cluster.py 0.0.1')

    if arguments['start']:
        start()
    elif arguments['stop']:
        stop()
    elif arguments['ssh']:
        ssh(arguments['<ssh_arg>'])
