import io

from django.http import FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

from foodgram.settings import (DIAGONAL, FONT_SIZE, FONT_SIZE_1, HORIZONTAL,
                               RECIPE_SHOPPING_LIST, VERTICAL, VERTICAL_1)

from .number import number_ingredients


def create_recipe_shopping_list(response):
    """Создание файла с ингредиентами для рецепта."""

    buffer = io.BytesIO()
    canvas = Canvas(buffer, pagesize=A4)
    pdfmetrics.registerFont(TTFont("FreeSans", "data/FreeSans.ttf"))
    canvas.setFont("FreeSans", FONT_SIZE)
    canvas.drawString(HORIZONTAL, DIAGONAL, "Список покупок:")
    canvas.setFont("FreeSans", FONT_SIZE_1)
    start_pos = VERTICAL
    for count, ingredient in enumerate(response, start=1):
        ingredient_amount = ingredient[2]
        ingredient_type = ingredient[1]
        canvas.drawString(
            50,
            start_pos,
            f"{count}. {ingredient[0].capitalize()} - {ingredient_amount} "
            f"{number_ingredients(ingredient_type, ingredient_amount)}",
        )
        start_pos -= VERTICAL_1
    canvas.showPage()
    canvas.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True,
                        filename=RECIPE_SHOPPING_LIST)
