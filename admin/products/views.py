# admin/products/views.py
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Product, User
from .serializers import ProductSerializer
from .storage import get_presigned_upload_url, get_public_url
import uuid


@extend_schema_view(
    list=extend_schema(
        summary="List all products",
        description="Returns every product with its title, image URL, and current like count.",
        tags=["Products"],
    ),
    retrieve=extend_schema(
        summary="Get a single product",
        tags=["Products"],
    ),
    create=extend_schema(
        summary="Create a new product",
        description="Creates a product. The `image` field should be a URL — either an external link "
                     "or a public MinIO URL obtained from the `/products/upload-url/` endpoint.",
        tags=["Products"],
        examples=[
            OpenApiExample(
                "Example request",
                value={"title": "Wireless Mouse", "image": "https://.../products-images/products/abc.jpg"},
                request_only=True,
            )
        ],
    ),
    update=extend_schema(
        summary="Update an existing product",
        tags=["Products"],
    ),
    destroy=extend_schema(
        summary="Delete a product",
        description="Deletes the product. This also publishes a `product_deleted` event via Kafka, "
                     "which the Flask service consumes to keep its own copy in sync.",
        tags=["Products"],
    ),
)
class ProductViewSet(ModelViewSet):
    """
    Full CRUD for products. Every create/update/delete triggers a Kafka event
    (via Django signals) that keeps the Flask service's database in sync.
    """
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


@extend_schema(
    summary="Get a random user",
    description="Returns the ID of a randomly selected existing user. Used to simulate "
                "'current user' identity for the like feature, since no real auth is implemented.",
    tags=["Users"],
    responses={200: {"type": "object", "properties": {"id": {"type": "integer"}}}, 404: None},
)
class UserAPIView(APIView):
    def get(self, request):
        users = User.objects.all()
        if not users.exists():
            return Response({"detail": "No users found."}, status=404)
        user = users.order_by("?").first()
        return Response({"id": user.id})


ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}


@extend_schema(
    summary="Get a presigned MinIO upload URL",
    description=(
        "Generates a presigned PUT URL for direct-to-storage image upload. "
        "The frontend uploads the file directly to MinIO using `upload_url` "
        "(bypassing this Django server entirely for the file bytes), then saves "
        "`public_url` as the product's `image` field."
    ),
    tags=["Uploads"],
    request={"type": "object", "properties": {"filename": {"type": "string", "example": "photo.jpg"}}},
    responses={
        200: {
            "type": "object",
            "properties": {
                "upload_url": {"type": "string"},
                "object_name": {"type": "string"},
                "public_url": {"type": "string"},
            },
        },
        400: {"type": "object", "properties": {"error": {"type": "string"}}},
    },
)
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