
from django.template import Library

register = Library()

@register.inclusion_tag('widgets/form_error_summary.html')
def form_error_summary(form):
    return dict(form=form)