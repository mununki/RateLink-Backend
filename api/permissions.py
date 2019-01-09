from rest_framework import permissions


class UserPermission(permissions.BasePermission):
    """
    List : staff only
    Create : staff only
    Retrieve : own self or staff
    Update, Partial update : staff only
    Destroy : staff only
    """
    def has_permission(self, request, view):
        if view.action == 'list':
            return request.user.is_admin
        elif view.action == 'create':
            return request.user.is_admin
        elif view.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return request.user.is_authenticated
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if view.action == 'retrieve':
            return request.user.is_authenticated and (obj.email == request.user.email or request.user.is_admin)
        elif view.action in ['update', 'partial_update']:
            return request.user.is_admin
        elif view.action == 'destroy':
            return request.user.is_admin
        else:
            return False

class UserCreatePermission(permissions.BasePermission):
    """
    List : staff only
    Create : anyone
    Retrieve : staff only
    Update, staff only
    Destroy : staff only
    """
    def has_permission(self, request, view):
        if view.action == 'list':
            return request.user.is_admin
        elif view.action == 'create':
            return True
        elif view.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return request.user.is_authenticated
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if view.action == 'retrieve':
            return request.user.is_admin
        elif view.action in ['update', 'partial_update']:
            return request.user.is_admin
        elif view.action == 'destroy':
            return request.user.is_admin
        else:
            return False

class UserUpdatePermission(permissions.BasePermission):
    """
    List : staff only
    Create : staff only
    Retrieve : own self or staff
    Update, Partial update : own self or staff
    Destroy : staff only
    """
    def has_permission(self, request, view):
        if view.action == 'list':
            return request.user.is_admin
        elif view.action == 'create':
            return request.user.is_admin
        elif view.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return request.user.is_authenticated
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if view.action == 'retrieve':
            return request.user.is_authenticated and (obj.email == request.user.email or request.user.is_admin)
        elif view.action in ['update', 'partial_update']:
            return request.user.is_authenticated and (obj.email == request.user.email or request.user.is_admin)
        elif view.action == 'destroy':
            return request.user.is_admin
        else:
            return False

class RatePermission(permissions.BasePermission):
    """
    List : anyone
    Create : anyone
    Retrieve : own self or staff
    Update, Partial update : own self or staff
    Destroy : staff only
    """
    def has_permission(self, request, view):
        if view.action == 'list':
            return request.user.is_authenticated
        elif view.action == 'create':
            return request.user.is_authenticated
        elif view.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return request.user.is_authenticated
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if view.action == 'retrieve':
            return request.user.is_authenticated and (obj.inputperson == request.user or request.user.is_admin)
        elif view.action in ['update', 'partial_update']:
            return request.user.is_authenticated and (obj.inputperson == request.user or request.user.is_admin)
        elif view.action == 'destroy':
            return request.user.is_admin
        else:
            return False

class AjaxPermission(permissions.BasePermission):
    """
        List : anyone
        Create : staff only
        Retrieve : anyone
        Update, Partial update : staff only
        Destroy : staff only
        """

    def has_permission(self, request, view):
        if view.action == 'list':
            return request.user.is_authenticated
        elif view.action == 'create':
            return request.user.is_admin
        elif view.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return request.user.is_authenticated
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if view.action == 'retrieve':
            return request.user.is_authenticated
        elif view.action in ['update', 'partial_update']:
            return request.user.is_admin
        elif view.action == 'destroy':
            return request.user.is_admin
        else:
            return False