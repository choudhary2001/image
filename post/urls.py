from django.conf import settings
from django.urls import path
from post.views import index, NewPost, PostDetails, tags, like, favorite,  search, usersettings, EditPost, delete_post, contact
from django.conf.urls import url
from django.views.static import serve

urlpatterns = [
   	path('', index, name='index'),
   	path('newpost/', NewPost, name='newpost'),
   	path('<uuid:post_id>', PostDetails, name='postdetails'),
   	path('<uuid:post_id>/like', like, name='postlike'),
   	path('<uuid:post_id>/favorite', favorite, name='postfavorite'),
   	path('tag/<slug:tag_slug>', tags, name='tags'),
	path('search/', search, name='search'),
	url(r'^download/(?P<path>.*)$', serve, {'download_root':settings.MEDIA_ROOT}),
	url('settings/', usersettings, name="usersettings"),
	path('editpost/<uuid:post_id>', EditPost, name='edit-post'),
	path('deletepost/<uuid:post_id>', delete_post, name='delete-post'),
	path('contactus/',contact, name='contactus' ),
]