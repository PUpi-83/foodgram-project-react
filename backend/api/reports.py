import io

from django.http import FileResponse
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

from .numbers import declination_ingredients


def create_recipe_shopping_list(response):
    """Создание файла с ингредиентами для рецепта."""
    buffer = io.BytesIO()
    canvas = Canvas(buffer, pagesize=A4)
    pdfmetrics.registerFont(TTFont("Ostrovsky", "fonts/Ostrovsky.ttf"))
    canvas.setFont("Ostrovsky", settings.FONT_SIZE_18)
    canvas.drawString(settings.TEXT_HORIZONTAL_CENTER,
                      settings.TEXT_DIAGONAL_POSITION,
                      "Список покупок:")
    canvas.setFont("Ostrovsky", settings.FONT_SIZE_14)
    start_pos = settings.LINE_HEIGHT
    for count, ingredient in enumerate(response, start=1):
        ingredient_amount = ingredient[2]
        ingredient_type = ingredient[1]
        canvas.drawString(
            50,
            start_pos,
            f"{count}. {ingredient[0].capitalize()} - {ingredient_amount} "
            f"{declination_ingredients(ingredient_type, ingredient_amount)}",
        )
        start_pos -= settings.LINE_HEIGHT_INCREMENT
    canvas.setFont("Ostrovsky", settings.FONT_SIZE_12)
    canvas.drawString(settings.TEXT_HORIZONTAL_CENTER, 30,
                      "Твой продуктовый помощник")

    canvas.showPage()
    canvas.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True,
                        filename=settings.RECIPE_SHOPPING_LIST)
