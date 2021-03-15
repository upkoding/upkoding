from django.db import models
from django.db.models import Q
from django.db.models.deletion import CASCADE
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.conf import settings
from django.utils.timezone import now
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
    SearchVectorField,
    TrigramSimilarity
)

from sorl.thumbnail import ImageField
from account.models import User

PROJECT_SEARCH_VECTORS = (SearchVector('title', weight='A') +
                          SearchVector('tags', weight='A') +
                          SearchVector('description_short', weight='B') +
                          SearchVector('description', weight='C'))


def project_cover_path(instance, filename):
    """
    Custom cover path: projects/cover/123455678-hello-world.png
    """
    ts = int(now().timestamp())
    return 'projects/cover/{}-{}'.format(ts, filename)


def project_image_path(instance, filename):
    """
    Custom cover path: projects/images/12345678-hello-world.png
    """
    ts = int(now().timestamp())
    return 'projects/images/{}-{}'.format(ts, filename)


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
        return self.filter(status=2)

    def featured(self):
        """
        Returns featured projects only.
        Usage:
            `Project.objects.featured()`
        Which is equivalent to:
            `Project.objects.all(status=2, is_featured=True)`
        """
        return self.filter(status=2, is_featured=True)

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
            .filter(status=2) \
            .filter(Q(rank__gte=0.2) | Q(similarity__gt=0.1)) \
            .order_by('-rank')


class Project(models.Model):
    """
    Project that can be picked-up by users.
    """
    # statuses
    STATUS_DRAFT = 0
    STATUS_PENDING = 1
    STATUS_ACTIVE = 2
    STATUS_DELETED = 3
    STATUSES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PENDING, 'Pending'),
        (STATUS_ACTIVE, 'Active'),
        (STATUS_DELETED, 'Deleted'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='projects')
    slug = models.SlugField(max_length=150, blank=True)
    title = models.CharField('Judul', max_length=100)
    description_short = models.CharField(
        'Deskripsi Pendek', max_length=100, default='')
    description = models.TextField('Deskripsi')
    requirements = models.JSONField('Requirements', blank=True, null=True)
    cover = ImageField(
        upload_to=project_cover_path,
        blank=True,
        null=True
    )
    point = models.IntegerField(default=0)
    tags = models.CharField('Tags', max_length=50, blank=True, default='')
    is_featured = models.BooleanField(default=False)
    status = models.PositiveSmallIntegerField(
        'Status', choices=STATUSES, default=STATUS_DRAFT)

    # whether user need to provide `demo_url` and/or `sourcecode_url` before project
    # marked as complete.
    require_demo_url = models.BooleanField(default=False)
    require_sourcecode_url = models.BooleanField(default=False)

    taken_count = models.IntegerField(default=0)
    completed_count = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # full text search
    search_vector = SearchVectorField(null=True, blank=True)

    # custom manager
    objects = ProjectManager()

    class Meta:
        indexes = [
            models.Index(fields=['slug'], name='project_slug_idx'),
            models.Index(fields=['status'], name='project_status_idx'),
            GinIndex(fields=['search_vector'],
                     name='project_search_vector_idx'),
        ]
        ordering = ['-created']

    def __str__(self, *args, **kwargs):
        return self.title

    def save(self, *args, **kwargs):
        # set slug
        if not self.slug:
            self.slug = slugify(self.title)

        # cleanup tags
        if self.tags:
            self.tags = ','.join([
                tag.strip().lower()
                for tag in self.tags.split(',')])

        # set search_vector on update
        # TODO: update this asynchronously (using PubSub / Cloud Task)
        if self.pk:
            self.search_vector = PROJECT_SEARCH_VECTORS
        super().save(*args, **kwargs)

    def is_active(self):
        return self.status == self.STATUS_ACTIVE

    def get_absolute_url(self):
        return reverse('projects:detail', args=[self.slug, str(self.pk)])

    def get_point_display(self):
        return '{}{}'.format(self.point, settings.POINT_UNIT)

    def inc_taken_count(self):
        self.taken_count = models.F('taken_count') + 1
        self.save()

    def inc_completed_count(self):
        self.completed_count = models.F('completed_count') + 1
        self.save()

    def dec_completed_count(self):
        self.completed_count = models.F('completed_count') - 1
        self.save()

    def assign_to(self, user):
        """
        Returns `UserProject` instance and created (bool).
        - If user already pick this project, return that one instead of creating new one
          since user can only work on the same project once.
        - If user never pick this project, create new `UserProject`.
        - Add project creator to the UserProjectParticipant so we can notify them for event in this project.
        - Last, we increment the taken count.
        """
        obj, created = UserProject.objects.get_or_create(
            user=user,
            project=self,
            defaults={
                'requirements': self.requirements,
                'point': self.point,
                'require_demo_url': self.require_demo_url,
                'require_sourcecode_url': self.require_sourcecode_url,
            })
        if created:
            # add project creator as participant
            UserProjectParticipant.objects.get_or_create(
                user_project=obj, user=self.user
            )
            # add user who working on the project as participant
            UserProjectParticipant.objects.get_or_create(
                user_project=obj, user=user)
            # inc taken count
            self.inc_taken_count()
        return (obj, created)


