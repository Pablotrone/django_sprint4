from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import (CreateView, DeleteView,
                                  DetailView, ListView, UpdateView)

from blog.models import Category, Comment, Post
from .constants import POST_VALUE_PER_PAGE
from .mixins import (CommentBaseModelMixin, CommentDispatchMixin,
                     GetUrlMixin, PostBaseModelMixin, UniqueUrlAtributMixin)
from .utils import (base_post_details, get_published_posts,
                    annotate_comment_count)
from .forms import CommentForm, UserForm


User = get_user_model()


class HomePage(ListView):
    """Главная страница сайта"""

    model = Post
    template_name = 'blog/index.html'
    paginate_by = POST_VALUE_PER_PAGE

    def get_queryset(self):
        return annotate_comment_count(
            get_published_posts().order_by('-pub_date')
        )


class PostCreateView(PostBaseModelMixin, LoginRequiredMixin, CreateView):
    """Создать пост"""

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        username = self.request.user.username
        return reverse(
            'blog:profile',
            kwargs={'username': username})


class PostDetailView(DetailView):
    """Страница просмотра поста"""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self):
        post_id = self.kwargs.get('post_id')
        start_queryset = Post.objects.all()
        base_queryset = base_post_details(start_queryset)
        post = get_object_or_404(base_queryset, pk=post_id)
        if self.request.user == post.author:
            return post
        else:
            published_posts = get_published_posts()
            base_queryset = base_post_details(published_posts)
            post = get_object_or_404(
                base_queryset,
                pk=self.kwargs['post_id']
            )
            return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.all()
        return context


class PostUpdateView(
    PostBaseModelMixin,
    UniqueUrlAtributMixin,
    LoginRequiredMixin,
    UpdateView
):
    """Редактировать пост"""

    def dispatch(self, request, *args, **kwargs):
        posts = get_object_or_404(Post, id=self.kwargs['post_id'])
        if request.user != posts.author:
            return redirect('blog:post_detail', post_id=posts.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class PostDeleteView(
    PostBaseModelMixin,
    UniqueUrlAtributMixin,
    LoginRequiredMixin,
    DeleteView
):
    """Удалить пост"""

    def dispatch(self, request, *args, **kwargs):
        posts = get_object_or_404(
            Post,
            id=self.kwargs['post_id']
        )
        if request.user != posts.author:
            return redirect('blog:post_detail, post_id=posts.pk')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostCategoryListView(ListView):
    """Просмотр категорий постов"""

    model = Post
    template_name = 'blog/category.html'
    paginate_by = POST_VALUE_PER_PAGE
    slug_url_kwarg = 'category_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return annotate_comment_count(
            get_published_posts().filter(
                category_id=self.category,
            ).order_by('-pub_date')
        )


class ProfileListView(ListView):
    """Страница профиля"""

    model = User
    template_name = 'blog/profile.html'
    slug_url_kwarg = 'username'
    paginate_by = POST_VALUE_PER_PAGE

    def get_queryset(self):
        self.user = get_object_or_404(User, username=self.kwargs['username'])
        posts = annotate_comment_count(Post.objects.select_related(
            'category',
            'location',
            'author'
        ).filter(
            author=self.user,
        ).order_by(
            '-pub_date'
        )
        )
        if self.request.user == self.user:
            return posts
        return annotate_comment_count(get_published_posts()).order_by(
            '-pub_date'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.user
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Страница редактирования профиля"""

    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class CommentCreateView(
    GetUrlMixin,
    UniqueUrlAtributMixin,
    LoginRequiredMixin,
    CreateView
):
    """Написать комментарий"""

    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        post = get_object_or_404(
            get_published_posts(),
            pk=self.kwargs['post_id'],
        )
        form.instance.author = self.request.user
        form.instance.post = post
        return super().form_valid(form)


class CommentUpdateView(
    CommentBaseModelMixin,
    CommentDispatchMixin,
    GetUrlMixin,
    LoginRequiredMixin,
    UpdateView
):
    """Редактировать комментарий"""


class CommentDeleteView(
    CommentBaseModelMixin,
    CommentDispatchMixin,
    GetUrlMixin,
    LoginRequiredMixin,
    DeleteView
):
    """Удалить комментарий"""
