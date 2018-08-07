from rest_framework import serializers


class CreateVnfReqSerializer(serializers.Serializer):
    vnfdId = serializers.CharField(
        help_text="Identifier that identifies the VNFD which defines the VNF instance to be created.",
        max_length=255,
        required=True,
        allow_null=True)
    vnfInstanceName = serializers.CharField(
        help_text="Human-readable name of the VNF instance to be created.",
        max_length=255,
        required=False,
        allow_null=True)
    vnfInstanceDescription = serializers.CharField(
        help_text="Human-readable description of the VNF instance to be created.",
        max_length=255,
        required=False,
        allow_null=True)
