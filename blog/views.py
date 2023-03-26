from django.shortcuts import render, redirect, get_object_or_404
from users.models import Account
from blog.forms import CreateBlogPostForm, UpdateBlogPostForm, CommentForm
from blog.models import BlogPost, Comment
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.db.models import Q
import requests
# Create your views here.


def create_blog_view(request):

	context = {}

	user = request.user
	if not user.is_authenticated:
		return redirect('users:must_authenticate')

	form = CreateBlogPostForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		obj = form.save(commit=False)
		author = Account.objects.filter(email=request.user.email).first()
		obj.author = author
		obj.save()
		form = CreateBlogPostForm()
		context["success_message"] = "Blog Created"

	context['form'] = form

	return render(request, 'blog/create.html', context)

def detail_blog_view(request, slug):

	context = {}
	blog_post = get_object_or_404(BlogPost, slug=slug)
	blog_comments = blog_post.comment.all()
	context['blog_post'] = blog_post
	context['blog_comments'] = blog_comments
	return render(request, 'blog/detail_blog.html', context)

def edit_blog_view(request, slug):

    user = request.user
    if not user.is_authenticated:
        return redirect('must_authenticate')
    blog_post = get_object_or_404(BlogPost, slug=slug)
    if user != blog_post.author:
        return HttpResponse("You are not the author of this Post!")
    if request.POST:
        form = UpdateBlogPostForm(request.POST or None, request.FILES or None, instance=blog_post)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            blog_post = obj
            
    form = UpdateBlogPostForm(
			initial={
					"title": blog_post.title, 
					"body": blog_post.body,
					"image": blog_post.image,
				}
			)
    return render(request, 'blog/edit_blog.html', context={"success_message": "Updated", "form": form})

def get_blog_queryset(query=None):
	queryset = []
	queries = query.split(" ")
	for q in queries:
		posts = BlogPost.objects.filter(
			Q(title__contains=q)|
			Q(body__icontains=q)
			).distinct()
		for post in posts:
			queryset.append(post)

	# create unique set and then convert to list
	return list(set(queryset)) 

def blog_like(request, pk):
	blog_post = get_object_or_404(BlogPost, pk=pk)
	blog_post.likes.add(request.user)
	return JsonResponse({'likes':blog_post.likes.count()})

def blog_dislike(request, pk):
	blog_post = get_object_or_404(BlogPost, pk=pk)
	blog_post.likes.remove(request.user)
	return HttpResponseRedirect(reverse('blog:detail', args=(blog_post.slug,)))

def create_comment(request, slug):
	context = {}

	if not request.user.is_authenticated:
		return redirect('users:must_authenticate')
	blog_post = get_object_or_404(BlogPost, slug=slug)
	form = CommentForm(request.POST or None)
	if form.is_valid():
		obj = form.save(commit=False)
		obj.blogpost = blog_post
		obj.author = request.user
		obj.save()
		context["success_message"] = "Comment Created"
		form = CommentForm()
	context['form'] = form
	return render(request, 'blog/create_comment.html', context)

def delete_comment(request, slug):
    if not request.user.is_authenticated:
        return redirect('users:must_authenticate')
    blog_post = get_object_or_404(BlogPost, slug=slug)
    comment = get_object_or_404(Comment, author=request.user, blogpost=blog_post)
    comment.delete()
    return HttpResponseRedirect(reverse('blog:detail', args=(blog_post.slug,)))
