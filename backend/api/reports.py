from reportlab.lib.pagesizes import A4
import io
from reportlab.pdfbase import pdfmetrics
from django.http import FileResponse
from reportlab.pdfbase.ttfonts import TTFont
from .func import declination_ingredients
from reportlab.pdfgen.canvas import Canvas


def create_recipe_shopping_list(response):
    """Создание файла с ингредиентами для рецепта."""

    buffer = io.BytesIO()
    canvas = Canvas(buffer, pagesize=A4)
    pdfmetrics.registerFont(TTFont("FreeSans", "data/FreeSans.ttf"))
    canvas.setFont("FreeSans", 18)
    canvas.drawString(220, 790, "Список покупок:")
    canvas.setFont("FreeSans", 14)
    start_pos = 750
    for count, ingredient in enumerate(response):
        ingredient_amount = ingredient[2]
        ingredient_type = ingredient[1]
        canvas.drawString(
            50,
            start_pos,
            f"{count + 1}. {ingredient[0].capitalize()} - {ingredient_amount} "
            f"{declination_ingredients(ingredient_type, ingredient_amount)}",
        )
        start_pos -= 15
    canvas.showPage()
    canvas.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True,
                        filename="create_recipe_shopping_list.pdf")
