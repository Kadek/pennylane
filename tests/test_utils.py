# Copyright 2018 Xanadu Quantum Technologies Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Unit tests for the :mod:`pennylane.utils` sub-module.
"""

import unittest
import logging as log
log.getLogger('defaults')

import autograd
from autograd import numpy as np

from defaults import pennylane as qml, BaseTest

from pennylane.qnode import _flatten, unflatten

a = np.linspace(-1,1,64)
a_shapes = [(64,),
            (64,1),
            (32,2),
            (16,4),
            (8,8),
            (16,2,2),
            (8,2,2,2),
            (4,2,2,2,2),
            (2,2,2,2,2,2)]

b = np.linspace(-1., 1., 8)
b_shapes = [(8,), (8,1), (4,2), (2,2,2), (2,1,2,1,2)]


class FlattenTest(BaseTest):
    """Tests flatten and unflatten.
    """
    def test_flatten(self):
        "Tests that _flatten successfully flattens multidimensional arrays."
        self.logTestName()
        flat = a
        for s in a_shapes:
            reshaped = np.reshape(flat, s)
            flattened = np.array([x for x in _flatten(reshaped)])

            self.assertEqual(flattened.shape, flat.shape)
            self.assertAllEqual(flattened, flat)


    def test_unflatten(self):
        "Tests that _unflatten successfully unflattens multidimensional arrays."
        self.logTestName()
        flat = a
        for s in a_shapes:
            reshaped = np.reshape(flat, s)
            unflattened = np.array([x for x in unflatten(flat, reshaped)])

            self.assertEqual(unflattened.shape, reshaped.shape)
            self.assertAllEqual(unflattened, reshaped)

        with self.assertRaisesRegex(TypeError, 'Unsupported type in the model'):
            model = lambda x: x # not a valid model for unflatten
            unflatten(flat, model)

        with self.assertRaisesRegex(ValueError, 'Flattened iterable has more elements than the model'):
            unflatten(np.concatenate([flat, flat]), reshaped)


if __name__ == '__main__':
    print('Testing PennyLane version ' + qml.version() + ', utils sub-module.')
    # run the tests in this file
    suite = unittest.TestSuite()
    for t in (FlattenTest,):
        ttt = unittest.TestLoader().loadTestsFromTestCase(t)
        suite.addTests(ttt)

    unittest.TextTestRunner().run(suite)