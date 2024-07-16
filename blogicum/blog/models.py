from django.db import models
from django.contrib.auth import get_user_model

MAX_LENGTH = 256
NUM_CHAR_OUTPUT = 15

User = get_user_model()


class PublishedModel(models.Model):
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    class Meta:
        abstract = True


class Category(PublishedModel):
    title = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Заголовок'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=("Идентификатор страницы для URL; разрешены символы "
                   "латиницы, цифры, дефис и подчёркивание.")
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:NUM_CHAR_OUTPUT]


class Location(PublishedModel):
    name = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Название места'
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name[:NUM_CHAR_OUTPUT]


class Post(PublishedModel):
    title = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Заголовок'
    )
    text = models.TextField(
        verbose_name='Текст'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=("Если установить дату и время в будущем — можно делать "
                   "отложенные публикации.")
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        verbose_name='Местоположение',
        related_name='post',
        null=True
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        verbose_name='Категория',
        related_name='post',
        null=True
    )
    image = models.ImageField(
        'Фото',
        upload_to='posts_image',
        blank=True
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.title[:NUM_CHAR_OUTPUT]
    

class Comment(models.Model):
    text = models.TextField(
        verbose_name='Текст комментария'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Пост для комментария',
        related_name='comment'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'комментарий'
        verbose_name_plural = ' Комментарии'

    def __str__(self):
        return self.text[:NUM_CHAR_OUTPUT]



