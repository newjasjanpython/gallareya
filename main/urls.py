from django.urls import path
from .views import *

app_name = 'main'

urlpatterns = [
    path('', IndexView.as_view(), name='home'),
    path('view-by', autoredirect_by_image),
    path('about-us/', AboutUsView.as_view()),
    path('view:<int:pk>/art/', ArtView.as_view(), name='art'),
    path('selected-by-categories/', SelectedByCategories.as_view(), name='selected-by-categories'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('rates/', RatedView.as_view(), name='rated'),
    path('room', RoomView.as_view(), name='room'),
    path('register/', register, name="register"),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('theme/', theme_view, name='theme'),
    path('feedback/<int:pk>/', feedback_view),
    path('like/<int:pk>/', like),
    path('set-star/<int:pk>', rate),
    path('get-data-about/--<str:name>--/', info),
    path('get-paged-art-image/', random_art_object),
    path('reupload', regenerate_images),
    path('frame-image-properly', frame_image__upload),
    path('frame/pdf', view_pdf),
    path('get-pdf-image', get_pdf_image),
]
