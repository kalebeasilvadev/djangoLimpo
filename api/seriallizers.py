from rest_framework.serializers import ModelSerializer
from .models import  Config, User

class ConfigSerializer(ModelSerializer):
    class Meta:
        model = Config
        fields = ('id','host', 'porta', 'automacao', 'ativo',
                  'data_licensa', 'tempo_cmd', 'start_auto','host_app','porta_app','automacao_ativo','emulado','pks')

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username', 'password', 'nivel')
