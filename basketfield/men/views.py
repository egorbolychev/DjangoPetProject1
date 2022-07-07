from django.contrib.auth import logout, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, HttpResponseNotFound, Http404, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, TemplateView, FormView
from django.views.generic.edit import FormMixin

from .forms import *
from .models import *
from .utils import *


class MenHome(DataMixin, ListView):
    model = Men
    template_name = 'men/index.html'
    context_object_name = 'posts'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Главная страница',
                                      cat_selected=0)
        return context | c_def

    def get_queryset(self):
        return Men.objects.filter(is_published=True).select_related('cat')


# def index(request):
#   posts = Men.objects.all()
#    context = {'posts': posts,
#               'title': 'Главная страница',
#               'cat_selected': 0,
#               'post_selected': 0
#               }
#
#    return render(request, 'men/index.html', context=context)


class Categories(DataMixin, ListView):
    model = Category
    template_name = 'men/index.html'
    context_object_name = 'posts'
    allow_empty = False

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        p = Category.objects.get(slug=self.kwargs['cat_slug'])
        c_def = self.get_user_context(title='Рубрика - ' + p.name,
                                      cat_selected=p.pk)
        return context | c_def

    def get_queryset(self):
        return Men.objects.filter(cat__slug=self.kwargs['cat_slug'], is_published=True).select_related('cat')


# def category(request, cat_slug):
#     pk = Category.objects.get(slug=cat_slug)
#     posts = Men.objects.filter(cat_id=pk)
#     context = {'posts': posts,
#                'title': 'Рубрики',
#                'cat_selected': cat_slug,
#                'post_selected': 0
#                }
#     if len(posts) == 0:
#         raise Http404()
#
#    return render(request, 'men/index.html', context=context)


class SinglePost(FormMixin, DataMixin, DetailView):
    model = Men
    form_class = AddCommentForm
    template_name = 'men/post.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'post'

    def get_success_url(self):
        return reverse('post', kwargs={'post_slug': self.get_object().slug})

    def get_context_data(self, *args, **kwargs):
        context = super(SinglePost, self).get_context_data(**kwargs)
        c_def = self.get_user_context(title=str(context['post'].title),
                                      cat_selected=-1,
                                      comments=context['post'].comments.get_comments(),
                                      likess=context['post'].likes.get_likes().count(),
                                      dislikess=context['post'].likes.get_dislikes().count())
        edit = {}
        if self.request.user.is_authenticated:
            edit = self.get_user_context(
                is_liked=context['post'].likes.filter(user=self.request.user, like=True).exists(),
                is_disliked=context['post'].likes.filter(user=self.request.user, dislike=True).exists(),
            )
        return context | c_def | edit

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if not request.user.is_authenticated:
            return redirect('login')
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        obj = self.get_object()
        form.instance.user = self.request.user
        form.instance.content_type = ContentType.objects.get_for_model(obj)
        form.instance.object_id = obj.pk
        form.save()
        return super().form_valid(form)

# def post(request, post_slug):
#     post = get_object_or_404(Men, slug=post_slug)
#     context = {'post': post,
#                'title': post.title,
#                'cat_selected': -1,
#                }
#
#     return render(request, 'men/post.html', context=context)


class AddLike(LoginRequiredMixin, DataMixin, View):
    model = None
    login_url = reverse_lazy('login')

    def post(self, request, pk, **kwargs):
        user = request.user
        obj = self.model.objects.get(id=pk)
        obj_type = ContentType.objects.get_for_model(obj)

        is_obj, x = Like.objects.get_or_create(content_type=ContentType.objects.get_for_model(obj),
                                               object_id=obj.id, user=request.user)
        is_dislike = is_obj.dislike
        is_like = is_obj.like

        if is_dislike:
            is_obj.dislike = False

        if not is_like:
            is_obj.like = True
        else:
            is_obj.like = False

        is_obj.save()

        # if not (is_like and is_dislike):
        #     Like.objects.get(object_id=pk).delete()

        return HttpResponseRedirect(reverse('post', args=[str(obj.slug)]))


class AddDisLike(LoginRequiredMixin, DataMixin, View):
    model = None
    login_url = reverse_lazy('login')

    def post(self, request, pk, *args, **kwargs):
        user = request.user
        obj = self.model.objects.get(id=pk)
        obj_type = ContentType.objects.get_for_model(obj)

        is_obj, x = Like.objects.get_or_create(content_type=obj_type,
                                               object_id=obj.id, user=user)

        is_dislike = is_obj.dislike
        is_like = is_obj.like

        if is_like:
            is_obj.like = False

        if not is_dislike:
            is_obj.dislike = True
        else:
            is_obj.dislike = False

        is_obj.save()
        return HttpResponseRedirect(reverse('post', args=[str(obj.slug)]))


class About(DataMixin, TemplateView):
    template_name = 'men/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='О нас')
        return context | c_def


# def about(request):
#     return render(request, 'men/about.html', {'title': 'О нас'})


class CreateAcc(DataMixin, CreateView):
    form_class = RegisterUserForm
    template_name = 'men/registration.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Регистрация')
        return context | c_def

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')


class LoginUser(DataMixin, LoginView):
    form_class = LoginUserForm
    template_name = 'men/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Авторизация')
        return context | c_def

    def get_success_url(self):
        return reverse_lazy('home')


class AddPage(LoginRequiredMixin, DataMixin, CreateView):
    form_class = AddPostForm
    template_name = 'men/addpage.html'
    success_url = reverse_lazy('home')
    login_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Добавить статью')
        return context | c_def


# def add_page(request):
#     if request.method == 'POST':
#         form = AddPostForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return redirect('home')
#     else:
#         form = AddPostForm()
#     return render(request, 'men/addpage.html', {'form': form, 'title': 'Добавление статьи'})


def logout_user(request):
    logout(request)
    return redirect('home')


class ContactFormView(DataMixin, FormView):
    form_class = ContactForm
    template_name = 'men/contact.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='О нас')
        return context | c_def

    def form_valid(self, form):
        print(form.cleaned_data)
        return redirect('home')


# def contact(request):
#     return HttpResponse('Связаться с нами')


def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')
