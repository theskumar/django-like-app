# encoding: utf-8

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic


class Likes(models.Model):
    content_type = models.ForeignKey("contenttypes.ContentType")
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey("content_type", "object_id")
    count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _("Likes")
        verbose_name_plural = _("Likes")
        unique_together = ("content_type", "object_id")

    @property
    def hashtag(self):
        if hasattr(self.content_object, 'hashtag'):
            return self.content_object.hashtag
        return None

    def __str__(self):
        return self.count


class Like(models.Model):
    content_type = models.ForeignKey("contenttypes.ContentType")
    object_id = models.PositiveIntegerField(null=False)
    content_object = generic.GenericForeignKey("content_type", "object_id")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, blank=False,
                             related_name="likes", verbose_name=_("likes"))

    class Meta:
        verbose_name = _("Like")
        verbose_name_plural = _("Likes")
        unique_together = ("content_type", "object_id", "user")

    @property
    def hashtag(self):
        if hasattr(self.content_object, 'hashtag'):
            return self.content_object.hashtag
        return None

    def __str__(self):
        return self.user
