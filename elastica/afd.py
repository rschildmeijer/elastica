from time import time
import math

class AccrualFailureDetector(object):
    """ Python implementation of 'The Phi Accrual Failure Detector'
    by Hayashibara et al.

    (Original version by Brandon Williams (github.com/driftx), modified by Roger Schildmeijer (github.com/rchildmeijer))

    Failure detection is the process of determining which nodes in a distributed fault-tolerant system have failed.
    Original Phi Accrual Failure Detection paper: http://ddg.jaist.ac.jp/pub/HDY+04.pdf"""

    max_sample_size = 1000
    threshold = 3 # 1 = 10% error rate, 2 = 1%, 3 = 0.1%.., (eg threshold=3. no heartbeat for >6s => node marked as dead

    def __init__(self):
        self._intervals = {}
        self._hosts = {}
        self._timestamps = {}

    def heartbeat(self, host):
        """ Call when host has indicated being alive (aka heartbeat) """
        if not self._timestamps.has_key(host):
            self._timestamps[host] = time()
            self._intervals[host] = []
            self._hosts[host] = {}
        else:
            now = time()
            interval = now - self._timestamps[host]
            self._timestamps[host] = now
            self._intervals[host].append(interval)
            if len(self._intervals) > self.max_sample_size:
                self._intervals.pop(0)
            if len(self._intervals[host]) > 1:
                self._hosts[host]['mean'] = sum(self._intervals[host]) / float(len(self._intervals[host]))
                ### lines below commented because deviation and variance are currently unused
                #deviationsum = 0
                #for i in self._intervals[host]:
                # deviationsum += (i - self._hosts[host]['mean']) ** 2
                #variance = deviationsum / float(len(self._intervals[host]))
                #deviation = math.sqrt(variance)
                #self._hosts[host]['deviation'] = deviation

    def _probability(self, host, timestamp):
        # cassandra does this, citing: /* Exponential CDF = 1 -e^-lambda*x */
        # but the paper seems to call for a probability density function
        # which I can't figure out :/
        exponent = -1.0 * timestamp / self._hosts[host]['mean']
        return 1 - ( 1.0 - math.pow(math.e, exponent))

    def phi(self, host, timestamp=None):
        if not self._hosts[host]:
            return 0
        ts = timestamp
        if ts is None:
            ts = time()
        diff = ts - self._timestamps[host]
        prob = self._probability(host, diff)
        return -1 * math.log10(prob)

    def isAlive(self, host):
        return self.phi(host) < self.threshold

    def isDead(self, host):
        return not self.isAlive(host)

    def reconcile(self):
        print "impls"