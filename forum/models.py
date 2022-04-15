import uuid
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from sorl.thumbnail import ImageField, get_thumbnail

from account.models import User
from .managers import TopicManager, ReplyManager


class Participant(models.Model):
    """
    Generic Participant model.
    Could be participant(subscriber) of Topic, Thread or an Answer.
    """

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    content_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey("content_type", "content_id")

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscribed = models.BooleanField(default=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["content_type", "content_id", "user"],
                name="forum_participant_unique_content_user",
            )
        ]

    def __str__(self):
        return "{} @ type={} pk={}".format(
            self.user.username, self.content_type.pk, self.content_id
        )

    @classmethod
    def subscribed_to(cls, obj, exclude_user: User = None):
        """Returns subscribed participants."""
        content_type = obj.get_content_type()
        queryset = cls.objects.select_related("user").filter(
            content_type=content_type, content_id=obj.pk, subscribed=True
        )
        return queryset if exclude_user is None else queryset.exclude(user=exclude_user)


class Stat(models.Model):
    """
    Generic Statistic model.
    Could be stat of Topic, Thread or an Answer.
    """

    TYPE_VIEW_COUNT = 0
    TYPE_REPLY_COUNT = 1
    TYPE_LIKE_COUNT = 2
    TYPE_THREAD_COUNT = 3
    TYPES = (
        (TYPE_THREAD_COUNT, "thread_count"),
        (TYPE_VIEW_COUNT, "view_count"),
        (TYPE_REPLY_COUNT, "reply_count"),
        (TYPE_LIKE_COUNT, "like_count"),
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    content_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey("content_type", "content_id")

    stat_type = models.SmallIntegerField(
        choices=TYPES, default=TYPE_VIEW_COUNT, db_index=True
    )
    value = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["content_type", "content_id", "stat_type"],
                name="forum_stat_unique_stat_type_content",
            )
        ]

    @classmethod
    def inc_value(cls, obj, stat_type: int):
        content_type = obj.get_content_type()
        stat, _ = cls.objects.get_or_create(
            content_type=content_type, content_id=obj.id, stat_type=stat_type
        )
        stat.value = models.F("value") + 1
        stat.save()


class ContentTypeMixin:
    @classmethod
    def get_content_type(cls):
        return ContentType.objects.get_for_model(cls)


class ParticipantMixin(ContentTypeMixin):
    def add_participant(self, user: User):
        content_type = self.__class__.get_content_type()
        participant, _ = Participant.objects.get_or_create(
            content_type=content_type, content_id=self.pk, user=user
        )
        return participant


class StatMixin(ContentTypeMixin):
    stat_types = []

    def inc_stat(self, stat_type: int):
        Stat.inc_value(self, stat_type)

    def inc_thread_count(self):
        self.inc_stat(Stat.TYPE_THREAD_COUNT)

    def inc_view_count(self):
        self.inc_stat(Stat.TYPE_VIEW_COUNT)

    def inc_reply_count(self):
        self.inc_stat(Stat.TYPE_REPLY_COUNT)

    def inc_like_count(self):
        self.inc_stat(Stat.TYPE_LIKE_COUNT)

    def get_stats(self):
        content_type = self.__class__.get_content_type()
        stats = Stat.objects.filter(
            content_type=content_type,
            content_id=self.pk,
            stat_type__in=self.stat_types,
        )
        return {stat.get_stat_type_display(): stat.value for stat in stats}


def topic_image(instance, filename):
    """
    Custom image path: forum/topics/123455678-hello-world.png
    """
    return f"forum/topics/{uuid.uuid4()}-{filename.lower()}"


class Topic(models.Model, StatMixin, ParticipantMixin):
    stat_types = [Stat.TYPE_THREAD_COUNT]

    STATUS_INACTIVE = 0
    STATUS_ACTIVE = 1
    STATUSES = (
        (STATUS_INACTIVE, "Inactive"),
        (STATUS_ACTIVE, "Active"),
    )

    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=150, blank=True, unique=True)
    user = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name="forum_topics"
    )

    # so we can have topic for many content types: Project, Class, Tutorial, Custom
    # BUT there should be only single topic for content_type and content_id combination.
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    content_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey("content_type", "content_id")

    status = models.PositiveSmallIntegerField(
        "Status", choices=STATUSES, default=STATUS_ACTIVE, db_index=True
    )

    description = models.TextField(blank=True, default="")
    image = ImageField(upload_to=topic_image, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = TopicManager()

    class Meta:
        ordering = ["-pk"]
        # single topic for content_type and content_id combination
        constraints = [
            models.UniqueConstraint(
                fields=["content_type", "content_id"],
                name="forum_topic_unique_content_type_id",
            )
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # set slug
        if not self.slug:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            "forum:topic_detail",
            args=[
                self.slug,
            ],
        )

    def image_url(self, size=64):
        """
        If topic have image, use it. Otherwise generate from default Gravatar image.
        """
        if self.image:
            return get_thumbnail(
                self.image, "{}x{}".format(size, size), crop="center", quality=99
            ).url
        return "https://www.gravatar.com/avatar/{}?d=identicon&f=y&s={}".format(
            self.pk, size
        )


class Thread(models.Model, StatMixin, ParticipantMixin):
    # stats available for Thread
    stat_types = [Stat.TYPE_VIEW_COUNT, Stat.TYPE_REPLY_COUNT]

    STATUS_INACTIVE = 0
    STATUS_ACTIVE = 1
    STATUSES = (
        (STATUS_INACTIVE, "Inactive"),
        (STATUS_ACTIVE, "Active"),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, blank=True, db_index=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="threads")
    user = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name="forum_threads"
    )
    description = models.TextField()
    status = models.PositiveSmallIntegerField(
        "Status", choices=STATUSES, default=STATUS_ACTIVE, db_index=True
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = TopicManager()

    class Meta:
        ordering = ["-pk"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # set slug
        if not self.slug:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            "forum:thread_detail", args=[self.topic.slug, self.slug, self.pk]
        )


class Reply(models.Model, StatMixin, ParticipantMixin):
    # available stats for Reply
    stat_types = [Stat.TYPE_REPLY_COUNT, Stat.TYPE_LIKE_COUNT]

    STATUS_INACTIVE = 0
    STATUS_ACTIVE = 1
    STATUSES = (
        (STATUS_INACTIVE, "Inactive"),
        (STATUS_ACTIVE, "Active"),
    )

    # level 0: is a reply to a thread
    # level 1: is a reply to a reply
    MAX_LEVEL = 1  # deepest level of reply (can only reply to level 0)

    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    message = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, blank=True, null=True, related_name="replies"
    )
    status = models.PositiveSmallIntegerField(
        "Status", choices=STATUSES, default=STATUS_ACTIVE, db_index=True
    )
    # to keep track of reply level tree
    level = models.PositiveSmallIntegerField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = ReplyManager()

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return f"(id={self.pk}, lvl={self.level}) {self.message}"

    def owned_by(self, user):
        return self.user == user
