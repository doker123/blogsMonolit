from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    """Модель профиля пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.jpg', blank=True)
    bio = models.TextField(max_length=500, blank=True, verbose_name='Информация о пользователе')

    def __str__(self):
        return f'Профиль {self.user.username}'

@receiver(post_save, sender=User)
def create_user_profile(instance, created):
    """Автоматическое создание профиля при регистрации"""
    if created:
        Profile.objects.create(user=instance)

class Post(models.Model):
    """Модель поста"""
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(verbose_name='Текст поста')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    likes = models.ManyToManyField(User, blank=True, related_name='liked_posts')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Пост от {self.author.username} ({self.created_at.strftime("%d.%m.%Y %H:%M")})'

class Comment(models.Model):
    """Модель комментария"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Комментарий от {self.author.username} к посту {self.post.id}'