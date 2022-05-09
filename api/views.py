from webbrowser import get
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer
from .models import User
import jwt, datetime


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginView(APIView):
    def post(self, request):
        email = request.data["email"]
        password = request.data["password"]

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed("User not found")

        if not user.check_password(password):
            raise AuthenticationFailed("Password is not correct")
        
        payload = {
            "id": user.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            "iat": datetime.datetime.utcnow()
        }
        
        token = jwt.encode(payload, "SECRET_KEY", algorithm="HS256")
        
        response = Response()

        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
                "status": 1,
                "message": "Login success",
                "token": token
            }
        
        return response


class UserView(APIView):
  def get(self, request):
    token = request.COOKIES.get("jwt")
    
    if not token:
      raise AuthenticationFailed("Unauthorized")
    
    try:
      payload = jwt.decode(token, "SECRET_KEY", algorithms=["HS256"])
    except:
      raise AuthenticationFailed("Unauthorized")
    
    user = User.objects.filter(id=payload["id"]).first()
    serializer = UserSerializer(user)
    
    return Response(serializer.data)
  
class LogoutView(APIView):
  def post(self, request):
    response = Response()
    response.delete_cookie("jwt")
    response.data = {
      'status': 1,
      'message': 'Logout success'
    }
    return response