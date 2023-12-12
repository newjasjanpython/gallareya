from django.http.response import JsonResponse, Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.generic import *
import pypdfium2 as pdfium
from .forms import MultiModelCreationForm
from artist.models import MeUser
from .models import *
import threading
import requests
import os
import io


def get_random_images():
    images = list(Art.objects.filter(on_admin=True).order_by('-pk'))
    return images


# Create your views here.

TOKEN = "5932673280:AAHLayXF1n6tBmPP07taeGCo3xtfUZexWso"

left = imopen('./main/images/left.jpg')
top = imopen('./main/images/top.jpg')
right = imopen('./main/images/right.jpg')
bottom = imopen('./main/images/bottom.jpg')


class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_name'] = 'home'

        digital_arts = Art.objects.filter(categories__pk=10).order_by('-views')[:8]
        fotosurat = Art.objects.filter(categories__pk=11).order_by('-views')[:8]
        man_made = Art.objects.filter(categories__pk=13).order_by('-views')[:8]
        branding = Art.objects.filter(categories__pk=12).order_by('-views')[:8]

        context['digital_arts'] = digital_arts
        context['fotosurat'] = fotosurat
        context['man_made'] = man_made
        context['branding'] = branding

        random_images_by_column = get_random_images()
        context['hero_images'] = random_images_by_column

        return context


def autoredirect_by_image(req):
    art = get_object_or_404(Art, image__iendswith=req.GET.get('path', 'none-dfahkdjsfhljasdhlfkjalsd-s.jpg'))
    return redirect(f'/view:{art.pk}/art')


def view_pdf(req):
    link = req.GET.get('link')
    pages = []
    if link:
        path = os.path.join(os.getcwd(), link.strip('/').strip('\\'))
        pdf = pdfium.PdfDocument(path)
        for i in range(len(pdf)):
            pages.append(f'/get-pdf-image?index=%s&link=%s' % (str(i), link))
        pdf.close()

    return render(req, 'iframe.pdf.html', {'images': pages})


def get_pdf_image(req):
    link = req.GET.get('link')
    index = req.GET.get('index')
    if link and index and index.isdigit():
        path = os.path.join(os.getcwd(), link.strip('/').strip('\\'))
        pdf = pdfium.PdfDocument(path)
        buffer = io.BytesIO()
        pdf[int(index)].render().to_pil().save(buffer, format='JPEG')
        rea_response = HttpResponse(buffer.getvalue(), content_type="image/jpg")
        rea_response['Content-Disappointment'] = 'attachment; filename="image.png"'
        pdf.close()
        return rea_response
    raise Http404("No Image Found")


class AboutUsView(TemplateView):
    template_name = "about-us.html"


class ArtView(DetailView):
    template_name = 'art.html'
    model = Art

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        
        if self.request.user.is_authenticated:
            try:
                viewed_arts = self.request.session['viewed_arts']
                if obj.pk not in viewed_arts:
                    obj.views += 1
            except KeyError:
                self.request.session['viewed_arts'] = [obj.pk]
                obj.views += 1
            obj.save()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_name'] = 'arts'
        viewed_art = context['object']

        branding = Category.objects.get(pk=12)
        if branding in viewed_art.categories.all():
            context['is_branding'] = True
        bests = Art.objects.order_by('-likes')[:140]
        if viewed_art in bests:
            context['display'] = True
        return context


class SelectedByCategories(ListView):
    template_name = 'publications.html'
    model = Art
    paginate_by = 16
    categories = []

    def get_queryset(self):
        list_categories = self.request.GET.get('categories', '').strip().strip(',').strip()
        if ':' in list_categories:
            list_categories, add = list_categories.split(':')
        else:
            add = None

        if '|' in list_categories:
            list_categories, remove = list_categories.split('|')
        else:
            remove = None

        list_categories = list(set(list_categories.split(',')))

        if add:
            list_categories.append(add)

        if remove:
            try:
                list_categories.remove(remove)
            except ValueError:
                pass
        
        try:
            list_categories.remove('')
        except:
            pass

        list_categories = sorted(list(Category.objects.get(pk=i) for i in set(list_categories)))

        object_list = []

        for i in list_categories:
            object_list.extend(list(i.carts.all()))

        return list(set(object_list))


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['categories'] = Category.objects.all()

        return context


