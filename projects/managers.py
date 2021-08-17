from django.db import models
from django.db.models import Q
from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
    TrigramSimilarity,
)

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
        return self.select_related('codeblock').filter(status=2)

    def featured(self):
        """
        Returns featured projects only.
        Usage:
            `Project.objects.featured()`
        Which is equivalent to:
            `Project.objects.all(status=2, is_featured=True)`
        """
        return self.select_related('codeblock').filter(status=2, is_featured=True)

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
            .select_related('codeblock') \
            .filter(status=2) \
            .filter(Q(rank__gte=0.2) | Q(similarity__gt=0.1)) \
            .order_by('-rank')
