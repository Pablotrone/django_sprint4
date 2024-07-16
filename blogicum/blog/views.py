from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.urls import reverse
from django.views.generic import CreateView, \
    DeleteView, DetailView, ListView, UpdateView
from blog.models import Category, Comment, Post
from .mixins import CommentBaseModelMixin, \
    DispacthMixin, GetUrlMixin, PostBaseModelMixin, \
    UniqueUrlAtributMixin
from .utils import base_post_queryset
from .forms import CommentForm, UserForm


User = get_user_model()

POST_VALUE_PER_PAGE = 10


class HomePage(ListView):
    """Главная страница сайта"""

    model = Post
    template_name = 'blog/index.html'
    paginate_by = POST_VALUE_PER_PAGE
    queryset = base_post_queryset().annotate(
        comment_count=Count('comment')
    )

    def get_queryset(self):
        return Post.objects.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        ).order_by('-pub_date').annotate(
            comment_count=Count('comment')
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
        post = get_object_or_404(Post, pk=post_id)
        if (self.request.user == post.author
            or (post.is_published and post.category.is_published
                and post.pub_date < timezone.now())):
            return post
        raise Http404("Page not found")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (Comment.objects.select_related(
            'author'
        ).filter(
            post_id=self.kwargs['post_id']
        )
        )
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
            Category.objects.filter(
                slug=self.kwargs['category_slug'],
                is_published=True),
            slug=self.kwargs['category_slug']
        )
        return Post.objects.all().filter(
            pub_date__lte=timezone.now(),
            category__slug=self.kwargs['category_slug'],
            is_published=True
        ).order_by('-pub_date').annotate(
            comment_count=Count('comment')
        )


class ProfileListView(ListView):
    """Страница профиля"""

    model = User
    template_name = 'blog/profile.html'
    slug_url_kwarg = 'username'
    paginate_by = POST_VALUE_PER_PAGE

    def get_queryset(self):
        self.user = get_object_or_404(User, username=self.kwargs['username'])
        return Post.objects.select_related(
            'category',
            'location',
            'author'
        ).filter(
            author=self.user
        ).order_by(
            '-pub_date').annotate(
                comment_count=Count('comment')
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

    def dispatch(self, request, *args, **kwargs):
        self.posts = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.posts
        return super().form_valid(form)


class CommentUpdateView(
    CommentBaseModelMixin,
    DispacthMixin,
    GetUrlMixin,
    LoginRequiredMixin,
    UpdateView
):
    """Редактировать комментарий"""


class CommentDeleteView(
    CommentBaseModelMixin,
    DispacthMixin,
    GetUrlMixin,
    LoginRequiredMixin,
    DeleteView
):
    """Удалить комментарий"""
