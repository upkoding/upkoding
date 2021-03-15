from django.utils.safestring import mark_safe
from django import template
from django.shortcuts import reverse
from django.conf import settings

from account.models import User
from projects.models import Project

register = template.Library()


@register.simple_tag(takes_context=True)
def active_class(context, namespace_or_path, classname="active"):
    """
    Detect whether we're in a page described by `namespace_or_path` and return `classname` if we are.

    Param `namespace_or_path` could be:
    - A path eg. `/about/`, it will return `classname` if request.path == `/about/`
    - A path with wildcard eg. `/about/*`, it will return `classname` if request.path starts with `/about/`
    - A URL namespace eg. `account:login`, it will return `classname` if request.path == reverse('account:login')

    Usage:
    {% active_class 'account:login' %}
    {% active_class '/account/login/' %}
    {% active_class '/account/*' %}
    """
    path = context.request.path
    if '/' in namespace_or_path:
        if '*' in namespace_or_path:
            return classname if path.startswith(namespace_or_path.replace('*', '')) else ''
        return classname if path == namespace_or_path else ''

    # it must be a namespace because `namespace_or_path` doesn't contains `/`
    return classname if path == reverse(namespace_or_path) else ''


@register.filter
def fullurl(url):
    """
    Constuct URL with domain
    """
    if url.startswith('/'):
        return '{}{}'.format(settings.SITE_DOMAIN, url)
    return '{}/{}'.format(settings.SITE_DOMAIN, url)


@register.filter
def avatar_url(user, size=100):
    """
    return only the URL of the gravatar
    Usage:  {{ user|gravatar_url:150 }}
    """
    return user.avatar_url(size)


@register.filter
def avatar_img(user, size=100):
    """
    return an image tag with the gravatar
    Usage:  {{ user|gravatar:150 }}
    """
    url = avatar_url(user, size)
    return mark_safe('<img src="%s" height="%d" width="%d" class="rounded-circle" alt="%s\'s avatar">' % (url, size, size, user.first_name))


@register.filter
def input_class(obj, arg):
    """
    Inserts css classes to input field.
    """
    current_classes = obj.field.widget.attrs.get('class', '')
    if current_classes:
        current_classes = current_classes.split()
    else:
        current_classes = []
    new_classes = arg.split()
    final_classes = set(current_classes + new_classes)
    return obj.as_widget(attrs={'class': ' '.join(final_classes)})


@register.inclusion_tag('base/templatetags/meta.html', takes_context=True)
def meta(context, **kwargs):
    meta_url = context.request.path
    meta_title = kwargs.get('title', settings.DEFAULT_METADATA.get('title'))
    meta_image = kwargs.get('image', settings.DEFAULT_METADATA.get('image'))
    meta_desc = kwargs.get(
        'desc', settings.DEFAULT_METADATA.get('description'))

    if 'object' in kwargs:
        obj = kwargs.get('object')
        if isinstance(obj, User):
            meta_url = obj.get_absolute_url()
            meta_title = 'Profil dari {} (@{})'.format(
                obj.get_display_name(), obj.username)
            meta_image = obj.avatar_url(640)
            meta_desc = obj.description

        if isinstance(obj, Project):
            meta_title = obj.title if (
                not 'title' in kwargs) else kwargs.get('title')
            meta_image = obj.cover.url
            meta_desc = obj.description

    return {
        'title': meta_title,
        'image': meta_image,
        'url': meta_url,
        'desc': meta_desc,
    }
