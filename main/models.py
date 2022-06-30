from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from datetime import date


# Create your models here.

class City(models.Model):
    name = models.CharField(verbose_name='Название', max_length=70)

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'

    def __str__(self):
        return self.name


class Inductee(models.Model):  # призывник
    name = models.CharField(max_length=64, verbose_name='Имя')
    surname = models.CharField(max_length=64, verbose_name='Фамилия')
    patronymic = models.CharField(max_length=64, verbose_name='Отчество')
    phone = models.CharField(max_length=11, verbose_name='Телефон', blank=True)
    birthday = models.DateField(null=True, verbose_name='Дата рождения')
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='Город',
                             default=1)
    MILITARY_FITNES_CATEGORY = [
        ('Не определена', 'Не определена'),
        ('A1', 'A1'),
        ('A2', 'A2'),
        ('A3', 'A3'),
        ('A4', 'A4'),
        ('Б1', 'Б1'),
        ('Б2', 'Б2'),
        ('Б3', 'Б3'),
        ('Б4', 'Б4'),
        ('В', 'В'),
        ('Г', 'Г'),
        ('Д', 'Д'),
    ]
    military_category = models.CharField(max_length=14,
                                         choices=MILITARY_FITNES_CATEGORY,
                                         default='Не определена',
                                         verbose_name='Категория годности')

    MILITARY_STATUS_CATEGORY = [
        ('Поставлен на учёт', 'Поставлен на учёт'),
        ('Военнослужащий', 'Военнослужащий'),
        ('В запасе', 'В запасе'),
        ('Снят с учёта', 'Снят с учёта'),
    ]

    military_status = models.CharField(max_length=20,  # военный статус (поставлен, снят с учёта и тд)
                                       choices=MILITARY_STATUS_CATEGORY,
                                       default='Поставлен на учёт',
                                       verbose_name='Военный статус')

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, verbose_name='Пользователь')

    def calculate_age(self):
        today = date.today()
        return today.year - self.birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day))

    def spring_call(self):  # решить вопрос с дублированием призывников с весеннего на осенний семестр
        today = date.today()
        return (today.year - self.birthday.year - (
                    (4, 1) < (self.birthday.month, self.birthday.day))) >= 18  # 1 апреля начало весеннего призыва

    def autumn_call(self):
        today = date.today()
        return (today.year - self.birthday.year - (
                    (10, 1) < (self.birthday.month, self.birthday.day))) >= 18  # 1 октября начало осеннего призыва

    class Meta:
        verbose_name = 'Призывник'
        verbose_name_plural = 'Призывники'

    def __str__(self):
        return '%s %s (%s)' % (self.user.inductee.name,
                               self.user.inductee.surname,
                               self.user.username)


class Responsible_person(models.Model):  # ответственное лицо
    name = models.CharField(max_length=64, verbose_name='Имя')
    surname = models.CharField(max_length=64, verbose_name='Фамилия')
    patronymic = models.CharField(max_length=64, verbose_name='Отчество')
    post = models.CharField(max_length=64, verbose_name='Должность')
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, verbose_name='Пользователь')

    class Meta:
        verbose_name = 'Ответственное лицо'
        verbose_name_plural = 'Ответственные лица'

    def __str__(self):
        return '%s %s (%s)' % (self.user.responsible_person.name,
                               self.user.responsible_person.surname,
                               self.user.username)


class Notification(models.Model):  # уведомление (всем пользователям)
    header = models.CharField(max_length=64, verbose_name='Заголовок уведомления')
    text = models.TextField(max_length=2000, verbose_name='Текст уведомления')
    date_time = models.DateTimeField(auto_now_add=True, verbose_name='Дата уведомления')
    author = models.ForeignKey(Responsible_person, on_delete=models.CASCADE, verbose_name='Сотрудник', default=1)

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'

    def __str__(self):
        return 'Уведомление № %d' % (self.pk)


class Message(models.Model):  # обращение
    header = models.CharField(max_length=64, verbose_name='Заголовок обращения')
    text = models.TextField(max_length=2000, verbose_name='Текст обращения')
    addresser = models.ForeignKey(
        Inductee, on_delete=models.CASCADE, verbose_name='Отправитель')  # при удалении пользователя
    # удаляются адресованные им сообщения
    # respondent = models.ForeignKey(
    # Responsible_person, on_delete=models.CASCADE, verbose_name='Получатель', default=1)

    date_time = models.DateTimeField(auto_now_add=True, verbose_name='Дата обращения')

    is_checked = models.BooleanField(verbose_name='Обработано', default=False)

    class Meta:
        verbose_name = 'Обращение'
        verbose_name_plural = 'Обращения'

    def __str__(self):
        return 'Обращение № %d' % (self.pk)


class Answer_Message(models.Model):  # ответ на обращение
    message = models.OneToOneField(Message, on_delete=models.CASCADE, verbose_name='Обращение')
    answer_text = models.TextField(max_length=2000, verbose_name='Текст ответа')
    date_time = models.DateTimeField(auto_now_add=True, verbose_name='Дата ответа')
    respondent = models.ForeignKey(Responsible_person, on_delete=models.CASCADE, verbose_name='Сотрудник')

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'

    def __str__(self):
        return 'Ответ № %d к обращению № %d' % (self.pk, self.message.pk)


class Recruiting_office(models.Model):  # военкомат/призывной пункт
    name = models.CharField(max_length=64, verbose_name='Название')
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='Город',
                             default=1)
    address = models.CharField(max_length=200, verbose_name='Адрес')

    class Meta:
        verbose_name = 'Военкомат'
        verbose_name_plural = 'Военкоматы'

    def __str__(self):
        return 'Военный комиссариат № %d Название: %s' % (self.pk, self.name)


class Subpoena(models.Model):  # повестка
    to_whom = models.ForeignKey(Inductee, on_delete=models.CASCADE,
                                verbose_name='Кому')  # одному призывнику может приходить несколько повесток
    where_to_come = models.ForeignKey(Recruiting_office, on_delete=models.CASCADE,
                                      verbose_name='Куда')  # один военкомат может быть в нескольких повестках
    when_to_come = models.DateTimeField(auto_now_add=False, verbose_name='Когда', )
    for_what = models.TextField(max_length=2000, verbose_name='Причина вызова')

    class Meta:
        verbose_name = 'Повестка'
        verbose_name_plural = 'Повестки'

    def __str__(self):
        return 'Повестка № %d для %s' % (self.pk, self.to_whom.user.username)


class Military_ID(models.Model):  # военный билет
    to_whom = models.ForeignKey(Inductee, on_delete=models.CASCADE, verbose_name='Кому выдан')
    issued_by = models.ForeignKey(Recruiting_office, on_delete=models.CASCADE, verbose_name='Кем выдан')
    when_issued = models.DateTimeField(auto_now_add=False, verbose_name='Когда выдан')

    class Meta:
        verbose_name = 'Военный билет'
        verbose_name_plural = 'Военные билеты'

    def __str__(self):
        return 'Военный билет № %d Кому выдан: %s' % (self.pk, self.to_whom.user.username)
