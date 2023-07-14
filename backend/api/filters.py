import django_filters
from django_filters import filters

from recipes.models import Ingredients, Recipes, Tags


class IngredientFilter(django_filters.FilterSet):
    """Фильтр для поиска инградиентов."""
    name = django_filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredients
        fields = ('name',)


class RecipeFilter(django_filters.FilterSet):
    """Фильтр для отображения рецептов в избранном и корзине."""
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tags.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    is_favorited = filters.NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipes
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favoriterecipe__user=self.request.user.pk)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(
                shoppingcartrecipe__user=self.request.user.pk
            )
        return queryset
