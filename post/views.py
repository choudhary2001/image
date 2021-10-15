from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, response
from django.template import loader

from post.models import Stream, Post, Tag, Likes, PostFileContent
from post.forms import NewPostForm

from comment.models import Comment
from comment.forms import CommentForm
import os
from django.conf import settings
from django.contrib.auth.decorators import login_required

from django.urls import reverse
from authy.models import Profile


from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.models import User

# Create your views here.

def index(request):
	user = request.user
	posts = Stream.objects.all()


	group_ids = []

	for post in posts:
		group_ids.append(post.post_id)
		
	post_items = Post.objects.filter(id__in=group_ids).all().order_by('-posted')
	post_count = Post.objects.filter(id__in=group_ids).count()		

	template = loader.get_template('index.html')

	context = {
		'post_items': post_items,
		'post_count':post_count,

	}

	return HttpResponse(template.render(context, request))

def PostDetails(request, post_id):
	post = get_object_or_404(Post, id=post_id)
	user = request.user
	favorited = False
	liked = False
	related_products = Post.objects.filter(
        user=post.user).exclude(id=post_id)[:4]
	#comment
	comments = Comment.objects.filter(post=post).order_by('date')
	
	if request.user.is_authenticated:
		profile = Profile.objects.get(user=user)
		#For the color of the favorite button

		if profile.favorites.filter(id=post_id).exists():
			favorited = True
			
	if request.user.is_authenticated:
		liked = Likes.objects.filter(user=user, post=post)
		#For the color of the like button

		if liked.exists():
			liked = True
	#Comments Form
	if request.method == 'POST':
		form = CommentForm(request.POST)
		if form.is_valid():
			comment = form.save(commit=False)
			comment.post = post
			comment.user = user
			comment.save()
			return HttpResponseRedirect(reverse('postdetails', args=[post_id]))
	else:
		form = CommentForm()


	template = loader.get_template('post_detail.html')

	context = {
		'post':post,
		'favorited':favorited,
		'liked':liked,
		'form':form,
		'comments':comments,
		'posts':related_products,
	}

	return HttpResponse(template.render(context, request))




def search(request):
	query = request.GET.get("q")
	context = {}
	
	if query:
		posts = Post.objects.filter(Q(caption__icontains=query) )
		users1 = Profile.objects.filter(Q(location__icontains=query) |  Q(first_name__icontains=query) |  Q(last_name__icontains=query) )
		users = User.objects.filter(Q(username__icontains=query) |  Q(first_name__icontains=query) |  Q(last_name__icontains=query))
		#Pagination
		paginator = Paginator(posts, 6)
		page_number = request.GET.get('page')
		users_paginator = paginator.get_page(page_number)
		paginator1 = Paginator(users, 6)
		page_number1 = request.GET.get('page')
		users_paginator1 = paginator1.get_page(page_number1)
		paginator2 = Paginator(users1, 6)
		page_number2 = request.GET.get('page')
		users_paginator2 = paginator2.get_page(page_number1)
		context = {
				'posts': users_paginator,
				'users': users_paginator1,
				'users1': users_paginator2
			}
	template = loader.get_template('search.html')
	return HttpResponse(template.render(context, request))

@login_required
def NewPost(request):
	user = request.user
	tags_objs = []
	files_objs = []

	if request.method == 'POST':
		form = NewPostForm(request.POST, request.FILES)
		if form.is_valid():
			files = request.FILES.getlist('content')
			caption = form.cleaned_data.get('caption')
			tags_form = form.cleaned_data.get('tags')

			tags_list = list(tags_form.split(','))

			for tag in tags_list:
				t, created = Tag.objects.get_or_create(title=tag)
				tags_objs.append(t)

			for file in files:
				file_instance = PostFileContent(file=file, user=user)
				file_instance.save()
				files_objs.append(file_instance)

			p, created = Post.objects.get_or_create(caption=caption, user=user)
			p.tags.set(tags_objs)
			p.content.set(files_objs)
			p.save()
			return redirect('index')
	else:
		form = NewPostForm()

	context = {
		'form':form,
	}

	return render(request, 'newpost.html', context)


@login_required
def EditPost(request, post_id):
	user = request.user
	post = Post.objects.get(id=post_id)
	postss = get_object_or_404(Post, id=post_id)
	tags_objs = []
	files_objs = []

	if request.method == 'POST':
		form = NewPostForm(request.POST, request.FILES, instance=post)
		if form.is_valid():
			post.files = request.FILES.getlist('content')
			post.caption = form.cleaned_data.get('caption')
			post.tags_form = form.cleaned_data.get('tags')

			tags_list = list(post.tags_form.split(','))

			for tag in tags_list:
				t, created = Tag.objects.get_or_create(title=tag)
				tags_objs.append(t)

			for file in post.files:
				file_instance = PostFileContent(file=file, user=user)
				file_instance.save()
				files_objs.append(file_instance)

			post.tags.set(tags_objs)
			post.content.set(files_objs)
			post.save()
			return redirect('profile', user)
	else:
		form = NewPostForm(instance=post)

	context = {
		'form':form,
		'postss':postss,
	}

	return render(request, 'editpost.html', context)

@login_required
def delete_post(request,post_id):
	
	post_to_delete=Post.objects.get(id=post_id)
	post_to_delete.delete()
	return redirect('profile', request.user)


def tags(request, tag_slug):
	tag = get_object_or_404(Tag, slug=tag_slug)
	posts = Post.objects.filter(tags=tag).order_by('-posted')

	template = loader.get_template('tag.html')

	context = {
		'posts':posts,
		'tag':tag,
	}

	return HttpResponse(template.render(context, request))



@login_required
def like(request, post_id):
	user = request.user
	post = Post.objects.get(id=post_id)
	current_likes = post.likes
	liked = Likes.objects.filter(user=user, post=post).count()

	if not liked:
		like = Likes.objects.create(user=user, post=post)
		#like.save()
		current_likes = current_likes + 1

	else:
		Likes.objects.filter(user=user, post=post).delete()
		current_likes = current_likes - 1

	post.likes = current_likes
	post.save()

	return HttpResponseRedirect(reverse('postdetails', args=[post_id]))

@login_required
def favorite(request, post_id):
	user = request.user
	post = Post.objects.get(id=post_id)
	profile = Profile.objects.get(user=user)

	if profile.favorites.filter(id=post_id).exists():
		profile.favorites.remove(post)

	else:
		profile.favorites.add(post)

	return HttpResponseRedirect(reverse('postdetails', args=[post_id]))


@login_required
def download(request, path):
	file_path = os.path.join(settings.MEDIA_ROOT, path)
	if os.path.exists(file_path):
		with open(file_path, 'rb')as fh:
			response=HttpResponse(fh.read(), content_type="application/contents")
			response['Content-Disposition']='inline;filename'+os.path.basename(file_path)
			return response
	raise Http404

def usersettings(request):

	return render(request, 'settings.html')