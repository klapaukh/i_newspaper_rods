from unittest import TestCase

from ...model.corpus import Corpus

import numpy as np

class test_corpus(TestCase):
    def setUp(self):
        #from mpi4py import MPI
        self.communicator=None
        self.source='/rdZone/live/rd009s/2TB-Drive-Transfer-06-07-q2016/TDA_GDA_1785-2009'
        self.corpus=Corpus(self.source, self.communicator)
    def test_count(self):
        assert(len(self.corpus)==75503)
