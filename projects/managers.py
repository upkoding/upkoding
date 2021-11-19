from django.db import models
from django.db.models import Q
from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
    TrigramSimilarity,
)

from account.models import User

PROJECT_SEARCH_VECTORS = (SearchVector('title', weight='A') +
                          SearchVector('tags', weight='A') +
                          SearchVector('description_short', weight='B') +
                          SearchVector('description', weight='B'))


class ProjectManager(models.Manager):
    """
    Custom manager for `Project` with some helper methods to work with Project.
    """

    def active(self):
        """
        Returns active projects only.
        Usage:
            `Project.objects.active()`
        Which is equivalent to:
            `Project.objects.all(status=2)`
        """
        return self.filter(status__in=[self.model.STATUS_ACTIVE, self.model.STATUS_ARCHIVED])

    def active_ordered(self):
        return self.active().order_by('-pk', 'level')

    def featured(self):
        """
        Returns featured projects only.
        Usage:
            `Project.objects.featured()`
        Which is equivalent to:
            `Project.objects.all(status=2, is_featured=True)`
        """
        return self.filter(status=2, is_featured=True).order_by('level')

    def solved(self, user: User):
        # to avoid circular dependency
        from projects.models import UserProject

        if not user.is_authenticated:
            return self.none()

        # TODO: below are inefficient for large list
        solved_ids = UserProject.objects \
            .filter(user=user, status=UserProject.STATUS_COMPLETE) \
            .values_list('project_id')
        return self.active_ordered().filter(pk__in=solved_ids)

    def unsolved(self, user: User):
        # to avoid circular dependency
        from projects.models import UserProject

        if not user.is_authenticated:
            return self.none()

        # TODO: below are inefficient for large list
        unsolved_ids = UserProject.objects \
            .filter(user=user) \
            .exclude(status=UserProject.STATUS_COMPLETE) \
            .values_list('project_id')
        return self.active_ordered().filter(pk__in=unsolved_ids)

    def not_taken(self, user: User):
        # to avoid circular dependency
        from projects.models import UserProject

        if not user.is_authenticated:
            return self.none()

        # TODO: below are inefficient for large list
        taken_ids = UserProject.objects \
            .filter(user=user) \
            .values_list('project_id')
        return self.active_ordered().exclude(pk__in=taken_ids)

    def search(self, text):
        """
        Provides an easy way to do Full Text Search.
        Usage:
            `Project.objects.search('django')`
        """
        search_query = SearchQuery(text)
        search_rank = SearchRank(PROJECT_SEARCH_VECTORS, search_query)
        trigram_similarity = TrigramSimilarity('title', text) + \
            TrigramSimilarity('tags', text) + \
            TrigramSimilarity('description_short', text)
        return self.get_queryset() \
            .annotate(rank=search_rank, similarity=trigram_similarity) \
            .filter(status__in=[self.model.STATUS_ACTIVE, self.model.STATUS_ARCHIVED]) \
            .filter(Q(rank__gte=0.2) | Q(similarity__gt=0.1)) \
            .order_by('-rank', 'status', 'level')
