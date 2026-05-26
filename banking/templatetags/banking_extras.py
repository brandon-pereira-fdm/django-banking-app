from django import template

from banking.services import format_sgd, mask_identifier


register = template.Library()


@register.filter
def sgd(value):
    return format_sgd(value)


@register.filter
def mask(value):
    return mask_identifier(value)
