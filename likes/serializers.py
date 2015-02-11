# encoding: utf-8

# Third Party Stuff
from django.contrib.auth import get_user_model
from rest_framework import serializers


class LikerSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', required=False)

    class Meta():
        model = get_user_model()
        fields = ('id', 'username', 'full_name')
