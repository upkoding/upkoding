from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404

from account.models import User
from projects.models import UserProject


class CoderList(ListView):
    template_name = 'coders/coder_list.html'
    queryset = User.objects.filter(is_active=True)
    paginate_by = 12


class CoderDetail(DetailView):
    template_name = 'coders/coder_detail.html'
    context_object_name = 'coder'

    def get_object(self):
        """
        We need to find the user by their `username`
        """
        return get_object_or_404(
            User,
            username=self.kwargs.get('username'),
            is_active=True
        )

    def __get_link_props(self):
        """
        Returns a list of link and their attributes
        so we could just loop them in template instead of checking each field
        existance one-by-one. 
        """
        link = self.object.get_link()
        if not link:
            return []

        all_props = [
            {'field': 'github', 'icon_class': 'bi-github', 'label': 'Github'},
            {'field': 'gitlab', 'icon_class': 'bi-link-45deg',
                'label': 'GitLab'},
            {'field': 'bitbucket', 'icon_class': 'bi-link-45deg',
                'label': 'Bitbucket'},
            {'field': 'linkedin', 'icon_class': 'bi-linkedin',
                'label': 'LinkedIn'},
            {'field': 'facebook', 'icon_class': 'bi-facebook',
                'label': 'Facebook'},
            {'field': 'twitter', 'icon_class': 'bi-twitter',
                'label': 'Twitter'},
            {'field': 'youtube', 'icon_class': 'bi-youtube',
                'label': 'Channel Youtube'},
            {'field': 'website', 'icon_class': 'bi-globe', 'label': 'Website'},
        ]
        valid_props = []

        for prop in all_props:
            url = getattr(link, prop['field'], None)
            if url:
                prop['url'] = url
                valid_props.append(prop)
        return valid_props

    def get_context_data(self, **kwargs):
        """
        Add `Link` to context
        """
        data = super().get_context_data(**kwargs)
        data['links'] = self.__get_link_props()
        data['current_projects'] = UserProject.objects.filter(
            user=self.object).exclude(status=UserProject.STATUS_COMPLETE)[:5]
        data['completed_projects'] = UserProject.objects.filter(
            user=self.object, status=UserProject.STATUS_COMPLETE)[:5]
        return data
