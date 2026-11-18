from rest_framework import viewsets, status

from .models import Category, SubCategory, Product
from .serializers import CategorySerializer, SubCategorySerializer, ProductSerializer

from utils.decorators import handle_exceptions, check_authentication
from utils.responses import success_response, error_response


class CategoryViewSet(viewsets.ViewSet):

    @handle_exceptions
    def list(self, request):
        """GET - all active categories, or one when ?id= / ?slug= is passed"""
        queryset = Category.objects.filter(active=True).prefetch_related('sub_categories')

        category_id = request.query_params.get("id")
        slug = request.query_params.get("slug")
        if category_id or slug:
            category = queryset.filter(id=category_id).first() if category_id else queryset.filter(slug=slug).first()
            if not category:
                return error_response("Category not found.", status.HTTP_404_NOT_FOUND)
            return success_response({'category': CategorySerializer(category, context={'request': request}).data})

        data = CategorySerializer(queryset, many=True, context={'request': request}).data
        return success_response({'categories': data})

    @handle_exceptions
    @check_authentication(required_role='admin')
    def create(self, request):
        """POST - create a category"""
        name = request.data.get("name")
        if not name:
            return error_response("name is required.")

        serializer = CategorySerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return error_response(serializer.errors)
        category = serializer.save()
        return success_response({'category': CategorySerializer(category, context={'request': request}).data}, status.HTTP_201_CREATED)

    @handle_exceptions
    @check_authentication(required_role='admin')
    def update(self, request, pk):
        """PUT - update a category"""
        category = Category.objects.filter(id=pk).first()
        if not category:
            return error_response("Category not found.", status.HTTP_404_NOT_FOUND)

        serializer = CategorySerializer(category, data=request.data, partial=True, context={'request': request})
        if not serializer.is_valid():
            return error_response(serializer.errors)
        category = serializer.save()
        return success_response({'category': CategorySerializer(category, context={'request': request}).data})

    @handle_exceptions
    @check_authentication(required_role='admin')
    def destroy(self, request, pk):
        """DELETE - delete a category (blocked while it still has sub categories)"""
        category = Category.objects.filter(id=pk).first()
        if not category:
            return error_response("Category not found.", status.HTTP_404_NOT_FOUND)
        if category.sub_categories.exists():
            return error_response("Delete or move its sub categories first.")

        category.delete()
        return success_response({'id': pk, 'deleted': True})


class SubCategoryViewSet(viewsets.ViewSet):

    @handle_exceptions
    def list(self, request):
        """GET - active sub categories. Filters: ?id= ?slug= ?category=<id>"""
        queryset = SubCategory.objects.filter(active=True, category__active=True).select_related('category')

        sub_category_id = request.query_params.get("id")
        slug = request.query_params.get("slug")
        if sub_category_id or slug:
            sub_category = queryset.filter(id=sub_category_id).first() if sub_category_id else queryset.filter(slug=slug).first()
            if not sub_category:
                return error_response("Sub category not found.", status.HTTP_404_NOT_FOUND)
            return success_response({'sub_category': SubCategorySerializer(sub_category, context={'request': request}).data})

        category_id = request.query_params.get("category")
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        data = SubCategorySerializer(queryset, many=True, context={'request': request}).data
        return success_response({'sub_categories': data})

    @handle_exceptions
    @check_authentication(required_role='admin')
    def create(self, request):
        """POST - create a sub category"""
        if not request.data.get("name") or not request.data.get("category"):
            return error_response("name and category are required.")

        serializer = SubCategorySerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return error_response(serializer.errors)
        sub_category = serializer.save()
        return success_response({'sub_category': SubCategorySerializer(sub_category, context={'request': request}).data}, status.HTTP_201_CREATED)

    @handle_exceptions
    @check_authentication(required_role='admin')
    def update(self, request, pk):
        """PUT - update a sub category"""
        sub_category = SubCategory.objects.filter(id=pk).first()
        if not sub_category:
            return error_response("Sub category not found.", status.HTTP_404_NOT_FOUND)

        serializer = SubCategorySerializer(sub_category, data=request.data, partial=True, context={'request': request})
        if not serializer.is_valid():
            return error_response(serializer.errors)
        sub_category = serializer.save()
        return success_response({'sub_category': SubCategorySerializer(sub_category, context={'request': request}).data})

    @handle_exceptions
    @check_authentication(required_role='admin')
    def destroy(self, request, pk):
        """DELETE - delete a sub category (blocked while it still has products)"""
        sub_category = SubCategory.objects.filter(id=pk).first()
        if not sub_category:
            return error_response("Sub category not found.", status.HTTP_404_NOT_FOUND)
        if sub_category.products.exists():
            return error_response("Delete or move its products first.")

        sub_category.delete()
        return success_response({'id': pk, 'deleted': True})


class ProductViewSet(viewsets.ViewSet):

    def _queryset(self):
        return (
            Product.objects.filter(active=True, sub_category__active=True, sub_category__category__active=True)
            .select_related('sub_category', 'sub_category__category')
            .prefetch_related('images', 'specifications')
        )

    @handle_exceptions
    def list(self, request):
        """GET - active products. Filters: ?id= ?slug= ?category=<id> ?sub_category=<id> ?search="""
        queryset = self._queryset()

        product_id = request.query_params.get("id")
        slug = request.query_params.get("slug")
        if product_id or slug:
            product = queryset.filter(id=product_id).first() if product_id else queryset.filter(slug=slug).first()
            if not product:
                return error_response("Product not found.", status.HTTP_404_NOT_FOUND)
            return success_response({'product': ProductSerializer(product, context={'request': request}).data})

        category_id = request.query_params.get("category")
        sub_category_id = request.query_params.get("sub_category")
        search = request.query_params.get("search")
        if category_id:
            queryset = queryset.filter(sub_category__category_id=category_id)
        if sub_category_id:
            queryset = queryset.filter(sub_category_id=sub_category_id)
        if search:
            queryset = queryset.filter(name__icontains=search)

        data = ProductSerializer(queryset, many=True, context={'request': request}).data
        return success_response({'products': data})

    @handle_exceptions
    @check_authentication(required_role='admin')
    def create(self, request):
        """POST - create a product"""
        if not request.data.get("name") or not request.data.get("sub_category"):
            return error_response("name and sub_category are required.")

        serializer = ProductSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return error_response(serializer.errors)
        product = serializer.save()
        return success_response({'product': ProductSerializer(product, context={'request': request}).data}, status.HTTP_201_CREATED)

    @handle_exceptions
    @check_authentication(required_role='admin')
    def update(self, request, pk):
        """PUT - update a product"""
        product = Product.objects.filter(id=pk).first()
        if not product:
            return error_response("Product not found.", status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product, data=request.data, partial=True, context={'request': request})
        if not serializer.is_valid():
            return error_response(serializer.errors)
        product = serializer.save()
        return success_response({'product': ProductSerializer(product, context={'request': request}).data})

    @handle_exceptions
    @check_authentication(required_role='admin')
    def destroy(self, request, pk):
        """DELETE - delete a product"""
        product = Product.objects.filter(id=pk).first()
        if not product:
            return error_response("Product not found.", status.HTTP_404_NOT_FOUND)

        product.delete()
        return success_response({'id': pk, 'deleted': True})
