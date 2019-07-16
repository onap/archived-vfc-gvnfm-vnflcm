# Copyright (C) 2019 ZTE. All Rights Reserved
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

import logging

from lcm.pub.database.models import SubscriptionModel
from lcm.pub.exceptions import NFLCMException

logger = logging.getLogger(__name__)


class DeleteSubscription:
    def __init__(self, subscription_id):
        self.subscription_id = subscription_id

    def delete_single_subscription(self):
        subscription = SubscriptionModel.objects.filter(subscription_id=self.subscription_id)
        if not subscription.exists():
            raise NFLCMException('Subscription(%s) does not exist' % self.subscription_id)
        subscription.delete()
