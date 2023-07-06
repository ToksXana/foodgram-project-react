from django.contrib import admin

from .models import (Favorite, Ingredients, IngredientsRecipes, Recipes,
                     ShoppingCart, Tags)


class IngredientsInLine(admin.TabularInline):
    model = IngredientsRecipes


class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


class RecipesAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'in_favorite')
    list_filter = ('author', 'name', 'tags')
    inlines = (IngredientsInLine,)

    def in_favorite(self, obj):
        favorite = obj.favoriterecipe.count()
        return favorite


admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(Tags)
admin.site.register(Recipes, RecipesAdmin)
admin.site.register(IngredientsRecipes)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
