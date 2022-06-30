from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views import generic
from .forms import Register_form, AuthForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.views.generic import TemplateView
from django.views.generic import FormView, UpdateView

from .forms import SignUpForm, CreateNotificationForm, CreateSubpoenaForm, CreateSubpoenaForm2, AddMilitaryIDForm, \
    AddRecruitingOfficeForm, FindInducteeForm, SortInducteeForm, ChangeInducteeDataForm, ChangeInducteeDataForm2, City, \
    CreateMessageForm, CreateAnswerMessageForm
from .models import Inductee, Notification, Subpoena, Military_ID, Recruiting_office, Message, Answer_Message, \
    Responsible_person


def index(request):
    return render(request, 'main/index.html')


def logout_view(request):
    success_url = '/main/'
    logout(request)
    return redirect(success_url)


class CreateUser(FormView):
    form_class = SignUpForm
    template_name = 'sign_up.html'
    success_url = '/main/success_registration/'

    def form_valid(self, form):
        user = form.save()  # сохранение созданного пользователя
        user.refresh_from_db()
        first_name = form.cleaned_data.get('first_name')
        last_name = form.cleaned_data.get('last_name')
        patronymic = form.cleaned_data.get('patronymic')
        birthday = form.cleaned_data.get('birthday')
        city = form.cleaned_data.get('city')
        Inductee.objects.create(user=user, name=first_name,  # занесение данных
                                surname=last_name,  # призывника
                                patronymic=patronymic,
                                birthday=birthday,
                                city=city)
        return super(CreateUser, self).form_valid(form)


class AuthUser(FormView):
    form_class = AuthForm
    template_name = 'sign_in.html'
    success_url = '/main/lk/'

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)
            return super(AuthUser, self).form_valid(form)
        else:
            message = 'Неверный логин или пароль'
            return render(self.request, 'sign_in.html', {
                'error_message': message,
                'form': form,
            })


def lk(request):
    return render(request, 'user_lk.html')


def success_page_view(request):
    return render(request, 'main/success_page.html')


def error_page_view(request):
    return render(request, 'main/error_page.html')


def success_registration_page_view(request):
    return render(request, 'main/success_registration_page.html')


class ShowUserLk(generic.TemplateView):
    template_name = 'user_lk/user_lk.html'

    def get(self, request):
        if request.user.is_authenticated and request.user.is_staff:
            return render(request, 'user_lk/user_lk.html')
        elif request.user.is_authenticated:
            inductee = Inductee.objects.filter(user=request.user)
            military_id = Military_ID.objects.filter(to_whom=inductee[0])
            if not military_id:
                context = {
                    'inductee': inductee,
                }
            else:
                context = {
                    'inductee': inductee,
                    'mil_id': military_id,
                    'military_id': military_id[0],
                }
            return render(request, 'user_lk/user_lk.html', context)
        else:
            return redirect('/main/')


# class ShowUserLk(FormView):
# form_class = CreateNotificationForm
# template_name='user_lk.html'
# success_url = '/main/lk/'
# def form_valid(self,form):
# header = form.cleaned_data.get('header')
# text = form.cleaned_data.get('text')
# Notification.objects.create(header=header, text = text)
# return super(ShowUserLk,self).form_valid(form)

class AddNotification(FormView):
    form_class = CreateNotificationForm
    template_name = 'add_pages/add_notification.html'
    success_url = '/main/success/'

    def form_valid(self, form):
        header = form.cleaned_data.get('header')
        text = form.cleaned_data.get('text')
        Notification.objects.create(header=header, text=text, author=self.request.user.responsible_person)
        return super(AddNotification, self).form_valid(form)


class AddNotification2(generic.TemplateView):
    template_name = 'add_pages/add_notification.html'

    def get(self, request):
        form = CreateNotificationForm
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request):
        form = CreateNotificationForm(request.POST)
        if form.is_valid():
            header = form.cleaned_data.get('header')
            text = form.cleaned_data.get('text')
            author = request.user.responsible_person
            Notification.objects.create(header=header, text=text, author=author)  # сохранение созданной повестки
            return redirect('/main/success/')
        else:
            return redirect('/main/error/')


class ShowNotifications(generic.TemplateView):
    template_name = 'information_pages/notifications.html'

    def get(self, request):
        notifications_list = Notification.objects.all()
        context = {'notifications_list': notifications_list}
        return render(request, self.template_name, context)


