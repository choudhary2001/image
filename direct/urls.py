from post.views import delete_post
from django.urls import path
from direct.views import Inbox,  Directs, NewConversation, SendDirect
urlpatterns = [
   	path('', Inbox, name='inbox'),
   	path('directs/<username>', Directs, name='directs'),
   	path('new/<username>', NewConversation, name='newconversation'),
   	path('send/', SendDirect, name='send_direct'),

]