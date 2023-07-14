import base64

import webcolors
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Ingredients, IngredientsRecipes, Recipes, Tags
from users.serializers import CustomUserSerializer


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class TagsSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        fields = ['id', 'name', 'color', 'slug']
        model = Tags


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""
    class Meta:
        fields = ['id', 'name', 'measurement_unit']
        model = Ingredients


class IngredientsRecipesSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов в рецепте."""
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.StringRelatedField(read_only=True,
                                          source='ingredients.name')
    measurement_unit = serializers.StringRelatedField(
        read_only=True,
        source='ingredients.measurement_unit'
    )

    class Meta:
        model = IngredientsRecipes
        fields = ['id', 'name', 'measurement_unit', 'amount']
        validators = [
            UniqueTogetherValidator(
                queryset=IngredientsRecipes.objects.all(),
                fields=['ingredients', 'recipe']
            )
        ]

    def validate_ingredients(self, data):
        ingredients_list = []
        ingredient = data['ingredients']
        if not data:
            raise serializers.ValidationError(
                'Укажите как минимум один ингредиент'
            )
        for item in data:
            if item['amount'] == 0:
                raise serializers.ValidationError(
                    'Укажите колличество'
                )
            if ingredient in ingredients_list:
                raise serializers.ValidationError(
                    'Вы уже добавили этот ингредиент'
                )
            ingredients_list.append(ingredient)
        return data


class IngredientsInRecipeSerializer(IngredientsRecipesSerializer):
    """Вспомогательный сериализатор для добавления ингредиентов"""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredients.objects.all())

    class Meta:
        model = IngredientsRecipes
        fields = ['id', 'name', 'measurement_unit', 'amount']


class RecipesSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""
    author = CustomUserSerializer(read_only=True)
    tags = TagsSerializer(read_only=True, many=True)
    image = Base64ImageField()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipes
        fields = ['id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time']

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorite.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.shoppingcart.filter(recipe=obj).exists()

    def get_ingredients(self, obj):
        ingredients = IngredientsRecipes.objects.filter(recipes=obj)
        return IngredientsRecipesSerializer(ingredients, many=True).data


class CreateRecipesSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и изменения рецептов."""
    author = CustomUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(), many=True
    )
    ingredients = IngredientsInRecipeSerializer(many=True)
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipes
        fields = ['id', 'ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time', 'author']

    def validate_tags(self, data):
        if not data:
            raise serializers.ValidationError(
                'Укажите один или несколько тегов'
            )
        return data

    def add_ingredients(self, ingredients, model):
        ingredientsinrecipe_data = []
        for ingredient in ingredients:
            ingredientsinrecipe_data.append(IngredientsRecipes(
                recipes=model,
                ingredients=ingredient['id'],
                amount=ingredient['amount']
            ))
        IngredientsRecipes.objects.bulk_create(ingredientsinrecipe_data)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = super().create(validated_data)
        self.add_ingredients(ingredients, recipe)
        for tag in tags:
            recipe.tags.add(tag)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        if 'tags' in validated_data:
            instance.tags.set(validated_data.pop('tags'))
        instance.ingredients.clear()
        instance.image = validated_data.get('image', instance.image)
        self.add_ingredients(ingredients, instance)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        return super().update(instance, validated_data)

    def to_representation(self, recipe):
        return RecipesSerializer(
            recipe,
            context={'request': self.context.get('request')}
        ).data


class ShoppingCartSerializer(ModelSerializer):
    """Сериализатор для корзины."""

    class Meta:
        model = Recipes
        fields = ['id', 'name', 'image', 'cooking_time']