class RatedView(View):
    def get(self, request):
        context = {}
        aall = False

        if 'collective' in request.GET:
            context[f'is_{request.GET["collective"]}'] = 'active'
            if request.GET['collective'] != 'null':
                artists = {}
                category = get_object_or_404(Category, pk=request.GET['collective'])
                arts = category.carts.all()
                for art in arts:
                    try:
                        artists[art.artist.pk]['likes'] += art.likes
                    except:
                        artists[art.artist.pk] = {
                            "fullname": art.artist.fullname,
                            "artist": art.artist,
                            "slug": art.artist.user.slug,
                            "likes": art.likes
                        }
            else:
                aall = True
        else:
            aall = True

        if aall:
            artists = {}
            for category in Category.objects.all():
                arts = category.carts.all()
                for art in arts:
                    try:
                        artists[art.artist.pk]['likes'] += art.likes
                    except:
                        artists[art.artist.pk] = {
                            "fullname": art.artist.fullname,
                            "artist": art.artist,
                            "slug": art.artist.user.slug,
                            "likes": art.likes
                        }

        artists = sorted(artists.values(), key=lambda a: a['likes'], reverse=True)
        context['object_list'] = artists

        return render(request, 'rating.html', context)


class RoomView(View):
    def get(self, req):
        filters = {}
        wall_image = '/assets/three/example/Texture_Wall.jpg'
        floor_image = '/assets/three/example/Texture_Floor.jpg'

        room_name = "Filterli"
        if 'artist' in req.GET.keys():
            filters['artist'] = req.GET.get('artist')
            room_name = get_object_or_404(Artist, pk=filters.get('artist', None))
            room_name = room_name.user.first_name + "ning suratlari"

        if 'category' in req.GET.keys():
            category = req.GET.get('category')
            filters['categories'] = category
            if int(req.GET.get('category')) == 12:
                return redirect('/')
            category = Category.objects.get(pk=req.GET.get('category'))
            if category.wall_image:
                wall_image = category.wall_image.url
            if category.floor_image:
                floor_image = category.floor_image.url
            room_name = category.name

        arts = list(Art.objects.filter(**filters).exclude(categories__id=12))

        pagination = Paginator(arts, 20)
        try:
            page = int(req.GET.get('page', 1))
        except (ValueError, KeyError):
            page = 1

        page = pagination.get_page(page)

        object_list = page.object_list

        if not object_list:
            redirect_url = f"{req.path}?page=1"
            if 'artist' in filters:
                redirect_url += '&artist=' + filters['artist']
            if 'category' in filters:
                redirect_url += '&category=' + filters['category']
            return redirect(redirect_url)

        page_dat = {'object_list': object_list, 'wall_image': wall_image}
        page_dat['wall_image'] = wall_image
        page_dat['floor_image'] = floor_image

        return render(req, f"three/example/index.html", {'room_data': {'name': room_name}, 'page': page_dat, 'pag': page})


