from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.cache import cache_page
from django.conf import settings

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .paginator import paginator_method


@cache_page(settings.CACHE_TIME)
def index(request):
    posts = Post.objects.select_related('group', 'author').all()
    page_obj = paginator_method(request, posts)
    template = 'posts/index.html'
    context = {'page_obj': page_obj}
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = paginator_method(request, posts)
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
    page_obj = paginator_method(request, author_posts)
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
        # дает объект модели, затем можно добавить свои
        # дополнительные данные и сохранить их.
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    follow_request = request.user.follower.all().values('author')
    posts = Post.objects.filter(author__in=follow_request)
    page_obj = paginator_method(request, posts)
    context = {'page_obj': page_obj}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    following = get_object_or_404(User, username=username)
    follow_object = request.user.follower.filter(
        author_id=following.id
    ).exists()
    if (
        request.user != following
        and (not follow_object)
    ):
        Follow.objects.create(user=request.user, author=following)
        cache.clear()
    return redirect('posts:index')


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    follower = get_object_or_404(User, username=request.user)
    following = get_object_or_404(User, username=username)
    follow_object = Follow.objects.filter(user=follower, author=following)
    follow_object.delete()
    cache.clear()
    return redirect('posts:index')
