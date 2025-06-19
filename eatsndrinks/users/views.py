from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import RetrieveUpdateAPIView, ListAPIView
from drf_spectacular.utils import extend_schema
from .serializers import RegisterSerializer, LoginSerializer, UserUpdateSerializer, AddressBookSerializer
from rest_framework.permissions import AllowAny
from .models import User, AddressBook
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.exceptions import NotFound
from datetime import datetime, timedelta
from django.db.models import Count
from django.utils import timezone
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
    
class IsAdminView(APIView):
    permission_classes = [IsAuthenticated]  # Chỉ cho phép user đã đăng nhập truy cập
    serializer_class = None  # No serializer needed for simple response

    def get(self, request):
        return Response({"is_admin": request.user.is_staff})

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

class AddressBookViewSet(viewsets.ModelViewSet):
    queryset = AddressBook.objects.all()
    serializer_class = AddressBookSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Chỉ trả về địa chỉ của người dùng hiện tại
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Gán user hiện tại cho địa chỉ mới
        serializer.save(user=self.request.user)

class DefaultAddressView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddressBookSerializer

    def get(self, request):
        # Lấy địa chỉ mặc định của người dùng hiện tại
        user = request.user
        default_address = AddressBook.objects.filter(user=user, is_default=True).first()

        if not default_address:
            raise NotFound("Không có địa chỉ mặc định nào được thiết lập.")

        serializer = AddressBookSerializer(default_address)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AdminUserStatsView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'current_month_users': {'type': 'integer'},
                    'previous_month_users': {'type': 'integer'},
                    'increase_percentage': {'type': 'number'},
                }
            }
        }
    )
    def get(self, request):
        # Get current date in UTC
        now = timezone.now()
        
        # Calculate first day of current month
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Calculate first day of previous month
        if now.month == 1:
            previous_month_start = now.replace(year=now.year-1, month=12, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            previous_month_start = now.replace(month=now.month-1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Calculate first day of next month
        if now.month == 12:
            next_month_start = now.replace(year=now.year+1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            next_month_start = now.replace(month=now.month+1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get user counts
        current_month_users = User.objects.filter(
            date_joined__gte=current_month_start,
            date_joined__lt=next_month_start
        ).count()
        
        previous_month_users = User.objects.filter(
            date_joined__gte=previous_month_start,
            date_joined__lt=current_month_start
        ).count()
        
        # Calculate increase percentage
        if previous_month_users == 0:
            increase_percentage = 100 if current_month_users > 0 else 0
        else:
            increase_percentage = ((current_month_users - previous_month_users) / previous_month_users) * 100
        
        return Response({
            'current_month_users': current_month_users,
            'previous_month_users': previous_month_users,
            'increase_percentage': round(increase_percentage, 2)
        }, status=status.HTTP_200_OK)