from django.db import models
from django.db.models import constraints, indexes
from django.db.models.deletion import CASCADE
from django.template.defaultfilters import slugify
from django.utils.timezone import now
from django.urls import reverse
from django.conf import settings

from sorl.thumbnail import ImageField
from account.models import User


def cover_path(instance, filename):
    """
    Custom cover path: projects/cover/hello-world-12345678.png
    """
    return 'projects/cover/{}-{}.{}'.format(
        instance.slug,
        int(now().timestamp()),
        filename.split('.')[-1]
    )


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
        upload_to=cover_path,
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

    # custom manager
    objects = ProjectManager()

    class Meta:
        indexes = [
            models.Index(fields=['slug'], name='project_slug_idx'),
            models.Index(fields=['status'], name='project_status_idx'),
        ]

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
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('projects:detail', args=[self.slug, str(self.pk)])

    def get_point_display(self):
        return '{}{}'.format(self.point, settings.POINT_UNIT)

    def assign_to(self, user):
        """
        Returns `UserProject` instance and created (bool).
        - If user already pick this project, return that one instead of creating new one
          since user can only work on the same project once.
        - If user never pick this project, create new `UserProject`.
        """
        return UserProject.objects.get_or_create(
            user=user,
            project=self,
            defaults={
                'requirements': self.requirements,
                'point': self.point,
                'require_demo_url': self.require_demo_url,
                'require_sourcecode_url': self.require_sourcecode_url,
            }
        )


class UserProject(models.Model):
    """
    Status of project that picked-up by user.
    The original project data itself may changed overtime, but UserProject will holds 
    the snapshot of important data (requirements, point) at the time user pick this project.
    """
    # statuses
    STATUS_IN_PROGRESS = 0
    STATUS_PENDING_REVIEW = 1
    STATUS_NEED_REVISION = 2
    STATUS_COMPLETE = 3
    STATUS_INCOMPLETE = 4
    STATUSES = [
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_PENDING_REVIEW, 'Pending Review'),
        (STATUS_NEED_REVISION, 'Need Revision'),
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

    # to store the original value
    _original_values = {}

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
        if self.status == self.STATUS_NEED_REVISION:
            return 'warning'
        if self.status == self.STATUS_PENDING_REVIEW:
            return 'primary'
        if self.status == self.STATUS_COMPLETE:
            return 'success'
        if self.status == self.STATUS_INCOMPLETE:
            return 'danger'
        return 'primary'

    def calculate_progress(self):
        """
        Calculate percent of completed tasks/requirements and set `requirements_completed_percent` value.
        """
        if not self.requirements:
            return
        reqs_completed_percent = 0.0
        reqs_completed = sum(
            map(lambda r: 1 if 'complete' in r else 0, self.requirements))
        reqs_completed_percent = (
            reqs_completed/len(self.requirements)) * 100.0
        self.requirements_completed_percent = reqs_completed_percent

    def is_requirements_complete(self):
        return self.requirements_completed_percent == 100.0

    def is_complete(self):
        return self.status == self.STATUS_COMPLETE

    def is_pending_review(self):
        return self.status == self.STATUS_PENDING_REVIEW

    def is_in_progress(self):
        return self.status == self.STATUS_IN_PROGRESS


class UserProjectEvent(models.Model):
    # type 0-9: user generated event
    TYPE_PROJECT_START = 0
    TYPE_PROGRESS_UPDATE = 1
    TYPE_REVIEW_REQUEST = 2
    # type >= 10: staff/system generated event
    TYPE_REQUIRE_REVISION = 10
    TYPE_REVIEW_MESSAGE = 11
    TYPE_PROJECT_COMPLETE = 12
    TYPE_PROJECT_INCOMPLETE = 13
    TYPES = [
        (TYPE_PROJECT_START, 'Project start'),
        (TYPE_PROGRESS_UPDATE, 'Progress update'),
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
        return self.event_type
