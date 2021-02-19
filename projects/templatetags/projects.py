from django import template

register = template.Library()


@register.inclusion_tag('projects/templatetags/render_requirements.html')
def render_requirements(project):
    """
    Render project's requirements.
    """
    return {'requirements': project.requirements}


@register.inclusion_tag('projects/templatetags/render_requirements_form.html', takes_context=True)
def render_requirements_form(context, project):
    """
    Render project's requirements form to updated progress.
    """
    reqs_completed_percent = 0.0
    reqs = project.requirements
    if reqs:
        # calculate percent of completed tasks/requirements
        reqs_completed = sum(map(lambda r: 1 if 'complete' in r else 0, reqs))
        reqs_completed_percent = (reqs_completed/len(reqs)) * 100
    return {
        'user_project': project,
        'requirements': project.requirements,
        'requirements_completed_percent': reqs_completed_percent,
        'editable': context.request.user == project.user,
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
