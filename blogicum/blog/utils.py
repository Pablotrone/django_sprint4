from django.db.models import Count
from django.utils import timezone

from blog.models import Post


def base_post_queryset():
    return Post.objects.select_related(
        'author',
        'category',
        'author'
    ).filter(
        is_published=True
    ).order_by('-pub_date')


def get_published_posts():
    return Post.objects.filter(category__is_published=True,
                               is_published=True,
                               pub_date__lte=timezone.now()
                               )


def annotate_comment_count(queryset):
    return queryset.annotate(comment_count=Count('comments')
                             )