class InducteeList(generic.TemplateView):
    template_name = 'information_pages/inductee_list.html'

    def get(self, request):
        inductee_list = Inductee.objects.all()
        surnames = []
        for ind in inductee_list:
            if ind.surname not in surnames:
                surnames.append(ind.surname)

        surnames.sort()

        cities = City.objects.all().order_by('name')
        city = None
        sort_method = request.GET.get('sort_field')
        if sort_method is not None:
            form = SortInducteeForm()
            if sort_method == 'По фамилии':
                ind_list = Inductee.objects.order_by('surname')
            elif sort_method == 'По имени':
                ind_list = Inductee.objects.order_by('name')
            else:
                ind_list = Inductee.objects.order_by('-birthday')

            if request.GET.get('surname_filter') != 'None' and request.GET.get('surname_filter') != None:
                surname = request.GET.get('surname_filter')
                ind_list = ind_list.filter(surname=surname)  # если есть фильтр по фамилии, то фильтруем

            if request.GET.get('city_filter') != 'None' and request.GET.get('city_filter') is not None:
                city = City.objects.filter(pk=request.GET.get('city_filter'))[0]
                city_id = request.GET.get('city_filter')
                ind_list = ind_list.filter(city=city_id)  # если есть фильтр по городу, то фильтруем дополнительно

            context = {
                'ind_list': ind_list,
                'form': form,
                'surnames': surnames,
                'cities': cities,
                'surname_filter': request.GET.get('surname_filter'),
                'city_filter': city,
            }
            return render(request, self.template_name, context)
        else:
            form = SortInducteeForm()
            ind_list = Inductee.objects.all()
            city = None
            if request.GET.get('surname_filter') != 'None' and request.GET.get('surname_filter') is not None:
                surname = request.GET.get('surname_filter')
                ind_list = ind_list.filter(surname=surname)  # если есть фильтр по фамилии, то фильтруем

            if request.GET.get('city_filter') != 'None' and request.GET.get('city_filter') is not None:
                city = City.objects.filter(pk=request.GET.get('city_filter'))[0]
                city_id = request.GET.get('city_filter')
                ind_list = ind_list.filter(city=city_id)  # если есть фильтр по городу, то фильтруем дополнительно

            context = {
                'ind_list': ind_list,
                'form': form,
                'surnames': surnames,
                'cities': cities,
                'surname_filter': request.GET.get('surname_filter'),
                'city_filter': city,
            }
            return render(request, self.template_name, context)

    def post(self, request):
        pass


def sort_inductee(request):
    data = {'inuctee_list': None, }
    if request.method == 'GET':
        sort_method = request.GET.get('sort_method')
        if sort_method == 'По фамилии':
            inductee_list = Inductee.objects.order_by('surname')
        elif sort_method == 'По имени':
            inductee_list = Inductee.objects.order_by('name')
        else:
            inductee_list = Inductee.objects.order_by('birthday')
        data = {
            'inuctee_list': inductee_list,
        }
    return JsonResponse(data)


class CreateSubpoena(FormView):
    form_class = CreateSubpoenaForm
    template_name = 'add_pages/create_subpoena.html'
    success_url = '/main/success/'

    def form_valid(self, form):
        subpoena = form.save()  # сохранение созданной повестки
        subpoena.refresh_from_db()
        return super(CreateSubpoena, self).form_valid(form)


