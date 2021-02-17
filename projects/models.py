from django.db import models
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


class Project(models.Model):
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
    tags = models.CharField('Tags', max_length=50, null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    taken_count = models.IntegerField(default=0)
    completed_count = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

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
