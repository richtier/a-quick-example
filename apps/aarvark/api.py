# C9001 (indirect-foreign-key)
# C9002 (count-instead-exists)
# C9003 (truthy-instead-exists)
# C9004 (inefficient-order-by-random)
from rest_framework.views import APIView

from django.core.exceptions import PermissionDenied

from .models import PlatformUser


class GoodDocuments(APIView):
    authentication_classes = []

    def post(self, request, pk):
        user = PlatformUser.objects.get(pk=1)

        if user.group.id != get_request_user_organisation_id(request):
            raise PermissionDenied()

        return Response()

class UserDocuments(APIView):
    authentication_classes = []

    def post(self, request, pk):
        if PlatformUser.objects.filter(group=1).count() > 0:
            raise PermissionDenied()
        return Response()


class FooDocuments(APIView):
    authentication_classes = []

    def post(self, request, pk):
        if PlatformUser.objects.filter(group=1):
            raise PermissionDenied()
        return Response()


class RandomUser(APIView):
    authentication_classes = []

    def get(self, request, pk):
        user = PlatformUser.objects.all().order_by('?')[0]
        return Response(user.pk)
