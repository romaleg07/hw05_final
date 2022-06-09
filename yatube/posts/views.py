from django.shortcuts import render, get_object_or_404
from .models import Post, Group, User, Comment, Follow
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .forms import PostForm, CommentForm
from .utils import PostsPaginator


def index(request):
    post_list = Post.objects.all()
    page_obj = PostsPaginator(post_list, request)
    context = {
        'page_obj': page_obj
    }
    template = 'posts/index.html'

    return render(request, template, context)


def groups_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.group_posts.all()
    page_obj = PostsPaginator(posts, request)
    template = 'posts/group_list.html'
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    count = author.posts.all().count()
    page_obj = PostsPaginator(post_list, request)
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=author
        ).exists()

    context = {
        'page_obj': page_obj,
        'count': count,
        'author': author,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    count = post.author.posts.all().count()
    form = CommentForm(
        request.POST or None
    )
    comment = Comment.objects.filter(post=post)
    context = {
        'post': post,
        'count': count,
        'form': form,
        'comments': comment
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    username = request.user.username
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect(reverse_lazy('posts:profile', args=[username]))
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    if form.is_valid():
        post = form.save(commit=True)
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'is_edit': True,
        'form': form,
        'post_id': post_id
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    followers = Follow.objects.filter(user=request.user)
    post = Post.objects.filter(author__in=followers.values("author"))
    page_obj = PostsPaginator(post, request)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    if username != request.user.username:
        author = User.objects.get(username=username)
        Follow.objects.create(user=request.user, author=author)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', username)
