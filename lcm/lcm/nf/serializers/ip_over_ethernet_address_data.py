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
from ip_addresse import IpAddresseSerializer


class IpOverEthernetAddressDataSerializer(serializers.Serializer):
    macAddress = serializers.CharField(
        help_text="MAC address. If this attribute is not present, \
        it shall be chosen by the VIM.",
        required=False,
        allow_null=True,
        allow_blank=True)
    ipAddresses = IpAddresseSerializer(
        help_text="List of IP addresses to assign to the CP instance. \
        Each entry represents IP address data for fixed or dynamic IP address assignment per subnet.",
        many=True,
        required=False,
        allow_null=True)
