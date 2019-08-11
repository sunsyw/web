from rest_framework.response import Response
from book01.models import BookInfo, PeopleInfo
from rest_framework.views import APIView
from book01.seriazliers import IndexSerializers


# Create your views here.


class IndexAPIView(APIView):
    def get(self, request):
        books = BookInfo.objects.all()
        serializer = IndexSerializers(books, many=True)
        return Response(serializer.data)
