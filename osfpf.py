#!/usr/bin/env python3

import configparser
import arxiv
import csv
import logging
from osfclient import OSF
import os
import argparse
import threading
import queue


class ConfigsManager:

    def __init__(self, path):
        self.configs = configparser.ConfigParser()
        with open(path, 'r') as f:
            self.configs.read_file(f)

    def _getConfig(self, section, name):
        section_conf = self.configs[section]
        if section_conf is not None:
            return section_conf[name]
        return ""

    def getUsername(self):
        return self._getConfig('ACCOUNT', 'Username')

    def getPassword(self):
        return self._getConfig('ACCOUNT', 'Password')

    def getProject(self):
        return self._getConfig('PROJECT', 'Name')


class ArxivFinder:

    def __init__(self, path):
        self.queries = []
        self.downloads = []
        with open(path, 'r') as f:
            queries = csv.DictReader(f, delimiter=',')
            for buf in queries:
                self.queries.append(buf)

    def find(self, query, max=50, path="./", buf=None):
        results = []
        try:
            logging.info("Searching for {0} ({1} items)".format(query, max))
            results = arxiv.query(query, max_results=int(max))
            for result in results:
                logging.info("Downloading {0} to {1}...".format(results, path))
                download = {
                    "query": query,
                    "path": arxiv.arxiv.download(result, dirpath=path)
                }
                self.downloads.append(download)
                if buf is not None:
                    logging.info("Put to queue {0}".format(download))
                    buf.put(download)
                logging.info("Done.")

        except Exception as ex:
            logging.error(ex)
        finally:
            logging.info("Found {0} papers".format(len(results)))

    def findAll(self, buf=None):
        if self.queries is not None:
            for query in self.queries:
                self.find(query.get('query'), query.get(
                    'max'), query.get('path'), buf)


class OSFClient:

    def __init__(self, username, password, project):
        self.osf = OSF(username=username, password=password)
        self.project = self.osf.project(project)

    def uploadFile(self, folder, path):
        try:
            storage = self.project.storage()
            storage.create_folder(folder, exist_ok=True)

            with open(path, 'rb') as f:
                storage.create_file(folder + '/' + os.path.basename(path), f)
        except Exception as ex:
            logging.error(ex)

    def uploadWorker(self, buf):
        while True:
            item = buf.get()
            folder = item.get('query')
            path = item.get('path')
            logging.info("Uploading from {0} to {1}...".format(path, folder))
            self.uploadFile(folder, path)
            buf.task_done()
            logging.info('Done.')


def main(conf, queries):
    logging.basicConfig(level=logging.INFO)
    manager = ConfigsManager(conf)
    finder = ArxivFinder(queries)
    client = OSFClient(manager.getUsername(),
                       manager.getPassword(), manager.getProject())
    q = queue.Queue()
    threading.Thread(target=client.uploadWorker, args=(q,), daemon=True).start()
    finder.findAll(q)
    q.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', required=True, help="Config file")
    parser.add_argument('-t', '--table', required=True,
                        help="CVS file with queries")
    args = parser.parse_args()
    main(args.config, args.table)
