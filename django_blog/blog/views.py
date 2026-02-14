from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy, reverse
from django.db import transaction
from django.db.models import Q
from .models import Post, Profile, Comment
from .forms import UserRegisterForm, UserUpdateForm, UserProfileForm, PostForm, CommentForm, SearchForm

# Authentication Views
def home(request):
    posts = Post.objects.all()
    context = {
        'posts': posts,
        'title': 'Home',
        'search_form': SearchForm()
    }
    return render(request, 'blog/home.html', context)

def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()

    return render(request, 'registration/register.html', {'form': form, 'title': 'Register'})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            next_page = request.GET.get('next', 'home')
            return redirect(next_page)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'registration/login.html', {'title': 'Login'})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')

@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'title': 'Profile'
    }
    return render(request, 'registration/profile.html', context)

@login_required
def profile_detail(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user)

    context = {
        'profile_user': user,
        'posts': posts,
        'title': f"{user.username}'s Profile"
    }
    return render(request, 'registration/profile_detail.html', context)

@login_required
@transaction.atomic
def update_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'title': 'Edit Profile'
    }
    return render(request, 'registration/edit_profile.html', context)

# Blog Post CRUD Views
class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    ordering = ['-published_date']
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'All Posts'
        context['search_form'] = SearchForm()
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.title
        context['comment_form'] = CommentForm()
        context['comments'] = self.object.comments.all()
        context['search_form'] = SearchForm()
        return context

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('post-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Post'
        context['button_text'] = 'Create Post'
        context['search_form'] = SearchForm()
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)

        # Handle tags
        tags = form.cleaned_data.get('tags', '')
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
            self.object.tags.add(*tag_list)

        messages.success(self.request, 'Your post has been created successfully!')
        return response

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('post-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Post'
        context['button_text'] = 'Update Post'
        context['search_form'] = SearchForm()

        # Pre-populate tags field
        if self.object.tags.exists():
            context['form'].fields['tags'].initial = ', '.join([tag.name for tag in self.object.tags.all()])

        return context

    def form_valid(self, form):
        response = super().form_valid(form)

        # Handle tags
        tags = form.cleaned_data.get('tags', '')
        self.object.tags.clear()
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
            self.object.tags.add(*tag_list)

        messages.success(self.request, 'Your post has been updated successfully!')
        return response

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('post-list')
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Post'
        context['search_form'] = SearchForm()
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Your post has been deleted successfully!')
        return super().delete(request, *args, **kwargs)

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

# Comment Views
class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Comment'
        context['search_form'] = SearchForm()
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post_id = self.kwargs['pk']
        messages.success(self.request, 'Your comment has been added!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('post-detail', kwargs={'pk': self.kwargs['pk']})

class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Comment'
        context['search_form'] = SearchForm()
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Your comment has been updated!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('post-detail', kwargs={'pk': self.object.post.pk})

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Comment'
        context['search_form'] = SearchForm()
        return context

    def get_success_url(self):
        return reverse('post-detail', kwargs={'pk': self.object.post.pk})

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Your comment has been deleted!')
        return super().delete(request, *args, **kwargs)

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

# Tag and Search Views
class TagPostListView(ListView):
    """View to display posts filtered by tag."""
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        tag_slug = self.kwargs.get('tag_slug')
        return Post.objects.filter(tags__name__in=[tag_slug]).distinct().order_by('-published_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Posts tagged with '{self.kwargs.get('tag_slug')}'"
        context['search_form'] = SearchForm()
        context['current_tag'] = self.kwargs.get('tag_slug')
        return context

class SearchResultsView(ListView):
    """View to display search results."""
    model = Post
    template_name = 'blog/search_results.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return Post.objects.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(tags__name__icontains=query)
            ).distinct().order_by('-published_date')
        return Post.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Search Results'
        context['search_form'] = SearchForm(self.request.GET)
        context['query'] = self.request.GET.get('q', '')
        context['result_count'] = self.get_queryset().count()
        return context

def search_view(request):
    """View to handle search functionality."""
    form = SearchForm(request.GET or None)
    posts = []
    query = ''

    if form.is_valid():
        query = form.cleaned_data.get('query', '')
        if query:
            posts = Post.objects.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(tags__name__icontains=query)
            ).distinct().order_by('-published_date')

    context = {
        'form': form,
        'posts': posts,
        'query': query,
        'title': 'Search Results',
        'result_count': len(posts)
    }
    return render(request, 'blog/search_results.html', context)

def tag_detail_view(request, tag_slug):
    """View to display all posts with a specific tag."""
    posts = Post.objects.filter(tags__name__in=[tag_slug]).distinct().order_by('-published_date')

    context = {
        'posts': posts,
        'tag': tag_slug,
        'title': f'Posts tagged with "{tag_slug}"',
        'search_form': SearchForm(),
        'result_count': posts.count()
    }
    return render(request, 'blog/tag_detail.html', context)