class ProjectImage(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='images')
    title = models.CharField(max_length=250, blank=True, default='')
    order = models.SmallIntegerField(default=0)
    image = ImageField(
        upload_to=project_image_path,
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class UserProject(models.Model):
    """
    Status of project that picked-up by user.
    The original project data itself may changed overtime, but UserProject will holds
    the snapshot of important data (requirements, point) at the time user pick this project.
    """
    # statuses
    STATUS_IN_PROGRESS = 0
    STATUS_PENDING_REVIEW = 1
    STATUS_COMPLETE = 2
    STATUS_INCOMPLETE = 3
    STATUSES = [
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_PENDING_REVIEW, 'Pending Review'),
        (STATUS_COMPLETE, 'Complete'),
        (STATUS_INCOMPLETE, 'Incomplete'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_projects')
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='user_projects')
    requirements = models.JSONField('Requirements', blank=True, null=True)
    requirements_completed_percent = models.DecimalField(
        default=0.0, decimal_places=2, max_digits=5)  # max value: 100.00
    requirements_completed_percent_max = models.DecimalField(
        default=0.0, decimal_places=2, max_digits=5)
    point = models.IntegerField(default=0)
    status = models.PositiveSmallIntegerField(
        'Status', choices=STATUSES, default=STATUS_IN_PROGRESS)

    # information bellow can be added by user when confirming the project completion
    demo_url = models.CharField(
        'URL demo proyek', max_length=250, blank=True, default='')
    sourcecode_url = models.CharField(
        'URL kode sumber proyek', max_length=250, blank=True, default='')
    note = models.TextField('Catatan', blank=True, default='')

    # whether user need to provide `demo_url` and/or `sourcecode_url` before project
    # marked as complete.
    require_demo_url = models.BooleanField(default=False)
    require_sourcecode_url = models.BooleanField(default=False)

    likes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            # to make sure get UserProject by `user` and `project` query fast
            models.Index(fields=['user', 'project'], name='user_project_idx'),
            models.Index(fields=['status'], name='user_project_status_idx'),
        ]
        constraints = [
            # to make sure there's only one UserProject record with the same `user` and `project`
            models.UniqueConstraint(
                fields=['user', 'project'],
                name='unique_user_project')
        ]

    def __str__(self):
        return '{} - {} ({})'.format(self.user.username, self.project.slug, self.point)

    def get_absolute_url(self):
        return reverse('projects:detail_user', args=[self.project.slug, self.project.pk, self.user.username])

    def get_project_url(self):
        return self.project.get_absolute_url()

    def get_point_display(self):
        return '{}{}'.format(self.point, settings.POINT_UNIT)

    def get_color_class(self):
        """
        Based Bootstrap theme color
        """
        if self.is_pending_review() or self.is_incomplete():
            return 'warning'
        if self.is_complete():
            return 'success'
        return 'primary'

    def approvable_by(self, user):
        """
        Check whether `user` can approve this project.
        """
        if self.is_complete():
            return False
        if user.is_staff and self.user != user:
            return True
        return False

    @ staticmethod
    def requirements_to_progress(requirements):
        """
        Returns progress in percent.
        """
        reqs_progress_percent = 0.0
        reqs_progress = sum(
            map(lambda r: 1 if 'complete' in r else 0, requirements))
        reqs_progress_percent = (
            reqs_progress/len(requirements)) * 100.0
        return float(format(reqs_progress_percent, '.2f'))

    @ staticmethod
    def requirements_diff(before, after):
        """
        Return the differences between before and after requirements
        """
        progress_before = UserProject.requirements_to_progress(before)
        progress_after = UserProject.requirements_to_progress(after)
        become_complete = []
        become_incomplete = []

        for index, req_before in enumerate(before):
            req_after = after[index]
            if not req_before.get('complete') and req_after.get('complete'):
                become_complete.append(req_before.get('title'))
            if req_before.get('complete') and not req_after.get('complete'):
                become_incomplete.append(req_before.get('title'))
        return (progress_before, progress_after, become_complete, become_incomplete)

    def calculate_progress(self):
        """
        Calculate percent of completed tasks/requirements and set `requirements_completed_percent` value.
        """
        if self.requirements:
            progress = UserProject.requirements_to_progress(self.requirements)
            self.requirements_completed_percent = progress
            if progress > self.requirements_completed_percent_max:
                self.requirements_completed_percent_max = progress

    def is_requirements_complete(self):
        return self.requirements_completed_percent == 100.0

    def is_complete(self):
        return self.status == self.STATUS_COMPLETE

    def is_incomplete(self):
        return self.status == self.STATUS_INCOMPLETE

    def is_pending_review(self):
        return self.status == self.STATUS_PENDING_REVIEW

    def is_in_progress(self):
        return self.status == self.STATUS_IN_PROGRESS

    def add_event(self, event_type, **kwargs):
        UserProjectEvent(
            user_project=self,
            user=kwargs.get('user', self.user),
            event_type=event_type,
            message=kwargs.get('message', '')).save()


