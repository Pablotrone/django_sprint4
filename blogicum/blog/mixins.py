from django.urls import reverse
from django.core.exceptions import PermissionDenied

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


class CommentDispatchMixin:
    """Проверка на авторство комментария"""

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
