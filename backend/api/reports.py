import io

from django.http import FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

from django.conf import settings

from .numbers import number_ingredients


def create_recipe_shopping_list(response):
    """Создание файла с ингредиентами для рецепта."""
    buffer = io.BytesIO()
    canvas = Canvas(buffer, pagesize=A4)
    pdfmetrics.registerFont(TTFont("FreeSans", "data/FreeSans.ttf"))
    canvas.setFont("FreeSans", settings.FONT_SIZE_18)
    canvas.drawString(settings.TEXT_HORIZONTAL_CENTER,
                      settings.TEXT_DIAGONAL_POSITION,
                      "Список покупок:")
    canvas.setFont("FreeSans", settings.FONT_SIZE_14)
    start_pos = settings.LINE_HEIGHT
    for count, ingredient in enumerate(response, start=1):
        ingredient_amount = ingredient[2]
        ingredient_type = ingredient[1]
        canvas.drawString(
            50,
            start_pos,
            f"{count}. {ingredient[0].capitalize()} - {ingredient_amount} "
            f"{number_ingredients(ingredient_type, ingredient_amount)}",
        )
        start_pos -= settings.LINE_HEIGHT_INCREMENT
    canvas.showPage()
    canvas.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True,
                        filename=settings.RECIPE_SHOPPING_LIST)
