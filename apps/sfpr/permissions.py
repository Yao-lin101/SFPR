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


class IsRecordOwnerOrReadOnly(permissions.BasePermission):
    """
    对象级权限，允许记录的所有者删除或修改记录。
    """
    def has_object_permission(self, request, view, obj):
        # 读取权限允许任何请求
        if request.method in permissions.SAFE_METHODS:
            return True

        # 写入权限只允许记录的所有者
        return obj.submitter == request.user 