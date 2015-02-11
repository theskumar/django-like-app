# encoding: utf-8

from django.apps import apps


def attach_likescount_to_queryset(queryset, as_field="likes_count"):
    """Attach likes count to each object of the queryset.

    Because of laziness of like objects creation, this makes much simpler and more efficient to
    access to liked-object number of likes.

    (The other way was to do it in the serializer with some try/except blocks and additional
    queries)

    :param queryset: A Django queryset object.
    :param as_field: Attach the likes-count as an attribute with this name.

    :return: Queryset object with the additional `as_field` field.
    """
    model = queryset.model
    content_type = apps.get_model("contenttypes", "ContentType").objects.get_for_model(model)
    sql = ("SELECT coalesce(likes_likes.count, 0) FROM likes_likes "
           "WHERE likes_likes.content_type_id = {type_id} AND likes_likes.object_id = {tbl}.id")
    sql = sql.format(type_id=content_type.id, tbl=model._meta.db_table)
    qs = queryset.extra(select={as_field: sql})
    return qs
