from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from token_jwt.authentication import JWTAuthentication
from datetime import datetime, timedelta
from dateutil.relativedelta import *
from .models import Config, User
from .seriallizers import ConfigSerializer, UserSerializer

from api.services.cripto import *
    
class ConfigViewSet(viewsets.ModelViewSet):
    queryset = Config.objects.all()
    serializer_class = ConfigSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def partial_update(self, request, *args, **kwargs):
        config_cad = Config.objects.filter(id=kwargs['pk'])
        config_cad.update(host=request.data['host'], porta=request.data['porta'], automacao=request.data['automacao'],
                          tempo_cmd=request.data['tempo_cmd'], start_auto=request.data['start_auto'], host_app=request.data['host_app'],
                          porta_app=request.data['porta_app'],emulado=request.data['emulado'])

        data = {
            "host": request.data['host'],
            "porta": request.data['porta'],
            "automacao": request.data['automacao'],
            "tempo_cmd": request.data['tempo_cmd'],
            "start_auto": request.data['start_auto'],
            "porta_app": request.data['porta_app'],
            "host_app": request.data['host_app'],
        }
        return Response(data)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('id', 'username', 'nivel')
    lookup_field = 'username'

    def create(self, request, *args, **kwargs):
        user_cad = User.objects.create(
            username=request.data['username'], password=request.data['password'], nivel=request.data['nivel'])
        user_cad.save()
        user_cad = User.objects.get(username=request.data['username'])
        user_cad.set_password(request.data['password'])
        user_cad.save()

        data = {
            "username": request.data['username'],
            "nivel": request.data['nivel'],
        }
        return Response(data)

    def partial_update(self, request, *args, **kwargs):
        user_cad = User.objects.filter(username=kwargs['username'])
        user_cad.update(nivel=request.data['nivel'])
        if request.data['password'][0:3] != "pbk":
            user_cad = User.objects.get(username=kwargs['username'])
            user_cad.set_password(request.data['password'])
            user_cad.save()

        data = {
            "username": kwargs['username'],
            "nivel": request.data['nivel'],
        }
        return Response(data)
