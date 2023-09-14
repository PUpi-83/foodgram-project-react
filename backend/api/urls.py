from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (UserViewSet, IngredientsViewSet, 
                       RecipesViewSet, TagViewSet, FollowApiView, 
                       FollowCartApiView, DownloadShoppingCart, ShoppingView)

app_name = 'api'

router = DefaultRouter()
router.register('ingredients', IngredientsViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipesViewSet, basename='recipes')
router.register('users', UserViewSet, basename='users')



urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/subscriptions/', FollowCartApiView.as_view()),
    path('recipes/download_shopping_cart/', DownloadShoppingCart.as_view()),
    path('users/<int:following_id>/subscribe/', FollowApiView.as_view()),
    path('recipes/<int:recipe_id>/shopping_cart/', ShoppingView.as_view()),
]