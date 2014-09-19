from django import template
register = template.Library()


@register.filter
def format_percent(num, decimals=0):
    '''
    Simple function to multiple number to 100 and round it to decimal provided.
    Not adding % as the number must go through the intcomma format for django locale

    :param num:     Input float number
    :param decimals: Decimal places to round to
    :return:
    '''

    if num:
        num *= 100

    return round(num, decimals)
