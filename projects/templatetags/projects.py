from django import template
from projects.models import UserProjectEvent

register = template.Library()


@register.inclusion_tag('projects/templatetags/render_requirements.html')
def render_requirements(project):
    """
    Render project's requirements.
    """
    return {'requirements': project.requirements}


@register.inclusion_tag('projects/templatetags/render_requirements_form.html', takes_context=True)
def render_requirements_form(context, user_project):
    """
    Render user_project's requirements form to updated progress.
    Requirements form only editable by its owner and the user_project not yet completed.
    """
    is_owner = context.request.user == user_project.user
    return {
        'user_project': user_project,
        'requirements': user_project.requirements,
        'is_owner': is_owner,
        'editable': is_owner and user_project.is_in_progress(),
    }


@register.inclusion_tag('projects/templatetags/render_review_request_form.html', takes_context=True)
def render_review_request_form(context, user_project, form):
    """
    The Review Request form always editable by owner even though the project already completed
    so user can edit project links and note if needed.
    """
    is_owner = context.request.user == user_project.user
    return {
        'user_project': user_project,
        'form': form,
        'is_owner': is_owner,
        'editable': is_owner,
    }


@register.inclusion_tag('projects/templatetags/render_tags.html')
def render_tags(project):
    """
    Render project's tags.
    """
    data = {'tags': []}
    if not project.tags:
        return data
    data['tags'] = project.tags.split(',')
    return data


@register.inclusion_tag('projects/templatetags/render_events.html')
def render_events(user_project):
    """
    Render project's events.
    """
    events = UserProjectEvent.objects.filter(user_project=user_project)
    events_with_template = []
    for event in events:
        events_with_template.append({
            'obj': event,
            'tpl': 'projects/templatetags/events/type_{}.html'.format(event.event_type)
        })
    return {
        'user_project': user_project,
        'events': events_with_template
    }
