from rest_framework import generics,status
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView,
                                            TokenVerifyView)
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail as send2
from django.conf import settings
from accounts.models import User,Profile
from .serializers import *
from ..utils import *
from mail_templated import send_mail,EmailMessage
from jwt.exceptions import ExpiredSignatureError,InvalidSignatureError
import jwt

class RegistrationApiView(TokenForUserMixin,generics.GenericAPIView):
    serializer_class = RegistrationSerializer
    def post(self, request, *args, **kwargs):
        serializer = RegistrationSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            email = serializer.validated_data['email']
            data = {
                'email' : email
            }
            user_obj = get_object_or_404(User,email=email)
            token = self.get_tokens_for_user(user_obj)
            email_obj = EmailMessage('email/activation_email.tpl',
                                {'token': token},
                                'admin@admin.com',
                                to=[email])
            EmailThread(email_obj).start()
            return Response(data)
        return Response(serializer.errors)

class CustomObtainAuthToken(ObtainAuthToken):
    serializer_class = CustomAuthTokenSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })
    

class CustomDiscardAuthToken(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class ChangePasswordApiView(generics.GenericAPIView):
    model = User
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def get_object(self,queryset=None):
        obj = self.request.user
        return obj
    
    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get('old_password')):
                return Response({'old_password' : ['wrong password']},status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get('new_password'))
            self.object.save()
            return Response({'details' : 'password changed very gooooooooood!'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class ProfileApiView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return get_object_or_404(Profile,user=self.request.user)
    def update(self, request, *args, **kwargs):
        response = self.update(request, *args, **kwargs)
        response.data['message'] = 'Changes were done successfully!'
        return response

#test class for testing email system!
class TestEmailSend(TokenForUserMixin,generics.GenericAPIView):
    def get(self,request,*args,**kwargs):
        self.email = 'test@test.com'
        user_obj = get_object_or_404(User,email=self.email)
        token = self.get_tokens_for_user(user_obj)
        email_obj = EmailMessage('email/hello.tpl',
                                {'token': token},
                                'admin@admin.com',
                                to=[self.email])
        EmailThread(email_obj).start()
        return Response('email sent!')
    


class ActivationApiView(APIView):
    def get(self,request,token,*args,**kwargs):
        try:
            token = jwt.decode(token,settings.SECRET_KEY,algorithms=['HS256'])
            user_id = token.get('user_id')
        except ExpiredSignatureError:
            return Response({'detail' : 'token expired!'},status=status.HTTP_400_BAD_REQUEST)
        except InvalidSignatureError:
            return Response({'detail' : 'token not valid!'},status=status.HTTP_400_BAD_REQUEST)
        user_obj = User.objects.get(pk = user_id)
        if not user_obj.is_verified:
            user_obj.is_verified = True
            user_obj.is_active = True
            user_obj.save()
            return Response({'detail' : 'ur acc activated successfully!'})
        else:
            return Response({'detail' : 'ur acc is already activated!'})

        
class ActivationResendApiView(TokenForUserMixin,generics.GenericAPIView):
    serializer_class = ActivationResendSerializer
    def post(self,request,*args,**kwargs):
        serializer = ActivationResendSerializer(data = request.data)
        if serializer.is_valid():
            user_obj = serializer.validated_data['user']
            token = self.get_tokens_for_user(user_obj)
            email_obj = EmailMessage('email/activation_email.tpl',
                                     {'token': token},
                                    'admin@admin.com',
                                    to=[user_obj.email])
            EmailThread(email_obj).start()
            return Response({'details':'user activation resend successfully!'},status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    