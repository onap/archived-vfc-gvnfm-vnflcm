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

from rest_framework import serializers
from address_range import AddressRangeSerializer


class IpAddresseSerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        help_text="The type of the IP addresses.",
        choices=["IPV4", "IPV6"],
        required=True,
        allow_null=False,
        allow_blank=False)
    fixedAddresses = serializers.ListSerializer(
        help_text="Fixed addresses to assign.",
        child=serializers.CharField(help_text="IpAddress"),
        required=False,
        allow_null=True)
    numDynamicAddresses = serializers.IntegerField(
        help_text="Number of dynamic addresses to assign.",
        required=False,
        allow_null=True)
    addressRange = AddressRangeSerializer(
        help_text="An IP address range to be used, e.g. in case of egress connections. \
        In case this attribute is present, IP addresses from the range will be used.",
        required=False,
        allow_null=True, )
    subnetId = serializers.CharField(
        help_text="Subnet defined by the identifier of the subnet resource in the VIM. \
        In case this attribute is present, IP addresses from that subnet will be assigned; \
        otherwise, IP addresses not bound to a subnet will be assigned.",
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=True)
