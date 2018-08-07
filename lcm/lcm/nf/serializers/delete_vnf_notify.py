from rest_framework import serializers


class VnfIdentifierDeletionNotification(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of the VNF instance",
        required=True,
        max_length=255,
        allow_null=True)
