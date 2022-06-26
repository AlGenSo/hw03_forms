from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from .models import Post, Group, User
from .constants import LIMIT_COUNTS_POSTS
from posts.forms import PostForm


def index(request):
    '''view-функция для главной страницы'''
    template = 'posts/index.html'
    post_list = Post.objects.select_related('author', 'group')
    paginator = Paginator(post_list, LIMIT_COUNTS_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }

    return render(request, template, context)


def groups_posts(request, slug):
    '''view-функция для страницы на которой будут посты'''
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, LIMIT_COUNTS_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }

    return render(request, template, context)


def profile(request, username):
    '''Страница профайла пользователя:
    на ней будет отображаться информация об авторе и его посты.'''
    temmplate = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts_list = author.posts.all()
    paginator = Paginator(posts_list, LIMIT_COUNTS_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': author,
        'page_obj': page_obj,
    }

    return render(request, temmplate, context)


def post_detail(request, post_id):
    '''Страница для просмотра отдельного поста.'''
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    posts_count = Post.objects.filter(author=post.author).count()
    context = {
        'post': post,
        'posts_count': posts_count,
    }

    return render(request, template, context)


@login_required
def post_create(request):
    '''Страница для публикации постов'''
    template = 'posts/post_create.html'
    form = PostForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()

        return redirect('posts:profile', username=post.author)

    return render(request, template, {'form': form, 'username': request.user})


@login_required
def edit(request, post_id):
    """Вью-функция изменения публикации"""
    template = 'posts:post_detail'
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect(template, post_id=post_id)

    form = PostForm(request.POST or None, instance=post)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()

        return redirect(template, post_id=post_id)

    form = PostForm(instance=post)

    return render(
        request,
        'posts/post_create.html',
        {'is_edit': True, 'form': form, 'post': post},
    )
