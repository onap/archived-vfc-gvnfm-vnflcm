
from rest_framework import serializers

from cp_protocol_info import CpProtocolInfoSerializer


class VnfcCpInfoSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of the external CP instance and the related information instance.",
        max_length=255,
        required=True,
        allow_null=False,
        allow_blank=False)
    cpdId = serializers.CharField(
        help_text="Identifier of the external CPD, VnfExtCpd, in the VNFD.",
        max_length=255,
        required=True,
        allow_null=False,
        allow_blank=False)
    vnfExtCpId = serializers.CharField(
        help_text="When the VNFC CP is exposed as external CP of the VNF, the identifier of this external VNF CP.",
        required=False,
        max_length=255,
        allow_null=True,
        allow_blank=True)
    cpProtocolInfo = CpProtocolInfoSerializer(
        help_text="Network protocol information for this CP.",
        many=True,
        required=False,
        allow_null=True)
    vnfLinkPortId = serializers.CharField(
        help_text="Identifier of the vnfLinkPorts structure in the vnfVirtualLinkResourceInfo structure.",
        max_length=255,
        required=True,
        allow_null=False,
        allow_blank=False)
