from django import template

register = template.Library()

@register.simple_tag
def getSuccess():
    return 1

@register.simple_tag
def getFailure():
    return 0