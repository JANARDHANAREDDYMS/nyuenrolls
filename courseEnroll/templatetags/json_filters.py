from django import template
import json
from django.core.serializers.json import DjangoJSONEncoder

register = template.Library()

@register.filter(name='json_script')
def json_script(value, element_id):
    """Escape all the HTML/XML special characters with their unicode escapes"""
    return json.dumps(value, cls=DjangoJSONEncoder)