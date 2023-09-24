# Generated by Django 3.2.20 on 2023-09-22 22:02

import colorfield.fields
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredients',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Ингредиенты',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='MeasureUnits',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250, unique=True, verbose_name='Наименование')),
            ],
            options={
                'verbose_name': 'Единица измерения',
                'verbose_name_plural': 'Единицы измерения',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='RecipeIngredients',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Минимальное количество - 1'), django.core.validators.MaxValueValidator(32767, message='Максимальное количество - 32767')], verbose_name='Количество')),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.ingredients')),
            ],
            options={
                'verbose_name': 'Ингредиенты рецепта',
                'verbose_name_plural': 'Ингредиенты рецептов',
            },
        ),
        migrations.CreateModel(
            name='Recipes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250, verbose_name='Название рецепта')),
                ('image', models.ImageField(default=None, null=True, upload_to='images', verbose_name='Изображение')),
                ('text', models.TextField(verbose_name='Описание рецепта')),
                ('cooking_time', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Время не меньше 1 минуты'), django.core.validators.MaxValueValidator(10000, message='Время не больше 1000 минут')], verbose_name='Время приготовления (минут)')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('ingredients', models.ManyToManyField(related_name='recipes', through='recipes.RecipeIngredients', to='recipes.Ingredients', verbose_name='Ингредиенты')),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
                'ordering': ('-pub_date',),
            },
        ),
        migrations.CreateModel(
            name='Tags',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250, verbose_name='Имя')),
                ('color', colorfield.fields.ColorField(default='#FF0000', image_field=None, max_length=25, samples=None, verbose_name='Цвет')),
                ('slug', models.SlugField(max_length=20, unique=True)),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='ShoppingCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopping_cart_recipe', to='recipes.recipes', verbose_name='Рецепт')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopping_cart_user', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Список покупок',
                'verbose_name_plural': 'Списки покупок',
            },
        ),
        migrations.CreateModel(
            name='RecipeTags',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.recipes')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.tags')),
            ],
            options={
                'verbose_name': 'Теги рецепта',
                'verbose_name_plural': 'Теги рецептов',
            },
        ),
        migrations.AddField(
            model_name='recipes',
            name='tags',
            field=models.ManyToManyField(related_name='recipes', through='recipes.RecipeTags', to='recipes.Tags', verbose_name='Теги'),
        ),
        migrations.AddField(
            model_name='recipeingredients',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.recipes'),
        ),
        migrations.AddField(
            model_name='ingredients',
            name='measurement_unit',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='recipes.measureunits', verbose_name='Единицы измерения'),
        ),
        migrations.CreateModel(
            name='FavoriteList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_list_recipe', to='recipes.recipes', verbose_name='Рецепт')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_list_user', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Список избранного',
                'verbose_name_plural': 'Списки избранного',
            },
        ),
        migrations.AddConstraint(
            model_name='shoppingcart',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_shopping_cart'),
        ),
        migrations.AddConstraint(
            model_name='recipetags',
            constraint=models.UniqueConstraint(fields=('recipe', 'tag'), name='unique_recipe_tags'),
        ),
        migrations.AddConstraint(
            model_name='recipeingredients',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredient'), name='unique_recipe_ingredients'),
        ),
        migrations.AddConstraint(
            model_name='favoritelist',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_favorite_list'),
        ),
    ]
