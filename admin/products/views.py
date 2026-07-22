import uuid
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Product, User
from .serializers import ProductSerializer
from .storage import get_presigned_upload_url, get_public_url



class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def list(self, request, *args, **kwargs):
        products = self.get_queryset()
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        product = self.get_object()
        serializer = self.get_serializer(product)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        product = self.get_object()
        serializer = self.get_serializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        product = self.get_object()
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserAPIView(APIView):
    def get(self, request):
        users = User.objects.all()

        if not users.exists():
            return Response({"detail": "No users found."}, status=404)

        user = users.order_by("?").first()

        return Response({
            "id": user.id
        })


ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}

@api_view(['POST'])
def get_upload_url(request):
    filename = request.data.get('filename', 'image.jpg')
    extension = filename.split('.')[-1].lower() if '.' in filename else ''

    if extension not in ALLOWED_EXTENSIONS:
        return Response({'error': 'Invalid file type'}, status=400)

    object_name = f"products/{uuid.uuid4()}.{extension}"
    upload_url = get_presigned_upload_url(object_name)
    public_url = get_public_url(object_name)

    return Response({
        'upload_url': upload_url,
        'object_name': object_name,
        'public_url': public_url,
    })