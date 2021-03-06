# -*- coding: utf-8 -*-
# The MIT License (MIT)
#
# Copyright (c) 2018 Laura Fernandez Robles,
#                    Hector Alaiz Moreton,
#                    Jaime Cifuentes-Rodriguez,
#                    Javier Alfonso-Cendón,
#                    Camino Fernández-Llamas,
#                    Manuel Castejón-Limas
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import logging
import unittest
import numpy as np
from sklearn.naive_bayes import GaussianNB
from sklearn.cluster import DBSCAN
from sklearn.linear_model import LinearRegression
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import MinMaxScaler
from pipegraph.base import add_mixins_to_step
from pipegraph.adapters import (FitTransformMixin,
                                FitPredictMixin,
                                AtomicFitPredictMixin,
                                CustomFitPredictWithDictionaryOutputMixin)

class TestAdapterForSkLearnLikeAdaptee(unittest.TestCase):
    def setUp(self):
        self.size = 100
        self.X = np.random.rand(self.size, 1)
        self.y = self.X + np.random.randn(self.size, 1)

    def test_baseadapter__get_fit_signature(self):
        lm = LinearRegression()
        gm = GaussianMixture()
        lm.__class__ = type('newClass', (type(lm), FitPredictMixin), {} )
        gm.__class__ = type('newClass', (type(gm), FitPredictMixin), {} )

        result_lm = lm._get_fit_signature()
        result_gm = gm._get_fit_signature()

        self.assertEqual(sorted(result_lm), sorted(['X', 'y', 'sample_weight']))
        self.assertEqual(sorted(result_gm), sorted(['X', 'y']))



class TestFitTransformMixin(unittest.TestCase):
    def setUp(self):
        self.size = 100
        self.X = np.random.rand(self.size, 1)
        self.y = self.X + np.random.randn(self.size, 1)

    def test_FitTransform__predict(self):
        X = self.X
        sc = MinMaxScaler()
        sc.__class__ = type('newClass', (type(sc), FitTransformMixin), {})
        sc.fit_using_varargs(X=X)
        result_sc = sc.predict_dict(X=X)
        self.assertEqual(list(result_sc.keys()), ['predict'])
        self.assertEqual(result_sc['predict'].shape, (self.size, 1))

    def test_FitTransform__get_predict_signature(self):
        sc = MinMaxScaler()
        sc.__class__ = type('newClass', (type(sc), FitTransformMixin), {})
        result_sc = sc._get_predict_signature()
        self.assertEqual(result_sc, ['X'])


class TestFitPredictMixin(unittest.TestCase):
    def setUp(self):
        self.size = 100
        self.X = np.random.rand(self.size, 1)
        self.y = self.X + np.random.randn(self.size, 1)

    def test_FitPredict__predict(self):
        X = self.X
        y = self.y
        lm = LinearRegression()
        lm.__class__ = type('newClass', (type(lm), FitPredictMixin), {})
        lm.fit(X=X, y=y)
        result_lm = lm.predict_dict(X=X)
        self.assertEqual(list(result_lm.keys()), ['predict'])
        self.assertEqual(result_lm['predict'].shape, (self.size, 1))

        gm = GaussianMixture()
        gm.__class__ = type('newClass', (type(gm), FitPredictMixin), {})
        gm.fit_using_varargs(X=X)
        result_gm = gm.predict_dict(X=X)
        self.assertEqual(sorted(list(result_gm.keys())),
                         sorted(['predict', 'predict_proba']))
        self.assertEqual(result_gm['predict'].shape, (self.size,))

    def test_FitPredict__get_predict_signature(self):
        lm = LinearRegression()
        lm.__class__ = type('newClass', (type(lm), FitPredictMixin), {})
        result_lm = lm._get_predict_signature()
        self.assertEqual(result_lm, ['X'])

class TestAtomicFitPredictMixin(unittest.TestCase):
    def setUp(self):
        self.size = 100
        self.X = np.random.rand(self.size, 1)
        self.y = self.X + np.random.randn(self.size, 1)

    def test_AtomicFitPredictMixin__predict(self):
        X = self.X
        y = self.y
        db = DBSCAN()
        db.__class__ = type('newClass', (type(db), AtomicFitPredictMixin), {})
        db.fit(X=X, y=y)
        result_db = db.predict_dict(X=X)
        self.assertEqual(list(result_db.keys()), ['predict'])
        self.assertEqual(result_db['predict'].shape, (self.size,))

    def test_AtomicFitPredictMixin__get_predict_signature(self):
        db = DBSCAN()
        db.__class__ = type('newClass', (type(db), AtomicFitPredictMixin), {})
        result_db = db._get_predict_signature()
        self.assertEqual(sorted(result_db), sorted(['X', 'y', 'sample_weight']))

class TestCustomFitPredictWithDictionaryOutputMixin(unittest.TestCase):
    def setUp(self):
        self.size = 100
        self.X = np.random.rand(self.size, 1)
        self.y = self.X + np.random.randn(self.size, 1)

    def test_FitPredictWithDictionaryOutput__predict(self):
        X = self.X
        y = self.y.astype(int)
        gm = GaussianNB()
        wrapped_gm = add_mixins_to_step(gm)
        double_wrap= add_mixins_to_step(wrapped_gm)

        double_wrap.fit(X=X, y=y)
        result = double_wrap.predict_dict(X=X)
        self.assertEqual(sorted(list(result.keys())),
                         sorted(['predict', 'predict_proba', 'predict_log_proba']))
        self.assertEqual(result['predict'].shape[0], self.size)
        self.assertEqual(result['predict_proba'].shape[0], self.size)
        self.assertEqual(result['predict_log_proba'].shape[0], self.size)

    def test_FitPredictWithDictionaryOutput__get_fit_signature(self):
        lm = LinearRegression()
        wrapped_lm = add_mixins_to_step(lm)
        double_wrap= add_mixins_to_step(wrapped_lm)
        result = double_wrap._get_fit_signature()
        self.assertEqual(sorted(result), sorted(['X', 'y', 'sample_weight']))

    def test_FitPredictWithDictionaryOutput__get_predict_signature(self):
        lm = LinearRegression()
        wrapped_lm = add_mixins_to_step(lm)
        double_wrap= add_mixins_to_step(wrapped_lm)
        result = double_wrap._get_predict_signature()
        self.assertEqual(result, ['X'])


if __name__ == '__main__':
    unittest.main()
