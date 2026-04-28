from django import template

register = template.Library()


@register.filter(name='currency')
def currency(value):
    """Formatea un número como moneda chilena: $X.XXX sin decimales.

    Ejemplo: 15000 -> $15.000
    """
    try:
        value = int(value)
        return f"${value:,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return value


@register.filter(name='get_item')
def get_item(dictionary, key):
    """Obtiene un valor de un diccionario por clave.

    Uso: {{ mydict|get_item:key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)
