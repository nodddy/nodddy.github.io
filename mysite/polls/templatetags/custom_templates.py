from django import template

register = template.Library()


@register.filter
def return_item(l, i):
    try:
        return l[i]
    except:
        return None


@register.filter(name='addclass')
def addclass(value, arg):
    return value.as_widget(attrs={'class': arg})