class ContactView(View):
    def get(self, req):
        return render(req, 'contact.html')

    def post(self, req):
        fullname = req.POST.get('fullname')
        tel = req.POST.get('tel')
        email = req.POST.get('email')
        subject = req.POST.get('subject')
        message = req.POST.get('text')

        def main():
            message_html = """
<b>{}</b>
<i>{}</i> - <b><i>{}</i></b>

--------------------
<b>{}</b>
{}"""

            message_html = message_html.format(fullname, tel, email, subject, message)

            requests.get(f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id=@digital_gallary&parse_mode=html&text={message_html}')
        
        t = threading.Thread(target=main)
        t.start()

        return redirect('/contact')


@login_required
def feedback_view(request, pk):
    if request.method == 'POST':
        feedback_text = request.POST.get('text')

        art = Art.objects.get(pk=pk)
        try:
            Feedback.objects.create(art=art, web_user=request.user.webuser, message=feedback_text)
        except:
            return redirect(f'/login?next=/view:{pk}/art')
    return redirect(f'/view:{pk}/art')

def like(req, pk):
    art = Art.objects.get(pk=pk)

    if req.user.is_authenticated: 
        try:
            if str(pk) not in req.user.webuser.data.split(','):
                art.likes += 1
                req.user.webuser.data += f',{pk}'
        except Exception:
            req.user.webuser.data = str(pk)
            art.likes += 1
        print(req.user.webuser.data)
        req.user.webuser.save()
    else:
        return redirect(f'/login?auto-register=True&next=/like/{pk}')
    art.save()

    return redirect(f'/view:{pk}/art')


@login_required
def info(req, name):
    try:
        art = Art.objects.filter(image__endswith=name)[0]
        
        data = {'text': art.about}
    except:
        data = {'text': 'No data'}
    
    return JsonResponse(data)


@login_required
def random_art_object(req):
    categories = req.GET.get('categories', '').split(',')
    if len(categories):
        categories_models = set()

        for category in categories:
            try:
                categories_models.add(Category.objects.get(pk=category))
            except:
                pass
    else:
        categories = list(Category.objects.all())

    arts = []

    for i in categories_models:
        arts.extend(list(i.carts.all()))

    arts = list(set(arts))

    paginator = Paginator(arts, 1)

    page = int(req.GET.get('page', 1))
    page = paginator.get_page(page)
    _object = page[0]

    next_page = 1

    if len(paginator.get_page(int(req.GET.get('page', 1)) + 1)) == 8:
        next_page = int(req.GET.get('page', 1)) + 9

    data = {
        'image': _object.image.url if _object.image else _object.image_url,
        'name': _object.name,
        'pk': _object.pk,
        'href': f'/view:{_object.pk}/art',
        'next_page': next_page
    }

    return JsonResponse(data, safe=False)



def register(request):
    if request.method == 'POST':
        form = MultiModelCreationForm(request.POST, request.FILES)

        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            return redirect('/')
        error_message = ""
    else:
        form = MultiModelCreationForm()
        error_message = ""

    context = {
        'form': form,
        "error_message": error_message
    }

    return render(request, 'register.html', context)

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password1"]
        auto_register = request.GET.get('auto-register')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect("/")
        else:
            if (not MeUser.objects.filter(username=username).exists()) and auto_register:
                user = MeUser.objects.create(first_name='User', email="not@given.uz",
                                             username=username, password=password, privacy=True)
                user.first_name = f"User #{user.pk}"

                Artist.objects.create(
                    user=user,
                    fullname=f"User #{user.pk}",
                    about="Ma'lumotlar berilmagan"
                )
                WebUser.objects.create(
                    user=user
                )

                user.save()
                login(request, user)
                return redirect(request.GET.get('next', '/'))
            else:
                error_message = "No'tog'ri raqam yoki parol."
    else:
        error_message = ""
    return render(request, "login.html", {"error_message": error_message})


def logout_view(req):
    logout(req)

    return redirect('/login')


def theme_view(req):
    try:
        if req.session['theme'] == 'light':
            req.session['theme'] = 'dark'
        else:
            req.session['theme'] = 'light'
    except:
        req.session['theme'] = 'light'
    return redirect(req.GET.get('next', '/'))


@login_required
def rate(req, pk):
    art = get_object_or_404(Art, pk=pk)
    if art.artist != req.user.artist_obj:
        try:
            try:
                if pk not in req.session['rated']:
                    Rate.objects.create(object_elem=art, rate=req.POST.get('value'))
                    req.session['rated'].append(pk)
            except:
                Rate.objects.create(object_elem=art, rate=req.POST.get('value'))
                req.session['rated'] = [pk]
        except:
            raise Http404()
    return JsonResponse({'status': 'ok'})


def regenerate_images(request):
    try:
        if request.method == 'POST':
            about_text = request.POST.get('about_text')
            image = request.FILES.get('image')

            if about_text and image:
                art = Art.objects.get(about=about_text)
                art.image = image
                art.save()
    except:
        pass
    return redirect('/')


def frame_image__upload(request):
    try:
        image = imopen(request.GET.get('path'))

        image.paste(left.resize((30, image.height)).copy(), (0, 0))
        image.paste(top.resize((image.width, 30)).copy(), (0, 0))
        image.paste(right.resize((30, image.height)).copy(), (image.width - 30, 0))
        image.paste(bottom.resize((image.width, 30)).copy(), (0, image.height - 30))

        buffer = io.BytesIO()
        image.save(buffer, format='JPEG')

        rea_response = HttpResponse(buffer.getvalue(), content_type="image/jpg")
        rea_response['Content-Disappointment'] = 'attachment; filename="image.png"'
        return rea_response
    except Exception as err:
        print(err)
        raise Http404("No image with this path")


def handler404(request, exeption):
    res = render(request, '404.html')
    res.status_code = 404
    return res


def handler500(request):
    res = render(request, '404.html')
    res.status_code = 404
    return res
