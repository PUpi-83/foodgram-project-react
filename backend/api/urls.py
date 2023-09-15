from rest_framework import routers

from django.urls import include, path

from .views import IngredientsViewSet, RecipesViewSet, TagsViewSet

router_v1 = routers.DefaultRouter()

router_v1.register("tags", TagsViewSet, basename="tags")
router_v1.register("ingredients", IngredientsViewSet, basename="ingredients")
router_v1.register("recipes", RecipesViewSet, basename="recipes")


urlpatterns = [
    path("", include(router_v1.urls)),
]