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
import types
import unittest
import logging as log
log.getLogger('defaults')

import autograd.numpy as np

import collections

from defaults import pennylane as qml, BaseTest

from pennylane.utils import flatten, unflatten

a = np.linspace(-1, 1, 64)
a_shapes = [(64,),
            (64, 1),
            (32, 2),
            (16, 4),
            (8, 8),
            (16, 2, 2),
            (8, 2, 2, 2),
            (4, 2, 2, 2, 2),
            (2, 2, 2, 2, 2, 2)]

b = np.linspace(-1., 1., 8)
b_shapes = [(8,), (8, 1), (4, 2), (2, 2, 2), (2, 1, 2, 1, 2)]


class FlattenTest(BaseTest):
    """Tests flatten and unflatten.
    """
    def mixed_iterable_equal(self, a, b):
        """We need a way of comparing nested mixed iterables that also
        checks that the types of sub-itreables match and that those
        of the elements compare to equal. This method does that.
        """
        print("called with ("+str(a)+", "+str(b)+") of types "+str(type(a))+("!=" if type(a) != type(b) else "=")+str(type(b)))
        if isinstance(a, types.GeneratorType):
            a = list(a)
        if isinstance(b, types.GeneratorType):
            b = list(b)
        if isinstance(a, collections.Iterable) or isinstance(b, collections.Iterable):
            if type(a) != type(b):
                print("returning False because type(a)="+str(type(a))+"!="+str(type(b))+"=type(b)")
                return False
            a_len = a.size if isinstance(a, np.ndarray) else len(a)
            b_len = b.size if isinstance(b, np.ndarray) else len(b)
            if a_len != b_len:
                print("returning False because a_len="+str(a_len)+"!="+str(b_len)+"=b_len")
                return False
            if a_len > 1:
                return np.all([self.mixed_iterable_equal(a[i], b[i]) for i in range(a_len)])

        return a == b


    def test_depth_first_jagged_list(self):
        r = list(range(5))
        a = [[0, 1, [2, 3]], 4]
        self.assertEqual(list(flatten(a)), r)
        self.assertEqual(list(unflatten(r, a)), a)
        assert(self.mixed_iterable_equal(flatten(a), r))#flatten() returns a generator here and this is what we want
        assert(self.mixed_iterable_equal(unflatten(r, a), a))


    def test_depth_first_jagged_mixed(self):
        r = np.array(range(17))
        a = [np.array([np.array([0]), np.array([1, 2, 3]), np.array([4, 5])]), 6, np.array([7, 8]), (9, 10), [11, (12, np.array(13)), np.array([(14, ), 15, np.array(16)])]]
        assert(self.mixed_iterable_equal(list(flatten(a)), list(r)))#todo: remove list() around flatten?

        a_unflattened = unflatten(r, a)
        assert(self.mixed_iterable_equal(a_unflattened, a))


    def test_flatten_list(self):
        "Tests that flatten successfully flattens multidimensional arrays."
        self.logTestName()
        flat = a
        for s in a_shapes:
            reshaped = list(np.reshape(flat, s))
            flattened = np.array([x for x in flatten(reshaped)])

            self.assertEqual(flattened.shape, flat.shape)
            self.assertAllEqual(flattened, flat)


    def test_unflatten_list(self):
        "Tests that _unflatten successfully unflattens multidimensional arrays."
        self.logTestName()
        flat = a
        for s in a_shapes:
            reshaped = list(np.reshape(flat, s))
            unflattened = np.array([x for x in unflatten(flat, reshaped)])

            self.assertEqual(unflattened.shape, np.array(reshaped).shape)
            self.assertAllEqual(unflattened, reshaped)

        with self.assertRaisesRegex(TypeError, 'Unsupported type in the model'):
            model = lambda x: x # not a valid model for unflatten
            unflatten(flat, model)

        with self.assertRaisesRegex(ValueError, 'Flattened iterable has more elements than the model'):
            unflatten(np.concatenate([flat, flat]), reshaped)


    def test_flatten_np_array(self):
        "Tests that flatten successfully flattens multidimensional arrays."
        self.logTestName()
        flat = a
        for s in a_shapes:
            reshaped = np.reshape(flat, s)
            flattened = np.array([x for x in flatten(reshaped)])

            self.assertEqual(flattened.shape, flat.shape)
            self.assertAllEqual(flattened, flat)


    def test_unflatten_np_array(self):
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
