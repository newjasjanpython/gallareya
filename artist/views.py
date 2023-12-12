from django.shortcuts import render, redirect, get_object_or_404
from django.http.response import JsonResponse
from django.core.paginator import Paginator
from .models import SOCIALS_AVAIBLE, Social, MeUser
from django.views.generic import *
from django.conf import settings
from main.models import *
from .mixins import *
from .forms import *
import uuid
import os
import requests

# Create your views here.


def check_and_create(instance):    
    if not hasattr(instance, 'webuser'):
        web_user = WebUser.objects.create(
            user=instance
        )

    if not hasattr(instance, 'artist_obj'):
        Artist.objects.create(
            user=instance,
            fullname=instance.first_name,
            about="Ma'lumotlar berilmagan",
            image=web_user.image
        )



class IndexPage(View):
    def get(self, request, slug):
        context = {}

        if slug.startswith(' '):
            slug = '+' + slug.strip().strip('+')

        try:
            user = MeUser.objects.get(slug=slug)
            check_and_create(user)

            context['vuser'] = user

            artist = Artist.objects.get(user=user)
            
            context['artist'] = artist

            arts = Art.objects.filter(artist=artist)

            context['arts'] = arts
        except Exception as err:
            raise err
            return redirect('/')
        
        context['page_name'] = 'index'

        return render(request, 'profile/index.html', context)


class ListDrafts(View):
    def get(self, req, slug):        
        if slug.startswith(' '):
            slug = '+' + slug.strip().strip('+')

        if slug == req.user.slug:
            context = {
                'columns': [
                    {'name': "Surat"},
                    {'name': "Nomi", 'bcname': 'name'},
                    {'name': "Surat haqida", 'bcname': 'about'},
                    {'name': "Categories",},
                    {'name': "Checked", 'bcname': 'verified'},
                ]
            }

            user = MeUser.objects.get(slug=slug)
            check_and_create(user)
            context['vuser'] = user

            rows = []

            paged = Paginator(list(OnVerifyArt.objects.filter(artist=req.user.artist_obj).order_by(req.GET.get('filter', '-pk'))), 16)
            try:
                paged = paged.get_page(int(req.GET.get('page', 0))).object_list
            except:
                paged = paged.get_page(1).object_list

            for i in paged:
                link = ""
                names = ""

                for c in i.categories.all():
                    link += f"{c.pk},"
                    names += f"{c.name},"

                html = f"<a href=\"/selected-by-categories?categories={link.strip(',')}\">{names.strip(',')}</a>"

                data = [
                    {"type": "text", 'text': "Telegramda yuklangan"},
                    {"type": "text", 'text': i.name},
                    {"type": "text", 'text': i.about},
                    {"type": "html", 'html': html},
                    {"type": "bool", 'bool': i.verified},
                ]
                
                rows.append(data)

            context['rows'] = rows
            context['page_name'] = 'list_drafts'

            return render(req, 'profile/list.html', context)
        return redirect(f'/profile/{slug}')


class ListNotifications(View):
    def get(self, req, slug):        
        if slug.startswith(' '):
            slug = '+' + slug.strip().strip('+')

        if slug == req.user.slug:
            context = {
                'columns': [
                    {'name': "Image"},
                    {'name': "Nomi", 'bcname': 'name'},
                    {'name': "Surat haqida", 'bcname': 'about'},
                    {'name': "Izoh", 'bcname': 'text'},
                ]
            }
            
            user = MeUser.objects.get(slug=slug)
            check_and_create(user)
            context['vuser'] = user

            rows = []

            paged = Paginator(list(OnVerifyArt.objects.filter(text__isnull=False, artist=req.user.artist_obj).order_by(req.GET.get('filter', '-pk'))), 16)
            try:
                paged = paged.get_page(int(req.GET.get('page', 0))).object_list
            except:
                paged = paged.get_page(1).object_list

            for i in paged:
                link = ""
                names = ""

                for c in i.categories.all():
                    link += f"{c.pk},"
                    names += f"{c.name},"

                data = [
                    {"type": "text", 'text': "Telegramda yuklangan"},
                    {"type": "text", 'text': i.name},
                    {"type": "text", 'text': i.about},
                    {"type": "text", 'text': i.text.replace('/reply', '')},
                ]
                
                if i.viewed == False and i.text != None:
                    i.viewed = True
                    i.save()

                rows.append(data)

            context['rows'] = rows
            context['page_name'] = 'list_notif'

            return render(req, 'profile/list.html', context)
        return redirect(f'/profile/{slug}')


class ListArtistArts(View):
    def get(self, request, slug):
        if slug.startswith(' '):
            slug = '+' + slug.strip().strip('+')

        user = get_object_or_404(MeUser, slug=slug)

        context = {
            'u': user,
        }

        if 'category' in request.GET.keys():
            context['objects'] = user.artist_obj.arts.filter(categories=get_object_or_404(Category, pk=request.GET.get('category')))
        else:
            context['objects'] = user.artist_obj.arts.all()

        user = MeUser.objects.get(slug=slug)
        check_and_create(user)
        context['vuser'] = user

        if 'view-main' in request.GET.keys():
            try:
                context['main'] = Art.objects.get(pk=request.GET['view-main'])
            except Exception as err:
                context['err'] = str(err)

        return render(request, 'list-artist-arts.html', context)


class CommentsView(View):
    def get(self, req, slug):
        context = {}
        if slug.startswith(' '):
            slug = '+' + slug.strip().strip('+')

        user = MeUser.objects.get(slug=slug)
        check_and_create(user)

        context['vuser'] = user
        context['page_name'] = 'comments'

        return render(req, 'profile/comments.html', context)


