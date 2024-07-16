from django.utils import timezone

from blog.models import Post


def base_post_queryset():
    return Post.objects.select_related(
        'author',
        'category',
        'author'
    ).filter(
        pub_date__lt=timezone.now(),
        is_published=True,
        category__is_published=True
    ).order_by('-pub_date')
