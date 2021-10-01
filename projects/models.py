from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.db.models.deletion import CASCADE
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.timezone import now
from sorl.thumbnail import ImageField
from stream_django.activity import Activity

from account.models import User
from codeblocks.models import CodeBlock
from .managers import ProjectManager, PROJECT_SEARCH_VECTORS


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


class Project(models.Model):
    """
    Project that can be picked-up by users.
    """
    # statuses
    STATUS_DRAFT = 0
    STATUS_PENDING = 1
    STATUS_ACTIVE = 2
    STATUS_DELETED = 3
    STATUS_ARCHIVED = 4
    STATUSES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PENDING, 'Pending'),
        (STATUS_ACTIVE, 'Active'),
        (STATUS_DELETED, 'Deleted'),
        (STATUS_ARCHIVED, 'Archived'),
    ]

    # dificulty levels and its point
    LEVEL_EASY = 1
    LEVEL_MEDIUM = 2
    LEVEL_HARD = 3
    LEVEL_PROJECT = 99  # (backward compat with legacy project)
    LEVELS = [
        (LEVEL_EASY, 'easy'),
        (LEVEL_MEDIUM, 'medium'),
        (LEVEL_HARD, 'hard'),
        (LEVEL_PROJECT, 'project'),
    ]
    POINT_EASY = 1
    POINT_MEDIUM = 5
    POINT_HARD = 10

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='projects')
    level = models.PositiveIntegerField(choices=LEVELS, default=LEVEL_EASY)
    slug = models.SlugField(max_length=150, blank=True)
    title = models.CharField('Judul', max_length=100)
    description_short = models.CharField(
        'Deskripsi Pendek', max_length=100, default='')
    description = models.TextField('Deskripsi')
    codeblock = models.OneToOneField(
        CodeBlock,
        on_delete=models.SET_NULL,
        blank=True,
        null=True)
    requirements = models.JSONField('Requirements', blank=True, null=True)
    cover = ImageField(
        upload_to=project_cover_path,
        blank=True,
        null=True
    )
    point = models.IntegerField(default=0)
    tags = models.CharField('Tags', max_length=50, blank=True, default='')
    is_featured = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
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
            models.Index(fields=['level'], name='project_level_idx'),
            models.Index(fields=['is_premium'], name='project_is_premium_idx'),
            GinIndex(fields=['search_vector'],
                     name='project_search_vector_idx'),
        ]
        ordering = ['-pk']

    def __str__(self, *args, **kwargs):
        return self.title

    def get_level_color(self):
        colors = {
            self.LEVEL_PROJECT: 'dark',
            self.LEVEL_EASY:  'success',
            self.LEVEL_MEDIUM: 'warning',
            self.LEVEL_HARD: 'danger',
        }
        return colors.get(self.level)

    def save(self, *args, **kwargs):
        # set slug
        if not self.slug:
            self.slug = slugify(self.title)

        # cleanup tags
        if self.tags:
            self.tags = ','.join([
                tag.strip().lower()
                for tag in self.tags.split(',')])

        # set point based on level
        if self.level != self.LEVEL_PROJECT:
            if self.level == self.LEVEL_EASY:
                self.point = self.POINT_EASY
            elif self.level == self.LEVEL_MEDIUM:
                self.point = self.POINT_MEDIUM
            elif self.level == self.LEVEL_HARD:
                self.point = self.POINT_HARD

        # set search_vector on update
        # TODO: update this asynchronously (using PubSub / Cloud Task)
        if self.pk:
            self.search_vector = PROJECT_SEARCH_VECTORS
        super().save(*args, **kwargs)

    def is_active(self):
        return self.status == self.STATUS_ACTIVE

    def is_archived(self):
        return self.status == self.STATUS_ARCHIVED

    def has_codeblock(self):
        return self.codeblock_id is not None

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

    def has_codeblock(self):
        return self.codeblock_id is not None

    def assign_to(self, user):
        """
        Returns `UserProject` instance and created (bool).
        - If user already pick this project, return that one instead of creating new one
          since user can only work on the same project once.
        - If user never pick this project, create new `UserProject`.
        - If project have CodeBlock, copy the codeblock and assign to `UserProject`
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
            # assign codeblock if any
            user_codeblock = None
            if self.codeblock:
                user_codeblock = self.codeblock
                user_codeblock.pk = None
                user_codeblock.save()
                obj.codeblock = user_codeblock
                obj.save()

            # add project creator as participant
            UserProjectParticipant.objects.get_or_create(
                user_project=obj, user=self.user)
            # add user who working on the project as participant
            UserProjectParticipant.objects.get_or_create(
                user_project=obj, user=user)
            # inc taken count
            self.inc_taken_count()
        return obj, created


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
    STATUS_ARCHIVED = 4
    STATUSES = [
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_PENDING_REVIEW, 'Pending Review'),
        (STATUS_COMPLETE, 'Complete'),
        (STATUS_INCOMPLETE, 'Incomplete'),
        (STATUS_ARCHIVED, 'Archived'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_projects')
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='user_projects')
    codeblock = models.OneToOneField(
        CodeBlock,
        on_delete=models.SET_NULL,
        blank=True,
        null=True)
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
        ordering = ['-pk']

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

    @staticmethod
    def requirements_to_progress(requirements):
        """
        Returns progress in percent.
        """
        reqs_progress = sum(
            map(lambda r: 1 if 'complete' in r else 0, requirements))
        reqs_progress_percent = (reqs_progress / len(requirements)) * 100.0
        return float(format(reqs_progress_percent, '.2f'))

    @staticmethod
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
        return progress_before, progress_after, become_complete, become_incomplete

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

    def has_details(self):
        return self.demo_url or self.sourcecode_url or self.note

    def has_codeblock(self):
        return self.codeblock_id is not None

    def is_solution_viewable_by(self, user):
        if not self.has_codeblock() or self.user == user:
            return True
        if user.is_authenticated and user.is_pro_user():
            return True
        return False

    def is_solution_editable_by(self, user):
        return self.user == user

    def can_run_codeblock(self, user):
        if not self.has_codeblock():
            return False
        if self.user != user:
            return False

        codeblock = self.codeblock
        is_pro_user = user.is_pro_user()

        # PRO user always can run codes
        if is_pro_user:
            return True

        # if this is premium project, but user not PRO -> disallow!
        if self.project.is_premium and not is_pro_user:
            return False

        # If never run 3 times OR not the first-or-last run of 3 -> allow!
        mod = codeblock.run_count % 3
        if (codeblock.run_count < 3) or (mod != 0):
            return True

        # free user can only run the code 3 times in 24hr
        if codeblock.last_run:
            breaktime = 60 * 60 * 24  # 24hr
            sec_since_last_run = (now() - codeblock.last_run).total_seconds()
            if sec_since_last_run >= breaktime:
                return True
        return False

    def set_complete(self):
        self.status = UserProject.STATUS_COMPLETE
        # backward compat with legacy project
        self.requirements_completed_percent = 100.0
        # backward compat with legacy project
        self.requirements_completed_percent_max = 100.0
        self.save()

        # add point to user
        self.user.add_point(self.point)

        # increment completed count on project
        self.project.inc_completed_count()

    def add_event(self, event_type, **kwargs):
        event = UserProjectEvent(
            user_project=self,
            user=kwargs.get('user', self.user),
            event_type=event_type,
            message=kwargs.get('message', ''))
        event.save()
        return event


class UserProjectEvent(models.Model, Activity):
    TYPE_PROJECT_START = 0
    TYPE_PROGRESS_UPDATE = 1
    TYPE_PROGRESS_COMPLETE = 2
    TYPE_REVIEW_REQUEST = 3
    TYPE_REVIEW_MESSAGE = 10
    TYPE_PROJECT_COMPLETE = 11
    TYPE_PROJECT_INCOMPLETE = 12
    TYPES = [
        (TYPE_PROJECT_START, 'project_start'),
        (TYPE_PROGRESS_UPDATE, 'progress_update'),
        (TYPE_PROGRESS_COMPLETE, 'progress_complete'),
        (TYPE_REVIEW_REQUEST, 'review_request'),
        (TYPE_REVIEW_MESSAGE, 'review_message'),
        (TYPE_PROJECT_COMPLETE, 'project_complete'),
        (TYPE_PROJECT_INCOMPLETE, 'project_incomplete'),
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

    # START ==> properties and methods for getstream.io activity feed.
    @property
    def activity_object_attr(self):
        return self.user_project

    @property
    def activity_verb(self):
        return self.get_event_type_display()

    @property
    def activity_time(self):
        return self.created

    @classmethod
    def activity_related_models(cls):
        return ['user_project', 'user']

    @property
    def extra_activity_data(self):
        return dict(
            event_type=self.event_type,
            event_message=self.message)
    # END <== properties and methods for getstream.io activity feed.


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
