from django.urls import path
from .views import return_html_response

urlpatterns = [
    path('<str:username>', return_html_response.as_view())
]
