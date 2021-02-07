from django import template
from django.shortcuts import reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def active_class(context, namespace_or_path, classname="active"):
    """
    Detect whether we're in a page described by `namespace_or_path` and return `classname` if we are.

    Param `namespace_or_path` could be:
    - A path eg. `/about/`, it will return `classname` if request.path == `/about/`
    - A path with wildcard eg. `/about/*`, it will return `classname` if request.path starts with `/about/`
    - A URL namespace eg. `account:login`, it will return `classname` if request.path == reverse('account:login')
    """
    path = context.request.path
    if '/' in namespace_or_path:
        if '*' in namespace_or_path:
            return classname if path.startswith(namespace_or_path.replace('*', '')) else ''
        return classname if path == namespace_or_path else ''

    # it must be a namespace because `namespace_or_path` doesn't contains `/`
    return classname if path == reverse(namespace_or_path) else ''
