from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Post, Profile, Comment, Message

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('feed')
    else:
        form = UserCreationForm()
    return render(request, 'posts/register.html', {'form': form})

def sign_out(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def feed(request):
   
    if hasattr(request.user, 'profile'):
        user_following = request.user.profile.follows.all()
        posts = Post.objects.filter(author__profile__in=user_following).order_by('-created_at')
    else:
        
        posts = Post.objects.all().order_by('-created_at')
    
    #
    if request.method == 'POST':
        content = request.POST.get('content')
        image = request.FILES.get('image')
        if content:
            Post.objects.create(author=request.user, content=content, image=image)
            return redirect('feed')
    
    return render(request, 'posts/feed.html', {'posts': posts})

def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=profile_user).order_by('-created_at')
    
    if hasattr(profile_user, 'profile'):
        following_count = profile_user.profile.follows.count()
        followers_count = profile_user.profile.followed_by.count()
    else:
        following_count = 0
        followers_count = 0

    post_count = posts.count()

    is_following = False
    my_profile = getattr(request.user, 'profile', None)
    target_profile = getattr(profile_user, 'profile', None)

    if my_profile and target_profile:
        if my_profile.follows.filter(user=profile_user).exists():
            is_following = True

    if request.method == 'POST':
        if request.user == profile_user and my_profile and request.FILES.get('profile_image'):
            my_profile.profile_image = request.FILES['profile_image']
            my_profile.save()
            return redirect('profile', username=username)
            
        
        if my_profile and target_profile:
            action = request.POST.get('follow')
            if action == "follow":
                my_profile.follows.add(target_profile)
            elif action == "unfollow":
                my_profile.follows.remove(target_profile)
            my_profile.save()
            return redirect('profile', username=username)

    return render(request, 'posts/profile.html', {
        'profile_user': profile_user, 
        'posts': posts,
        'is_following': is_following,
        'post_count': post_count,
        'following_count': following_count,
        'followers_count': followers_count
    })

def search(request):
    query = request.GET.get('q')
    results = []
    if query:
        results = User.objects.filter(username__icontains=query)
    return render(request, 'posts/search.html', {'results': results, 'query': query})

# --- POST ACTIONS ---
@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect('feed')

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        text = request.POST.get('text')
        if text:
            Comment.objects.create(post=post, author=request.user, text=text)
    return redirect('feed')

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user == post.author:
        post.delete()
    return redirect('feed')

# --- SETTINGS ---
@login_required
def settings(request):
    return render(request, 'posts/settings.html')

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        return redirect('login')
    return redirect('settings')

@login_required
def chat_room(request, username):
    other_user = get_object_or_404(User, username=username)
    
  
    cutoff_time = timezone.now() - timedelta(minutes=10)
    Message.objects.filter(timestamp__lt=cutoff_time).delete()

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(sender=request.user, receiver=other_user, content=content)
            return redirect('chat_room', username=username)

    messages = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) | 
        Q(sender=other_user, receiver=request.user)
    ).order_by('timestamp')

    return render(request, 'posts/chat.html', {
        'other_user': other_user,
        'messages': messages
    })

@login_required
def inbox(request):
    messages = Message.objects.filter(Q(sender=request.user) | Q(receiver=request.user))
    conversations = set()
    for msg in messages:
        if msg.sender != request.user:
            conversations.add(msg.sender)
        if msg.receiver != request.user:
            conversations.add(msg.receiver)
    return render(request, 'posts/inbox.html', {'conversations': conversations})