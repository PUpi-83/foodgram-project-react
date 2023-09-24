import pymorphy2


def declination_ingredients(name_ingredient, amount):
    """Склонение количества ингредиентов."""
    morph = pymorphy2.MorphAnalyzer()

    parsed = morph.parse(name_ingredient)[0]

    if amount == 1:
        inflected_word = parsed.inflect({'sing'}).word
    else:
        inflected_word = parsed.inflect({'plur'}).word

    return inflected_word
