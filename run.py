#!/usr/bin/python
import linux_metrics as metric
import pymongo
import time
import tornado.ioloop


class obj(dict):
    def __getattr__(self, attr):
        return self.get(attr, None)
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


##dot notation.
config = obj()


##Basic setup
config.mongo_ip = 'localhost'
config.mongo_port = 27017
config.db = 'events'
config.metrics_collection = 'test_collection'
config.run_interval_ms = 1000
##Setup done


class Collector(object):

    @classmethod
    def collectMetrics(self):

        _db = pymongo.Connection(config.mongo_ip, config.mongo_port)
        db = _db[config.db]

        collection = db[config.metrics_collection]
        report = obj()

        report.cputime = metric.cpu_stat.procs_running()
        report.cpu_percent = metric.cpu_stat.cpu_percents(sample_duration=3)
        report.memory = metric.mem_stat.mem_stats()
        report.procs_blocking = metric.cpu_stat.procs_blocked()
        report.load = metric.cpu_stat.load_avg()
        report.network_in = metric.net_stat.rx_tx_bytes('eth0')
        report.stamp = int(time.time())

        collection.insert(report, safe=False)
        _db.end_request()


def main():

    io = tornado.ioloop.IOLoop.instance()
    try:
        reportLoop = tornado.ioloop.PeriodicCallback(Collector.collectMetrics,
            (config.run_interval_ms),
            io_loop=io)
        reportLoop.start()
    except Exception, e:
        raise e

    io.start()

if __name__ == '__main__':
    main()
