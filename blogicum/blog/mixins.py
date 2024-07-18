from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect

from .forms import CommentForm, PostForm
from .models import Comment, Post


class PostBaseModelMixin:
    """Базовое описание поста"""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'


class CommentBaseModelMixin:
    """Базовое описание комментария"""

    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'


class GetUrlMixin:
    """Перенаправление на страницу с постом"""

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class UniqueUrlAtributMixin:
    """Уникальный идентификатор объекта"""

    pk_url_kwarg = 'post_id'


class DispatchMixin:
    """Проверка на авторство"""

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, id=self.kwargs['post_id'])
        if request.user != comment.author:
            return redirect('blog:post_detail', post_id=comment.pk)
        return super().dispatch(request, *args, **kwargs)