class UserProjectEvent(models.Model):
    TYPE_PROJECT_START = 0
    TYPE_PROGRESS_UPDATE = 1
    TYPE_PROGRESS_COMPLETE = 2
    TYPE_REVIEW_REQUEST = 3
    TYPE_REVIEW_MESSAGE = 10
    TYPE_PROJECT_COMPLETE = 11
    TYPE_PROJECT_INCOMPLETE = 12
    TYPES = [
        (TYPE_PROJECT_START, 'Project start'),
        (TYPE_PROGRESS_UPDATE, 'Progress update'),
        (TYPE_PROGRESS_COMPLETE, 'Progress complete'),
        (TYPE_REVIEW_REQUEST, 'Review request'),
        (TYPE_REVIEW_MESSAGE, 'Review message'),
        (TYPE_PROJECT_COMPLETE, 'Project complete'),
        (TYPE_PROJECT_INCOMPLETE, 'Project incomplete'),
    ]

    user_project = models.ForeignKey(
        UserProject, on_delete=models.CASCADE, related_name='events')
    user = models.ForeignKey(User, on_delete=CASCADE)
    event_type = models.PositiveSmallIntegerField(choices=TYPES)
    message = models.TextField(blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['event_type'],
                         name='user_project_event_type_idx'),
        ]

    def __str__(self):
        return self.get_event_type_display()

    def istype(self, event_type: int):
        return self.event_type == event_type


class UserProjectParticipant(models.Model):
    """
    Used to track who participates in `UserProject`
    including the owner and reviewers.
    """
    user_project = models.ForeignKey(
        UserProject, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=CASCADE)
    # whether this user will will be notified for an event.
    subscribed = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
