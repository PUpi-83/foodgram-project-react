import pymorphy2


def number_ingredients(name, amount):
    """Склонение количества ингредиентов"""
    morph = pymorphy2.MorphAnalyzer()
    return morph.parse(name)[0].make_agree_with_number(amount).word
