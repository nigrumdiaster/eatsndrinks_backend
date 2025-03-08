from rest_framework.permissions import BasePermission

class IsCartOwner(BasePermission):
    """
    Chỉ cho phép chủ sở hữu của giỏ hàng truy cập, sửa đổi hoặc xóa giỏ hàng.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class IsCartItemOwner(BasePermission):
    """
    Chỉ chủ sở hữu của giỏ hàng mới có quyền thao tác với sản phẩm trong giỏ.
    """

    def has_object_permission(self, request, view, obj):
        return obj.cart.user == request.user
