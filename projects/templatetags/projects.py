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
    Requirements form only editable by its owner and the project not yet completed.
    """
    return {
        'user_project': project,
        'requirements': project.requirements,
        'editable': (context.request.user == project.user) and not project.project_completed,
    }


@register.inclusion_tag('projects/templatetags/render_completion_form.html', takes_context=True)
def render_completion_form(context, project, form):
    """
    The completion form always editable by owner even though the project already completed
    so user can edit project links and note if needed.
    """
    return {
        'user_project': project,
        'form': form,
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
