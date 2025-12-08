from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import JsonResponse
from .models import Profile, Post, Comment
from .forms import (
    UserRegisterForm,
    ProfileUpdateForm,
    PostForm,
    CommentForm
)


# === Главная страница ===
def home(request):
    posts = Post.objects.select_related('author').prefetch_related('comments', 'likes').annotate(
        comment_count=Count('comments')
    ).order_by('-created_at')[:50]

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/home.html', {'page_obj': page_obj})


# === Регистрация ===
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Ваш аккаунт успешно создан!')
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'blog/register.html', {'form': form})


# === Вход / Выход ===
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'blog/login.html', {'form': form})


@login_required
def user_logout(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('home')


# === Профиль ===
@login_required
def profile(request):
    user_posts = Post.objects.filter(author=request.user).annotate(
        comment_count=Count('comments')
    ).order_by('-created_at')

    paginator = Paginator(user_posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/profile.html', {
        'page_obj': page_obj,
        'profile_user': request.user
    })


@login_required
def profile_edit(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=profile)
    return render(request, 'blog/profile_edit.html', {'form': form})


@login_required
def profile_delete(request):
    if request.method == 'POST':
        user = request.user
        user.delete()  # Каскадное удаление: посты и комментарии удалятся автоматически
        messages.success(request, 'Ваш профиль был удалён.')
        return redirect('home')
    return render(request, 'blog/profile_delete_confirm.html')


# === Посты ===
@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_detail', post_id=post.id)  # ← здесь post.id есть
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {
        'form': form,
        'title': 'Создать пост',
    })

@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Пост обновлён!')
            return redirect('post_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)


    return render(request, 'blog/post_form.html', {
        'form': form,
        'title': 'Редактировать пост',
        'post': post
    })

@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Пост удалён.')
        return redirect('profile')
    return render(request, 'blog/post_delete_confirm.html', {'post': post})


def post_detail(request, post_id):
    post = get_object_or_404(Post.objects.annotate(comment_count=Count('comments')), id=post_id)
    comments = post.comments.select_related('author').order_by('created_at')
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post_detail', post_id=post.id)
    else:
        form = CommentForm()
    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form
    })


# === Лайки ===
@login_required
def post_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': post.likes.filter(id=request.user.id).exists(),
            'likes_count': post.likes.count()
        })
    return redirect('post_detail', post_id=post_id)


# === Комментарии ===
@login_required
def comment_edit(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Комментарий обновлён.')
            return redirect('post_detail', post_id=comment.post.id)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'blog/comment_form.html', {'form': form, 'comment': comment})


@login_required
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    if request.method == 'POST':
        post_id = comment.post.id
        comment.delete()
        messages.success(request, 'Комментарий удалён.')
        return redirect('post_detail', post_id=post_id)
    return render(request, 'blog/comment_delete_confirm.html', {'comment': comment})