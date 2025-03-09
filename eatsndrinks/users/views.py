from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import RetrieveUpdateAPIView, ListAPIView
from drf_spectacular.utils import extend_schema
from .serializers import RegisterSerializer, LoginSerializer, UserUpdateSerializer
from rest_framework.permissions import AllowAny
from .models import User
from rest_framework.permissions import IsAdminUser, IsAuthenticated
# Create your views here.
# Register APIView
class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=RegisterSerializer,
        responses={
            201: RegisterSerializer,
            400: {
                'type': 'object',
                'properties': {
                    'detail': {'type': 'string'},
                    'errors': {'type': 'object'}
                }
            },
            409: {
                'type': 'object',
                'properties': {
                    'detail': {'type': 'string'}
                }
            },
        }
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    'detail': 'Yêu cầu không hợp lệ.',
                    'errors': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if username already exists
        if User.objects.filter(username=serializer.validated_data['username']).exists():
            return Response(
                {'detail': 'Tên người dùng đã tồn tại!'},
                status=status.HTTP_409_CONFLICT
            )

        serializer.save()
        return Response(
            {
                'detail': 'Đăng ký thành công!',
                'user': serializer.data  # Use UserSerializer to format the user data
            },
            status=status.HTTP_201_CREATED
        )
    



class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: {'type': 'object', 'properties': {
                'detail': {'type': 'string'},
                'refresh': {'type': 'string'},
                'access': {'type': 'string'},
            }},
            400: {'type': 'object', 'properties': {
                'detail': {'type': 'string'}
            }},
            401: {'type': 'object', 'properties': {
                'detail': {'type': 'string'}
            }},
            403: {'type': 'object', 'properties': {
                'detail': {'type': 'string'}
            }},
            404: {'type': 'object', 'properties': {
                'detail': {'type': 'string'}
            }},
        }
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Không tìm thấy người dùng!'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not user.check_password(password):
            raise AuthenticationFailed('Mật khẩu không đúng!')  # Trả về 401

        if not user.is_active:
            return Response(
                {'detail': 'Tài khoản của bạn đã bị khóa!'},
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            'detail': 'Đăng nhập thành công!',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)
    


# Admin: List all users (GET only)
class AdminUserListView(ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer

# Admin: Retrieve & Update a specific user
class AdminUserDetailView(RetrieveUpdateAPIView):
    permission_classes = [IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    lookup_field = "id"

# User: Edit own profile (except username)
class UserDetailView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserUpdateSerializer

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        serializer.validated_data.pop('username', None)  # Prevent updating username
        return super().perform_update(serializer)
