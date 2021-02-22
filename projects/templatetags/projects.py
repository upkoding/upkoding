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
    is_owner = context.request.user == project.user
    return {
        'user_project': project,
        'requirements': project.requirements,
        'is_owner': is_owner,
        'editable': is_owner and project.is_in_progress(),
    }


@register.inclusion_tag('projects/templatetags/render_review_request_form.html', takes_context=True)
def render_review_request_form(context, project, form):
    """
    The Review Request form always editable by owner even though the project already completed
    so user can edit project links and note if needed.
    """
    is_owner = context.request.user == project.user
    return {
        'user_project': project,
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
