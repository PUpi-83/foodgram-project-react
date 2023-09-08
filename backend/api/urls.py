from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (UserViewSet, IngredientsViewSet, RecipesViewSet, TagViewSet)

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
]