from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib.messages import error, warning
import time
from django.forms import ModelForm
from django.views.generic import *
from main.models import *
from .mixins import IsAdmin

# Create your views here.


AVAIBLE_MODEL_BY_NAME = {
    'artists': (Artist, 'Sanatkorlar'),
    'arts': (Art, 'Suratlar'),
    'categories': (Category, 'Turlar'),
}

AVAIBLE_MODELS = [
    {"name": "Rassomlar", "slug": 'artists-admin-page-view', 'label': 'artists'},
    {"name": "Suratlar", "slug": 'arts-admin-page-view', 'label': 'arts'},
    {"name": "Turlar", "slug": 'categories-admin-page-view', 'label': 'categories'},
]

SORTED_NAMES = sorted(list(map(lambda t: t['name'], AVAIBLE_MODELS)))
SORTED_AVAIBLLE_MODELS = []

for name in SORTED_NAMES:
    for model in AVAIBLE_MODELS:
        if model['name'] == name:
            SORTED_AVAIBLLE_MODELS.insert(SORTED_NAMES.index(name), model)
            break

del name, model, SORTED_NAMES, AVAIBLE_MODELS


def create_form(model_class):    
    class Form(ModelForm):
        class Meta:
            model = model_class
            fields = '__all__'
    
    return Form


def write_history(req, data):
    try:
        history = req.session['recent-actions']
        history.insert(0, data)
    except Exception as err:
        print(err)
        req.session['recent-actions'] = [data,]
    req.session.save()


class IndexView(IsAdmin, View):
    def get(self, req):
        session = req.session
        context = {}

        try:
            context['list_recent_actions'] = session['recent-actions'][:16]
        except:
            context['list_recent_actions'] = []
            session['recent-actions'] = []

        session.save()
        
        context['avaible_models'] = SORTED_AVAIBLLE_MODELS
        context['page_label'] = 'index'

        return render(req, 'cadmin/dashboard.html', context)


class ListElementsView(IsAdmin, View):
    def get(self, req, name):
        try:
            model, model_name_plural = AVAIBLE_MODEL_BY_NAME[name]
        except:
            warning(req, "Iltimos aniq bir link orqali o'ting.")
            return redirect('/admin/')

        models_paginator = Paginator(list(model.objects.order_by('-id')), 16)
        page = models_paginator.get_page(req.GET.get('page', 1))

        context = {
            'list_models_page': page,
            'name_model': model_name_plural,
            'avaible_models': SORTED_AVAIBLLE_MODELS,
            'page_name': name,
            'page_label': 'list'
        }

        return render(req, 'cadmin/list-it.html', context)


class DeleteView(IsAdmin, View):
    def get(self, req, name, pk):
        try:
            model, model_name_plural = AVAIBLE_MODEL_BY_NAME[name]
        except:
            warning(req, "Iltimos aniq bir link orqali o'ting.")
            return redirect('/admin/')

        try:
            obj = model.objects.get(pk=pk)
            
            data = {
                "icon": "bi bi-trash3",
                "text": f"{model_name_plural}dan #{obj.pk} o'chirilib yuborildi",
                "time_formatted": time.strftime("%Y %b %d %H %p"),
                "time": time.strftime("%Y:%m:%d %H:%M:%S")
            }

            write_history(req, data)
            obj.delete()
        except Exception as r:
            print(r)
            error(req, 'Afsuski ushbu malumot topilmadi.\nU allaqachon o\'chirilgan yoki siz eski link orqali kirgansiz')

        return redirect(f'/admin/{name}-admin-page-view')


class EditView(IsAdmin, View):
    def get(self, req, name, pk):
        try:
            model, model_name_plural = AVAIBLE_MODEL_BY_NAME[name]
        except:
            warning(req, "Iltimos aniq bir link orqali o'ting.")
            return redirect('/admin/')

        try:
            model_obj = model.objects.get(pk=pk)
        except:
            error(req, 'Afsuski ushbu malumot topilmadi.\nU allaqachon o\'chirilgan yoki siz eski link orqali kirgansiz')

            return redirect(f'/{name}-admin-page-view')

        context = {
            'model': model,
            'form': create_form(model)(instance=model_obj),
            'avaible_models': SORTED_AVAIBLLE_MODELS,
            'name_model': model_name_plural,
            'page_name': name,
            'page_label': 'list',
            'deletable': True,
        }

        return render(req, 'cadmin/form.html', context)
    
    def post(self, req, name, pk):
        try:
            model, model_name_plural = AVAIBLE_MODEL_BY_NAME[name]
        except:
            warning(req, "Iltimos aniq bir link orqali o'ting.")
            return redirect('/admin/')

        try:
            model_obj = model.objects.get(pk=pk)
            form = create_form(model)(req.POST, req.FILES, instance=model_obj)

            if form.is_valid():
                form.save()
                
                data = {
                    "icon": "bi bi-pen",
                    "text": f"{model_name_plural}dan #{model_obj.pk} yangilandi",
                    "time_formatted": time.strftime("%Y %b %d %H %p"),
                    "time": time.strftime("%Y:%m:%d %H:%M:%S")
                }

                write_history(req, data)
            else:
                context = {
                    'model': model_obj,
                    'form': form,
                    'avaible_models': SORTED_AVAIBLLE_MODELS,
                    'name_model': model_name_plural,
                    'page_name': name,
                    'page_label': 'list',
                    'deletable': True,
                }

                return render(req, 'cadmin/form.html', context)
        except:
            error(req, 'Afsuski ushbu malumot topilmadi.\nU allaqachon o\'chirilgan yoki siz eski link orqali kirgansiz')

        return redirect(f'/admin/{name}-admin-page-view')

class CreateView(IsAdmin, View):
    def get(self, req, name):
        try:
            model, model_name_plural = AVAIBLE_MODEL_BY_NAME[name]
        except:
            warning(req, "Iltimos aniq bir link orqali o'ting.")
            return redirect('/admin/')

        context = {
            'form': create_form(model)(),
            'avaible_models': SORTED_AVAIBLLE_MODELS,
            'name_model': model_name_plural,
            'page_name': name,
            'page_label': 'list'
        }

        return render(req, 'cadmin/form.html', context)

    def post(self, req, name):
        try:
            model, model_name_plural = AVAIBLE_MODEL_BY_NAME[name]
        except:
            warning(req, "Iltimos aniq bir link orqali o'ting.")
            return redirect('admin/')

        form = create_form(model)(req.POST, req.FILES)
        if form.is_valid():
            instance = form.save(False)
            instance.save()

            data = {
                "icon": "bi bi-plus",
                "text": f"{model_name_plural}dan #{instance.pk} qo'shildi",
                "time_formatted": time.strftime("%Y %b %d %H %p"),
                "time": time.strftime("%Y:%m:%d %H:%M:%S")
            }

            write_history(req, data)
        else:
            context = {
                'form': form,
                'avaible_models': SORTED_AVAIBLLE_MODELS,
                'name_model': model_name_plural,
                'page_name': name,
                'page_label': 'list'
            }

            return render(req, 'cadmin/form.html', context)
        return redirect(f'/admin/{name}-admin-page-view')
