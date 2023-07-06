from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Ingredients(models.Model):
    """Модель для ингредиентов."""
    name = models.CharField(
        max_length=200,
        verbose_name='название'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tags(models.Model):
    """Модель для тегов."""
    name = models.CharField(
        unique=True,
        max_length=200,
        verbose_name='Тег'
    )
    color = models.CharField(max_length=7, verbose_name='цвет')
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='слаг'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipes(models.Model):
    """Модель для рецептов."""
    name = models.CharField(
        verbose_name='название',
        max_length=200
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='автор'
    )
    text = models.TextField(
        verbose_name='описание'
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        through='IngredientsRecipes',
        related_name='ingredients'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        default=None,
        verbose_name='изображение'
    )
    tags = models.ManyToManyField(
        Tags,
        related_name='tags',
        verbose_name='теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='время приготовления',
        validators=[
            MinValueValidator(1),
        ]
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientsRecipes(models.Model):
    """Модель для ингредиентов в рецепте."""
    ingredients = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name='ingredientsrecipes',
        verbose_name='ингредиенты в рецепте'
    )
    recipes = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='колличество',
        validators=[
            MinValueValidator(1),
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиетны рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredients', 'recipes'], name='unique_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.ingredients} {self.recipes}'


class Favorite(models.Model):
    """Модель для избранных рецептов."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='пользователь'
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='favoriterecipe',
        verbose_name='избранное'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite'
            )
        ]


class ShoppingCart(models.Model):
    """Модель для корзины."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shoppingcart',
        verbose_name='пользователь'
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='shoppingcartrecipe',
        verbose_name='рецепт'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт для списка покупок'
        verbose_name_plural = 'Рецепты для списка покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='user_cart'
            )
        ]
