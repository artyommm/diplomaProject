from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Notification, Message, Subpoena, Military_ID, Inductee, Recruiting_office, City, Answer_Message
from django.forms import ModelForm
from django.contrib.admin.widgets import AdminDateWidget


class Register_form(forms.Form):
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = 'username'

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Пароли не совпадают')
        return cd['password2']


class SignUpForm(UserCreationForm):
    patronymic = forms.CharField(max_length=64, label='Отчество')
    birthday = forms.DateField(label='Дата рождения', widget=forms.DateInput)
    city = forms.ModelChoiceField(queryset=City.objects.all().order_by('name'), label='Город', required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'patronymic', 'birthday', 'city',
                  'password1', 'password2')


class AuthForm(forms.Form):
    username = forms.CharField(label='Логин')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)


class CreateNotificationForm(forms.Form):
    header = forms.CharField(max_length=64, label='Заголовок уведомления')
    text = forms.CharField(widget=forms.Textarea, label='Текст уведомления')

    class Meta:
        model = Notification
        fields = ('header', 'text')


class CreateSubpoenaForm2(forms.ModelForm):
    def __init__(self, inductee_filter, *args, **kwargs):
        super(CreateSubpoenaForm2, self).__init__(*args, **kwargs)
        if inductee_filter is None:
            self.fields['to_whom'] = forms.ModelChoiceField(queryset=Inductee.objects.all().order_by('surname'),
                                                            label='Кому', required=True)
        else:
            self.fields['to_whom'] = forms.ModelChoiceField(queryset=inductee_filter.order_by('surname'), label='Кому',
                                                            required=True)

    class Meta:
        model = Subpoena
        fields = ('to_whom', 'where_to_come', 'when_to_come', 'for_what')
        widgets = {}


class AddMilitaryIDForm(forms.ModelForm):
    to_whom = forms.ModelChoiceField(queryset=Inductee.objects.filter(military_status='Военнослужащий'),
                                     label='Кому')  # регулировка выпадающего списка

    class Meta:
        model = Military_ID
        fields = ('to_whom', 'issued_by', 'when_issued')


class AddRecruitingOfficeForm(forms.ModelForm):
    city = forms.ModelChoiceField(label='Город', queryset=City.objects.all().order_by('name'))

    class Meta:
        model = Recruiting_office
        fields = ('name', 'city', 'address')


class FindInducteeForm(forms.Form):
    inductee = forms.ModelChoiceField(queryset=Inductee.objects.all().order_by('surname'), label='Призывник',
                                      required=False)

    def __init__(self, inductee_filter, *args, **kwargs):
        super(FindInducteeForm, self).__init__(*args, **kwargs)
        if inductee_filter == None:
            self.fields['inductee'] = forms.ModelChoiceField(queryset=Inductee.objects.all().order_by('surname'),
                                                             label='Призывник', required=False)
        else:
            self.fields['inductee'] = forms.ModelChoiceField(queryset=inductee_filter.order_by('surname'),
                                                             label='Призывник', required=False)

    class Meta:
        fields = 'inductee'


class SortInducteeForm(forms.Form):
    sort_field = forms.ChoiceField(choices=[('По фамилии', 'По фамилии'),
                                            ('По имени', 'По имени'),
                                            ('По дате рождения', 'По дате рождения')],
                                   label='Параметр сортировки')

    class Meta:
        fields = 'sort_field'


class ChangeInducteeDataForm(forms.ModelForm):
    birthday = forms.DateField(label='Дата рождения', widget=forms.DateInput(format='%d.%m.%Y'))
    city = forms.ModelChoiceField(label='Город', queryset=City.objects.all().order_by('name'))

    class Meta:
        model = Inductee
        fields = ('name', 'surname', 'patronymic',
                  'phone', 'military_category', 'city',
                  'military_status')


class CreateMessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('header', 'text')


class ChangeInducteeDataForm2(forms.ModelForm):  # для личного каб. призывника
    city = forms.ModelChoiceField(label='Город', queryset=City.objects.all().order_by('name'))

    class Meta:
        model = Inductee
        fields = ('phone', 'city')


class CreateAnswerMessageForm(forms.ModelForm):
    class Meta:
        model = Answer_Message
        fields = ('answer_text',)
