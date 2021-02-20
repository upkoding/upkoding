from django.db import models
from django.db.models import constraints, indexes
from django.template.defaultfilters import slugify
from django.utils.timezone import now
from django.urls import reverse

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
            `Project.objects.all(is_active=True)`
        """
        return self.filter(is_active=True)


class Project(models.Model):
    """
    Project that can be picked-up by users.
    """
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
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    taken_count = models.IntegerField(default=0)
    completed_count = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # custom manager
    objects = ProjectManager()

    class Meta:
        indexes = [
            models.Index(fields=['slug'], name='slug_idx'),
            models.Index(fields=['is_active'], name='is_active_idx'),
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
        return '{}UP'.format(self.point)

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
                'point': self.point
            }
        )


class UserProject(models.Model):
    """
    Status of project that picked-up by user.
    The original project data itself may changed overtime, but UserProject will holds 
    the snapshot of important data (requirements, point) at the time user pick this project.
    """
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

    # when all requirements checked
    requirements_completed = models.BooleanField(default=False)
    # when project submitted for completion
    project_completed = models.BooleanField(default=False)

    likes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            # to make sure get UserProject by `user` and `project` query fast
            models.Index(fields=['user', 'project'],
                         name='user_project_idx')
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
        return '{}UP'.format(self.point)

    def calculate_progress(self):
        """
        Calculate percent of completed tasks/requirements and set `requirements_completed_percent` value.
        If `requirements_completed_percent` 100%, we also set `requirements_completed` to True
        """
        if not self.requirements:
            return
        reqs_completed_percent = 0.0
        reqs_completed = sum(
            map(lambda r: 1 if 'complete' in r else 0, self.requirements))
        reqs_completed_percent = (
            reqs_completed/len(self.requirements)) * 100.0
        self.requirements_completed_percent = reqs_completed_percent
        # changed from incomplete to complete
        if not self.requirements_completed and reqs_completed_percent == 100.0:
            self.requirements_completed = True
        # changed from complete to incomplete
        if self.requirements_completed and reqs_completed_percent < 100.0:
            self.requirements_completed = False
