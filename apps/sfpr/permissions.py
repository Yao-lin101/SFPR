from rest_framework import permissions


class IsAuthenticatedForCreate(permissions.BasePermission):
    """
    只有认证用户才能创建记录，但所有人都可以查看
    """
    
    def has_permission(self, request, view):
        # 允许GET, HEAD, OPTIONS请求
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 只有认证用户才能创建记录
        return request.user and request.user.is_authenticated 