from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.core.cache import cache

from .constants import POST_AMOUNT
from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def index(request):
    posts = Post.objects.all()
    # показывать post_amount постов
    paginator = Paginator(posts, POST_AMOUNT)
    # извлекаем номер запрошенной страницы
    page_number = request.GET.get('page')
    # получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)
    template = 'posts/index.html'
    context = {
        'main_key': 'Это главная страница',
        'page_obj': page_obj
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, POST_AMOUNT)
    # извлекаем номер запрошенной страницы
    page_number = request.GET.get('page')
    # получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'key_group_posts': 'Записи сообщества ',
        'page_obj': page_obj
    }
    template = 'posts/group_list.html'
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    author_posts = author.posts.all()
    posts_count = author.posts.count()
    # Здесь код запроса к модели и создание словаря контекста
    paginator = Paginator(author_posts, POST_AMOUNT)
    # извлекаем номер запрошенной страницы
    page_number = request.GET.get('page')
    # получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)
    following = True
    if request.user.is_authenticated:
        follow = Follow.objects.filter(
            author=author,
            user=request.user
        ).exists()
        if request.user != author and follow:
            following = True
        else:
            following = False
    context = {
        'posts_count': posts_count,
        'following': following,
        'page_obj': page_obj,
        'author': author
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    amount = post.author.posts.count()
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'post': post,
        'amount': amount,
        'comments': comments,
        'form': form
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    # A dictionary-like object containing all given HTTP POST parameters,
    # providing that the request contains form data.
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author)
    context = {'form': form, 'is_edit': False}
    return render(request, 'posts/create_post.html', context)


def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    author_post = post.author
    user_from_request = request.user
    if user_from_request != author_post:
        return HttpResponseRedirect(
            reverse('posts:post_detail', args=[post_id])
        )

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(
            reverse('posts:post_detail', args=[post_id])
        )
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        # Сохранение с помощью commit=False
        # дает вам объект модели, затем вы можете добавить свои
        # дополнительные данные и сохранить их.
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    # информация о текущем пользователе доступна в переменной request.user
    follow_request = request.user.follower.all()
    posts = Post.objects.none()
    for followers in follow_request:
        posts = posts | followers.author.posts.all()
    # posts = follow_request.author.posts.all()
    # posts = get_object_or_404(Post, author=following_request)
    paginator = Paginator(posts, POST_AMOUNT)
    # извлекаем номер запрошенной страницы
    page_number = request.GET.get('page')
    # получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    ...
    follower = get_object_or_404(User, username=request.user)
    following = get_object_or_404(User, username=username)
    follow_object = Follow.objects.filter(user=follower, author=following).exists()
    if follower != following and follow_object != True:  
        Follow.objects.create(user=follower, author=following)
        cache.clear()
    # return redirect('posts:profile', username)
    return redirect('posts:index')


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    ...
    follower = get_object_or_404(User, username=request.user)
    following = get_object_or_404(User, username=username)
    follow_object = Follow.objects.filter(user=follower, author=following)
    follow_object.delete()
    cache.clear()
    return redirect('posts:index')