class SocialsView(View):
    def get(self, req, slug):
        context = {}
        if slug.startswith(' '):
            slug = '+' + slug.strip().strip('+')

        user = MeUser.objects.get(slug=slug)
        check_and_create(user)
        context['vuser'] = user
        context['page_name'] = 'socials'
        context['socials_avaible'] = SOCIALS_AVAIBLE

        return render(req, 'profile/socials.html', context)
    
    def post(self, req, slug):
        if slug.startswith(' '):
            slug = '+' + slug.strip().strip('+')
        if slug == req.user.slug:
            name = req.POST.get('name', None)
            link = req.POST.get('link', None)

            if link and name:
                if req.POST.get('edit'):
                    s = Social.objects.get(pk=req.POST.get('edit'))
                    s.name = name
                    s.link = link
                    s.save()
                else:
                    Social.objects.create(user=req.user, name=name, link=link)
        return redirect(f"/profile/{slug}/socials")


class OnVerificationCreateView(TokenMixin, View):
    def post(self, request):
        name = request.POST['name']
        categories = list(map(lambda pk: Category.objects.get(pk=pk), request.POST['categories'].split(',')))
        about = request.POST['about']
        artist = Artist.objects.get(pk=request.POST['artist'])
        image_url = request.POST['image']

        instance = OnVerifyArt.objects.create(name=name, about=about, artist=artist, image=image_url)

        for cat in categories:
            instance.categories.add(cat)
        
        instance.save()

        return JsonResponse({'status': 'ok', 'code': 200, 'detail': 'Form acceptable.', 'pk': instance.pk}, safe=False, status=200)


class OnVerificationManageView(TokenMixin, View):
    def post(self, req):
        instance = req.POST['instance']
        instances = OnVerifyArt.objects.filter(pk=instance)
        instance = instances.values('pk', 'name', 'image')[0]

        if req.POST.get('delete') == 'ok':
            instances[0].delete()

        return JsonResponse(instance, safe=False)


class VerifyView(TokenMixin, View):
    def post(self, request):
        try:
            object_instance = OnVerifyArt.objects.filter(pk=request.POST.get('instance'))[0]
            object_instance.verified = True

            image_name = str(uuid.uuid4()) + '.jpg'
            image_path = 'images/arts/' + image_name
            image = requests.get(object_instance.image).content

            with open(os.path.normpath(os.path.join(settings.MEDIA_ROOT, image_path)), 'w+b') as f:
                f.write(image)

            art = Art.objects.create(name=object_instance.name or "", about=object_instance.about, artist=object_instance.artist,
                                     image=image_path)
            for cat in object_instance.categories.all():
                art.categories.add(cat)
            art.save()
            object_instance.save()

            return JsonResponse({'status': 'ok', 'code': 200, 'detailt': 'Verified', 'pk': art.pk, 'name': art.name})
        except Exception as err:
            print(err)
            return JsonResponse({'status': 'error', 'code': 500, 'detail': 'No object to verify', 'error': str(err)}, safe=False, status=500)


class AddMessageView(TokenMixin, View):
    def post(self, req, art):
        text = req.POST['text']
        art = OnVerifyArt.objects.get(pk=art)

        art.text = text
        art.viewed = True

        art.save()

        return JsonResponse({'status': 'ok'})


def get_categories(req):
    return JsonResponse([{'pk': i.pk, 'name': i.name} for i in Category.objects.all()], safe=False)


def is_artist(req, sk):
    try:
        artist = Artist.objects.get(secure_key=sk)
        return JsonResponse({'status': 'ok', 'detail': 'exists', 'data': {
                'pk': artist.pk, "name": artist.get_name(), "about": artist.about, "info": artist.get_link(), "image": artist.get_image(), 'slug': artist.user.slug
            }
        })
    except:
        return JsonResponse({'status': 'error', 'detail': 'not exists'})


def privacy(request, slug):
    if request.method == 'POST':
        if request.user.is_authenticated:
            try:
                user = MeUser.objects.get(slug=slug)
                if user == request.user:
                    user.privacy = not user.privacy
                    user.save()
            except Exception:
                pass
    return redirect(request.POST.get('next', '/'))


def edit_name(request, pk):
    artist = Artist.objects.get(pk=pk)
    if request.user != artist.user:
        return redirect(f'/profile/{request.user.slug}')
    artist.fullname = f"{request.POST.get('first_name', '')} {request.POST.get('last_name', '')}"
    artist.user.first_name = request.POST.get('first_name')
    artist.user.last_name = request.POST.get('last_name')
    artist.save()
    artist.user.save()

    return redirect(request.POST.get('next', '/'))


def edit_about(request, pk=None, slug=None):
    if pk:
        artist = Artist.objects.get(pk=pk)
    else:
        artist = Artist.objects.get(user__username=slug)
    if request.user != artist.user:
        return redirect(f'/profile/{request.user.slug}')
    artist.about = request.POST.get('text')
    artist.save()

    return redirect(request.POST.get('next', '/'))


class EditAboutApi(TokenMixin, View):
    def post(self, request, slug):
        user = MeUser.objects.get(slug=slug)
        user.artist_obj.about = request.POST.get('text')
        user.artist_obj.save()
        user.save()
        return redirect('/')


def edit_image(request, pk):
    artist = Artist.objects.get(pk=pk)
    if request.user != artist.user:
        return redirect(f'/profile/{request.user.slug}')
    artist.user.webuser.image = request.FILES.get('img')
    artist.user.webuser.save()

    return redirect(request.POST.get('next', '/'))

