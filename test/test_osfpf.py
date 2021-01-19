import csv
import os
import string
import random
import tempfile
import osfpf
import unittest
import sys
sys.path.append('../')


class OSFPFTest(unittest.TestCase):

    def test_config_manager(self):
        username = 'Test'
        password = 'Password'
        project = 'odvrfg3'
        tmp = '/tmp/' + \
            ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        with open(tmp, 'w+') as f:
            f.write("[ACCOUNT]\nUsername={0}\nPassword={1}\n\n[PROJECT]\nName={2}\n".format(
                username, password, project))
        manager = osfpf.ConfigsManager(tmp)
        self.assertEqual(username, manager.getUsername())
        self.assertEqual(password, manager.getPassword())
        self.assertEqual(project, manager.getProject())
        os.remove(tmp)

    def test_arxiv_finder(self):
        queries = ['Neural Networks', 'CNN', 'Image Classification']
        m = 1
        path = '/tmp/'
        tmp = '/tmp/' + \
            ''.join(random.choices(string.ascii_letters +
                                   string.digits, k=16)) + '.csv'
        with open(tmp, 'w+', newline='') as csvfile:
            testwriter = csv.writer(csvfile, delimiter=',')
            testwriter.writerow(['query',  'max', 'path'])
            for query in queries:
                testwriter.writerow([query, m, path])
        finder = osfpf.ArxivFinder(tmp)
        finder.findAll()
        self.assertGreater(len(finder.downloads), 0)
        self.assertLessEqual(len(finder.downloads), 3)
        for download in finder.downloads:
            self.assertIsNotNone(download.get('query'))
            self.assertIsNotNone(download.get('path'))