class CreateSubpoena2(generic.TemplateView):
    template_name = 'add_pages/create_subpoena.html'
    success_url = '/main/success/'

    def get(self, request):
        inductee_filter = Inductee.objects.all()
        form = CreateSubpoenaForm2(inductee_filter=inductee_filter)

        surnames = []
        for ind in inductee_filter:
            if ind.surname not in surnames:
                surnames.append(ind.surname)  # список фамилий

        surnames.sort()

        cities = City.objects.all().order_by('name')  # список городов
        city = None

        if request.GET.get('surname_filter') != 'None' and request.GET.get('surname_filter') is not None:
            surname = request.GET.get('surname_filter')
            inductee_filter = inductee_filter.filter(surname=surname)  # если есть фильтр по фамилии, то фильтруем

        if request.GET.get('city_filter') != 'None' and request.GET.get('city_filter') is not None:
            city = City.objects.filter(pk=request.GET.get('city_filter'))[0]
            city_id = request.GET.get('city_filter')
            inductee_filter = inductee_filter.filter(
                city=city_id)  # если есть фильтр по городу, то фильтруем дополнительно

        context = {
            'form': CreateSubpoenaForm2(inductee_filter=inductee_filter),
            'surnames': surnames,
            'cities': cities,
            'surname_filter': request.GET.get('surname_filter'),
            'city_filter': city,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = CreateSubpoenaForm2(None, request.POST)
        if form.is_valid():
            subpoena = form.save()  # сохранение созданной повестки
            subpoena.refresh_from_db()
            return redirect('/main/success/')
        else:
            return redirect('/main/error/')


class AddMilitaryID(FormView):
    form_class = AddMilitaryIDForm
    template_name = 'add_pages/add_military_id.html'
    success_url = '/main/success/'

    def form_valid(self, form):
        miliraty_id = form.save()  # сохранение созданного военного билета
        miliraty_id.refresh_from_db()
        inductee = miliraty_id.to_whom
        inductee.military_status = 'В запасе'  # внесение данных, что призывник отслужил
        inductee.save()  # сохранение изменений
        return super(AddMilitaryID, self).form_valid(form)


class AddRecruitingOffice(FormView):
    form_class = AddRecruitingOfficeForm
    template_name = 'add_pages/add_recruiting_office.html'
    success_url = '/main/success/'

    def form_valid(self, form):
        recruiting_office = form.save()  # сохранение созданного военного комиссариата
        recruiting_office.refresh_from_db()
        return super(AddRecruitingOffice, self).form_valid(form)


class ShowSubpoenas(generic.TemplateView):
    template_name = 'information_pages/user_subpoenas.html'

    def get(self, request):
        subpoenas_list = Subpoena.objects.filter(to_whom=request.user.inductee)
        context = {'subpoenas_list': subpoenas_list}
        return render(request, self.template_name, context)


class ShowMessages(generic.TemplateView):
    template_name = 'information_pages/user_messages.html'

    def get(self, request):
        messages = Message.objects.filter(addresser=request.user.inductee)
        context = {
            'messages': messages,
        }
        return render(request, self.template_name, context)


class ShowInducteePage(generic.TemplateView):
    template_name = 'information_pages/inductee_page.html'

    def get(self, request):
        inductee_filter = Inductee.objects.all().order_by('surname')
        form = FindInducteeForm(inductee_filter=inductee_filter)

        surnames = []
        for ind in inductee_filter:
            if ind.surname not in surnames:
                surnames.append(ind.surname)

        surnames.sort()

        cities = City.objects.all().order_by('name')
        city = None
        inductee_list = Inductee.objects.all().order_by('surname')
        inductee_pk = request.GET.get('inductee')
        if inductee_pk is not None and inductee_pk != '':
            inductee = Inductee.objects.filter(pk=inductee_pk)
        else:
            inductee = None

        if not inductee:
            if request.GET.get('surname_filter') != 'None' and request.GET.get('surname_filter') is not None:
                surname = request.GET.get('surname_filter')
                inductee_filter = inductee_filter.filter(surname=surname).order_by(
                    'surname')  # если есть фильтр по фамилии, то фильтруем

            if request.GET.get('city_filter') != 'None' and request.GET.get('city_filter') is not None:
                city = City.objects.filter(pk=request.GET.get('city_filter'))[0]
                city_id = request.GET.get('city_filter')
                inductee_filter = inductee_filter.filter(city=city_id).order_by(
                    'surname')  # если есть фильтр по городу, то фильтруем дополнительно

            context = {
                'inductee_list': inductee_list,
                'form': FindInducteeForm(inductee_filter=inductee_filter),
                'surnames': surnames,
                'cities': cities,
                'surname_filter': request.GET.get('surname_filter'),
                'city_filter': city,
            }
        else:
            if request.GET.get('surname_filter') != 'None' and request.GET.get('surname_filter') is not None:
                surname = request.GET.get('surname_filter')
                inductee_filter = inductee_filter.filter(surname=surname).order_by(
                    'surname')  # если есть фильтр по фамилии, то фильтруем

            if request.GET.get('city_filter') != 'None' and request.GET.get('city_filter') is not None:
                city_id = request.GET.get('city_filter')
                inductee_filter = inductee_filter.filter(city=city_id).order_by(
                    'surname')  # если есть фильтр по городу, то фильтруем дополнительно

            ind = inductee[0]
            change_form = ChangeInducteeDataForm(initial={
                'name': ind.name,
                'surname': ind.surname,
                'patronymic': ind.patronymic,
                'phone': ind.phone,
                'birthday': ind.birthday,
                'military_category': ind.military_category,
                'military_status': ind.military_status,
                'city': ind.city,
            })
            military_id = Military_ID.objects.filter(to_whom=inductee[0])
            if not military_id:  # если у призывника нет военного билета
                context = {
                    'inductee_list': inductee_list,
                    'form': FindInducteeForm(inductee_filter),
                    'inductee': ind,
                    'change_form': change_form,
                    'surnames': surnames,
                    'cities': cities,
                }
            else:
                context = {
                    'inductee_list': inductee_list,
                    'form': FindInducteeForm(inductee_filter),
                    'inductee': ind,
                    'military_id': military_id[0],
                    'change_form': change_form,
                    'surnames': surnames,
                    'cities': cities,
                }
        return render(request, self.template_name, context)

    def post(self, request):
        inductee_pk = request.GET.get('inductee')
        ind = Inductee.objects.filter(pk=inductee_pk)
        inductee = ind[0]

        form = ChangeInducteeDataForm(request.POST)
        if form.is_valid():
            inductee.name = request.POST.get('name')
            inductee.user.first_name = request.POST.get('name')
            inductee.surname = request.POST.get('surname')
            inductee.user.last_name = request.POST.get('surname')
            inductee.patronymic = request.POST.get('patronymic')
            inductee.phone = request.POST.get('phone')
            inductee.military_category = request.POST.get('military_category')
            inductee.military_status = request.POST.get('military_status')
            inductee.city = City.objects.filter(pk=request.POST.get('city'))[0]
            inductee.save()
            inductee.user.save()
            return redirect('/main/success/')
        return render(request, self.template_name, context={
            'valid_or_not': 'form is not valid'
        })


class ChangeInducteeData(generic.TemplateView):
    template_name = 'user_lk/user_data.html'
    success_url = '/main/success/'

    def get(self, request):
        ind = request.user.inductee
        change_form = ChangeInducteeDataForm2(initial={
            'name': ind.name,
            'surname': ind.surname,
            'patronymic': ind.patronymic,
            'phone': ind.phone,
            'birthday': ind.birthday,
            'military_category': ind.military_category,
            'military_status': ind.military_status,
            'city': ind.city,
        })
        context = {
            'inductee': ind,
            'change_form': change_form,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        inductee = request.user.inductee
        inductee.phone = request.POST.get('phone')
        inductee.city = City.objects.filter(pk=request.POST.get('city'))[0]
        inductee.save()
        inductee.user.save()
        return redirect('/main/success/')


class CreateMessage(generic.TemplateView):
    template_name = 'add_pages/create_message.html'
    success_url = '/main/success/'

    def get(self, request):
        form = CreateMessageForm()
        context = {
            'user': request.user,
            'form': form,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = CreateMessageForm()
        header = request.POST.get('header')
        text = request.POST.get('text')
        if request.user.is_staff:
            addresser = request.user.responsible_person
        else:
            addresser = request.user.inductee
        # respondent = None
        new_message = Message(header=header, text=text, addresser=addresser)
        new_message.save()
        new_message.refresh_from_db()
        return redirect('/main/success/')


class InducteeMessages(generic.TemplateView):
    template_name = 'information_pages/inductee_messages.html'

    def get(self, request):
        messages = Message.objects.filter(is_checked=False)
        if request.GET.get('id'):
            message_for_answer = Message.objects.filter(pk=request.GET.get('id'))[0]
            answer_form = CreateAnswerMessageForm()
            context = {
                'message_for_answer': message_for_answer,
                'messages': messages,
                'inf_request': request.GET,
                'id_message': request.GET.get('id'),  # так мы узнаем id обращения, на которое нужно сделать ответ
                'form': answer_form,
            }
        else:
            context = {
                'messages': messages,
            }
        return render(request, self.template_name, context)

    def post(self, request):
        respondent = request.user.responsible_person
        message = Message.objects.filter(pk=request.POST.get('id'))[0]
        answer_text = request.POST.get('answer_text')
        answer = Answer_Message(message=message, respondent=respondent, answer_text=answer_text)
        answer.save()
        answer.refresh_from_db()
        message.is_checked = True
        message.save()
        message.refresh_from_db()
        return redirect('/main/success/')
