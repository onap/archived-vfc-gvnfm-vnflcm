# Copyright 2018 ZTE Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from lcm.pub.verifyvnfd import verifyvnfd
from . import const
from lcm.pub.exceptions import NFLCMException


class VerifyVnfdTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_vnfd_verfify_success1(self):
        ret = verifyvnfd.verify(const.vnfd_model1)
        self.assertEqual(ret, True)

    def test_vnfd_verfify_success2(self):
        ret = verifyvnfd.verify(const.vnfd_model2)
        self.assertEqual(ret, True)

    def test_vnfd_verfify_success3(self):
        ret = verifyvnfd.verify(const.vnfd_model3)
        self.assertEqual(ret, True)

    def test_vnfd_verfify_fail_for_missing_required(self):
        ret = verifyvnfd.verify(const.vnfd_model_miss_required)
        self.assertNotEqual(ret, "")
