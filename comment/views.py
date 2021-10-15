from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, response
from .models import Comment
from django.urls import reverse
from post.models import Post

def delete_cmt(request, cmt_id):
	post_to_delete=Comment.objects.get(id=cmt_id, user=request.user)
	post_to_delete.delete()
    
	return redirect('index')

