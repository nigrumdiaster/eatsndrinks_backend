from rest_framework.permissions import IsAuthenticated

class CustomPermissionMixin:
    def get_permissions(self):
        """
        Đặt quyền truy cập cho từng phương thức.
        """
        if self.request.method == ['GET','POST', 'PUT', 'PATCH']:
            permission_classes = [IsAuthenticated]  # Phân quyền cho phương thức POST, PUT, PATCH
        else:
            permission_classes = []  # Phân quyền cho các phương thức khác nếu cần

        return [permission() for permission in permission_classes]
    