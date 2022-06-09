from django import template

register = template.Library()


def as_dict(value):
    return value.__dict__


register.filter('as_dict', as_dict)
