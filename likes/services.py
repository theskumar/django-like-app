# encoding: utf-8

# Third Party Stuff
from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import F
from django.db.transaction import atomic

from .models import Like, Likes

cache_type = {
    'object_like': 'ol:%(obj_type)s:%(obj_id)s:%(user_id)s',
    'object_like_count': 'olc:%(obj_type)s:%(obj_id)s',
    'obj_type': 'ot:%(app_label)s:%(model_name)s',
}


def cache_key(for_type, params):
    return cache_type[for_type] % params


def get_obj_type_for_model(model):
    params = {
        'app_label': model._meta.app_label,
        'model_name': model._meta.model_name
    }
    obj_type = cache.get(cache_key('obj_type', params))
    if obj_type is None:
        obj_type = apps.get_model("contenttypes", "ContentType").objects.get_for_model(model)
        cache.set(cache_key('obj_type', params), obj_type)

    return obj_type


def add_like(obj, user):
    """Add a like to an object.

    If the user has already liked the object nothing happends, so this function can be considered
    idempotent.

    :param obj: Any Django model instance.
    :param user: User adding the like. :class:`~hashup.users.models.User` instance.
    """
    obj_type = get_obj_type_for_model(obj)
    with atomic():
        like, created = Like.objects.get_or_create(content_type=obj_type, object_id=obj.id, user=user)

        if not created:
            return

        likes, _ = Likes.objects.get_or_create(content_type=obj_type, object_id=obj.id)
        likes.count = F('count') + 1
        params = {
            'obj_type': obj_type,
            'obj_id': obj.id,
            'user_id': user.id
        }
        cache.set(cache_key('object_like', params), True)
        likes.save()
        cache.delete(cache_key('object_like_count', params))
    return like


def remove_like(obj, user):
    """Remove an user like from an object.

    If the user has not liked the object nothing happens so this function can be considered
    idempotent.

    :param obj: Any Django model instance.
    :param user: User removing her like. :class:`~hashup.users.models.User` instance.
    """
    obj_type = get_obj_type_for_model(obj)
    with atomic():
        qs = Like.objects.filter(content_type=obj_type, object_id=obj.id, user=user)
        if not qs.exists():
            return

        qs.delete()

        likes, _ = Likes.objects.get_or_create(content_type=obj_type, object_id=obj.id)
        likes.count = F('count') - 1
        params = {
            'obj_type': obj_type,
            'obj_id': obj.id,
            'user_id': user.id
        }
        cache.set(cache_key('object_like', params), False)
        cache.delete(cache_key('object_like_count', params))
        likes.save()


def get_likers(obj):
    """Get the likers of an object.

    :param obj: Any Django model instance.

    :return: User queryset object representing the users that liked the object.
    """
    obj_type = get_obj_type_for_model(obj)
    return get_user_model().objects.filter(likes__content_type=obj_type, likes__object_id=obj.id)


def get_likes_count(obj):
    """Get the number of likes an object has.

    :param obj: Any Django model instance.

    :return: Number of likes or `0` if the object has no likes at all.
    """
    obj_type = get_obj_type_for_model(obj)

    params = {
        'obj_type': obj_type,
        'obj_id': obj.id,
    }
    obj_like_count = cache.get(cache_key('object_like_count', params))
    if obj_like_count is None:
        try:
            obj_like_count = Likes.objects.get(content_type=obj_type, object_id=obj.id).count
        except Likes.DoesNotExist:
            obj_like_count = 0

    cache.set(cache_key('object_like_count', params), obj_like_count)
    return obj_like_count


def has_liked(obj, user_or_id):
    """whether the objects is liked by an user.

    :param obj: Any Django model instance.
    :param user_or_id: :class:`~hashup.users.models.User` instance or id.
    """
    obj_type = get_obj_type_for_model(obj)

    if isinstance(user_or_id, get_user_model()):
        user_id = user_or_id.id
    else:
        user_id = user_or_id

    params = {
        'obj_type': obj_type,
        'obj_id': obj.id,
        'user_id': user_id
    }
    result = cache.get(cache_key('object_like', params))

    if result is None:
        result = Like.objects.filter(user=user_id, content_type=obj_type, object_id=obj.id).exists()
        cache.set(cache_key('object_like', params), result)
    return result


def get_liked(user_or_id, model):
    """Get the objects liked by an user.

    :param user_or_id: :class:`~hashup.users.models.User` instance or id.
    :param model: Show only objects of this kind. Can be any Django model class.

    :return: Queryset of objects representing the likes of the user.
    """
    obj_type = get_obj_type_for_model(model)
    conditions = ('likes_like.content_type_id = %s',
                  '%s.id = likes_like.object_id' % model._meta.db_table,
                  'likes_like.user_id = %s')

    if isinstance(user_or_id, get_user_model()):
        user_id = user_or_id.id
    else:
        user_id = user_or_id

    return model.objects.extra(where=conditions, tables=('likes_like',),
                               params=(obj_type.id, user_id))
