from django.shortcuts import render, redirect, get_object_or_404
from authy.forms import SignupForm, ChangePasswordForm, EditProfileForm, achievementForm
from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash

from authy.models import Profile, achivement
from post.models import Post, Follow, Stream
from django.db import transaction
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from django.core.paginator import Paginator

from django.urls import resolve

# Create your views here.

def UserProfile(request, username):
	user = get_object_or_404(User, username=username)
	profile = Profile.objects.get(user=user)
	url_name = resolve(request.path).url_name
	achivements = achivement.objects.filter(user=user).all()
	if url_name == 'profile':
		posts = Post.objects.filter(user=user).order_by('-posted')

	else:
		posts = profile.favorites.all()

	#Profile info box
	posts_count = Post.objects.filter(user=user).count()
	
	following_user = Follow.objects.filter(follower=user).all()

	followers_user = Follow.objects.filter(following=user).all()
	following_count = Follow.objects.filter(follower=user).count()
	followers_count = Follow.objects.filter(following=user).count()
	#follow status
	if Follow.objects.filter(following=user).exists():
		follow_status = True
	else: 
		follow_status = False

	postss = profile.favorites.all()

	#Pagination
	paginator = Paginator(posts, 8)
	page_number = request.GET.get('page')
	posts_paginator = paginator.get_page(page_number)

	template = loader.get_template('profile.html')

	context = {
		'posts': posts_paginator,
		'postss':postss,
		'profile':profile,
		'posts_count':posts_count,
		'follow_status':follow_status,
		'url_name':url_name,
		'following_user':following_user,
		'followers_user':followers_user,
		'following_count':following_count,
		'followers_count':followers_count,
		'achivements':achivements,
	}

	return HttpResponse(template.render(context, request))




def Signup(request):
	if request.method == 'POST':
		form = SignupForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			email = form.cleaned_data.get('email')
			password = form.cleaned_data.get('password')
			User.objects.create_user(username=username, email=email, password=password)
			return redirect('index')
	else:
		form = SignupForm()
	
	context = {
		'form':form,
	}

	return render(request, 'signup.html', context)


@login_required
def PasswordChange(request):
	user = request.user
	if request.method == 'POST':
		form = ChangePasswordForm(request.POST)
		if form.is_valid():
			new_password = form.cleaned_data.get('new_password')
			user.set_password(new_password)
			user.save()
			update_session_auth_hash(request, user)
			return redirect('change_password_done')
	else:
		form = ChangePasswordForm(instance=user)

	context = {
		'form':form,
	}

	return render(request, 'change_password.html', context)

def PasswordChangeDone(request):
	return render(request, 'change_password_done.html')


@login_required
def EditProfile(request):
	user = request.user.id
	profile = Profile.objects.get(user__id=user)
	BASE_WIDTH = 400

	if request.method == 'POST':
		form = EditProfileForm(request.POST, request.FILES, instance=request.user.profile)
		if form.is_valid():
			profile.picture = form.cleaned_data.get('picture')
			profile.background = form.cleaned_data.get('background')
			profile.first_name = form.cleaned_data.get('first_name')
			profile.last_name = form.cleaned_data.get('last_name')
			profile.location = form.cleaned_data.get('location')
			profile.url = form.cleaned_data.get('url')
			profile.profile_info = form.cleaned_data.get('profile_info')
			profile.save()
			return redirect('profile', request.user)
	else:
		form = EditProfileForm(instance=request.user.profile)

	context = {
		'form':form,
	}
	return render(request, 'edit_profile.html', context)


@login_required
def addachivement(request):
	user = request.user.id

	if request.method == 'POST':
		form = achievementForm(request.POST, request.FILES)
		if form.is_valid():
			achievement = form.save(commit=False)
			achievement.image = form.cleaned_data.get('image')
			achievement.user = request.user

			achievement.save()
			return redirect('profile', request.user)
	else:
		form = achievementForm()

	context = {
		'form':form,
	}

	return render(request, 'add_achievement.html', context)

@login_required
def Editachivement(request, id):
	user = request.user.id
	achievement = achivement.objects.get(id=id)

	if request.method == 'POST':
		form = achievementForm(request.POST, request.FILES, instance=achievement)
		if form.is_valid():
			achievement.image = form.cleaned_data.get('image')

			achievement.save()
			return redirect('profile', request.user)
	else:
		form = achievementForm(instance=achievement)

	context = {
		'form':form,
	}

	return render(request, 'edit_achievement.html', context)

@login_required
def follow(request, username, option):
	following = get_object_or_404(User, username=username)

	try:
		f, created = Follow.objects.get_or_create(follower=request.user, following=following)

		if int(option) == 0:
			f.delete()
			Stream.objects.filter(following=following, user=request.user).all().delete()
		else:
			 posts = Post.objects.all().filter(user=following)[:25]

			 with transaction.atomic():
			 	for post in posts:
			 		stream = Stream(post=post, user=request.user, date=post.posted, following=following)
			 		stream.save()

		return HttpResponseRedirect(reverse('profile', args=[username]))
	except User.DoesNotExist:
		return HttpResponseRedirect(reverse('profile', args=[username]))