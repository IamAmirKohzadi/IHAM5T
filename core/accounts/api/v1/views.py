from rest_framework import generics,status
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView,
                                            TokenVerifyView)
from django.shortcuts import get_object_or_404
from .permissions import RedirectAuthenticatedApiMixin
from django.core.mail import send_mail as send2
from django.conf import settings
from accounts.models import User,Profile
from .serializers import *
from ..utils import *
from mail_templated import send_mail,EmailMessage
from jwt.exceptions import ExpiredSignatureError,InvalidSignatureError
import jwt

from core.recaptcha import verify_recaptcha
# API endpoint to register new users and send activation emails.
class RegistrationApiView(RedirectAuthenticatedApiMixin,TokenForUserMixin,generics.GenericAPIView):
    serializer_class = RegistrationSerializer
    def post(self, request, *args, **kwargs):
        # Validate input, create user, and email activation token.
        if not request.user or not request.user.is_authenticated:
            token = request.data.get("g-recaptcha-response")
            is_valid, message = verify_recaptcha(token, request.META.get("REMOTE_ADDR"))
            if not is_valid:
                return Response({"detail": message}, status=status.HTTP_400_BAD_REQUEST)
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
                                {'token': token, 'site_url': settings.SITE_URL.rstrip('/')},
                                'admin@admin.com',
                                to=[email])
            EmailThread(email_obj).start()
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# Returns a DRF token (not JWT) for the authenticated user.
class CustomObtainAuthToken(ObtainAuthToken):
    serializer_class = CustomAuthTokenSerializer
    def post(self, request, *args, **kwargs):
        # Validate credentials and issue a token for the user.
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
    
# deletes the user’s DRF Token (logs them out if you’re using token auth). It only affects the DRF token, not JWT.
class CustomDiscardAuthToken(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        # Delete the current user's token.
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)  
# Returns a JWT access + refresh pair (SimpleJWT).
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# Allows authenticated users to change their own password.
class ChangePasswordApiView(generics.GenericAPIView):
    model = User
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def get_object(self,queryset=None):
        # Resolve the current user as the password change target.
        obj = self.request.user
        return obj
    
    def put(self, request, *args, **kwargs):
        # Verify old password and apply a new one.
        self.object = self.get_object()
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get('old_password')):
                return Response({'old_password' : ['wrong password']},status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get('new_password'))
            self.object.save()
            return Response({'details' : 'password changed very gooooooooood!'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
# Retrieves and updates the authenticated user's profile.
class ProfileApiView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        # Load the profile for the current user.
        return get_object_or_404(Profile,user=self.request.user)
    def update(self, request, *args, **kwargs):
        # Persist profile updates and add a success message.
        response = super().update(request, *args, **kwargs)
        response.data['message'] = 'Changes were done successfully!'
        return response

# Sends a test email using the templated email system.
class TestEmailSend(TokenForUserMixin,generics.GenericAPIView):
    def get(self,request,*args,**kwargs):
        # Send a sample email to confirm SMTP configuration.
        self.email = 'test@test.com'
        user_obj = get_object_or_404(User,email=self.email)
        token = self.get_tokens_for_user(user_obj)
        email_obj = EmailMessage('email/hello.tpl',
                                {'token': token},
                                'admin@admin.com',
                                to=[self.email])
        EmailThread(email_obj).start()
        return Response('email sent!')
    

# Confirms an activation token and renders HTML or JSON status.
class ActivationApiView(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]

    def get(self, request, token, *args, **kwargs):
        # Decode the token and toggle verification if valid.
        context = {"status": "error", "message": "Activation link is not valid."}
        status_code = status.HTTP_400_BAD_REQUEST
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id")
            if not user_id:
                context["message"] = "Activation link is not valid."
            else:
                user_obj = User.objects.filter(pk=user_id).first()
                if not user_obj:
                    context["message"] = "Account not found."
                elif not user_obj.is_verified:
                    user_obj.is_verified = True
                    user_obj.is_active = True
                    user_obj.save(update_fields=["is_verified", "is_active"])
                    context = {"status": "success", "message": "Your account is verified. You can log in now."}
                    status_code = status.HTTP_200_OK
                else:
                    context = {"status": "info", "message": "Your account is already verified."}
                    status_code = status.HTTP_200_OK
        except ExpiredSignatureError:
            context["message"] = "Activation link expired."
        except (InvalidSignatureError, jwt.DecodeError):
            context["message"] = "Activation link is not valid."

        if request.accepted_renderer.format == "html":
            return Response(context, template_name="accounts/activation_confirm.html", status=status.HTTP_200_OK)
        return Response({"detail": context["message"]}, status=status_code)

        
# Resends activation emails for users who are not verified yet.
class ActivationResendApiView(TokenForUserMixin,generics.GenericAPIView):
    serializer_class = ActivationResendSerializer
    def post(self,request,*args,**kwargs):
        # Validate the email and send a fresh activation token.
        serializer = ActivationResendSerializer(data = request.data)
        if serializer.is_valid():
            user_obj = serializer.validated_data['user']
            token = self.get_tokens_for_user(user_obj)
            email_obj = EmailMessage('email/activation_email.tpl',
                                     {'token': token, 'site_url': settings.SITE_URL.rstrip('/')},
                                    'admin@admin.com',
                                    to=[user_obj.email])
            EmailThread(email_obj).start()
            return Response({'details':'user activation resend successfully!'},status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    
