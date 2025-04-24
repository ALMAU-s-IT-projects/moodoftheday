from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from django.http import JsonResponse
from django.utils import timezone

from .forms import RegisterForm
from .models import Emotion, MoodEntry

import calendar
import random

# Начальная точка входа
def root_redirect(request):
    User = get_user_model()
    if User.objects.count() == 0:
        return redirect('register')
    return redirect('login')

# Регистрация
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Добро пожаловать, {user.username}!")
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'mood/register.html', {'form': form})

# Вход
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"С возвращением, {user.username}!")
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'mood/login.html', {'form': form})

# Выход
def logout_view(request):
    logout(request)
    messages.info(request, "Вы вышли из аккаунта.")
    return redirect('login')

# Главная страница — выбор эмоции
@login_required
def home_view(request):
    emotions = Emotion.objects.all()
    return render(request, 'mood/home.html', {'emotions': emotions})

# Создание записи с эмоцией
@login_required
def create_mood_view(request, emotion_id):
    emotion = Emotion.objects.get(id=emotion_id)

    image = random.choice(emotion.images.all()) if emotion.images.exists() else None
    track = random.choice(emotion.tracks.all()) if emotion.tracks.exists() else None
    quote = random.choice(emotion.quotes.all()) if emotion.quotes.exists() else None

    if request.method == 'POST':
        note = request.POST.get('note', '').strip()
        if not note:
            messages.warning(request, "Пожалуйста, добавьте текст перед сохранением.")
            return redirect('create_mood', emotion_id=emotion.id)

        MoodEntry.objects.create(
            user=request.user,
            emotion=emotion,
            note=note
        )
        messages.success(request, "Эмоция успешно сохранена!")
        return redirect('home')

    return render(request, 'mood/create_mood.html', {
        'emotion': emotion,
        'image': image,
        'track': track,
        'quote': quote
    })

# Календарь эмоций
@login_required
def mood_history_view(request):
    today = timezone.now().date()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

    entries = MoodEntry.objects.filter(
        user=request.user,
        created_at__year=year,
        created_at__month=month
    )

    mood_by_day = {entry.created_at.day: entry.emotion.color for entry in entries}
    month_calendar = calendar.monthcalendar(year, month)

    months = {
        1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
        5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
        9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
    }

    # переключение месяцев
    prev_month, prev_year = (12, year - 1) if month == 1 else (month - 1, year)
    next_month, next_year = (1, year + 1) if month == 12 else (month + 1, year)

    return render(request, 'mood/history.html', {
        'month_calendar': month_calendar,
        'year': year,
        'month': month,
        'month_name': months.get(month),
        'days': days,
        'mood_by_day': mood_by_day,
        'entries': entries,
        'has_entries': entries.exists(),
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
    })

# Детальный просмотр записи по дню (для popup)
@login_required
def mood_entry_detail(request, year, month, day):
    try:
        entry = MoodEntry.objects.select_related('emotion').get(
            user=request.user,
            created_at__year=year,
            created_at__month=month,
            created_at__day=day
        )
        image = entry.emotion.images.first()
        track = entry.emotion.tracks.first()
        quote = entry.emotion.quotes.first()

        return JsonResponse({
            'emotion': entry.emotion.name,
            'color': entry.emotion.color,
            'note': entry.note,
            'image': image.image.url if image else None,
            'track': track.audio.url if track else None,
            'quote': quote.text if quote else None,
        })
    except MoodEntry.DoesNotExist:
        return JsonResponse({'error': 'Нет записи'}, status=404)

# Профиль пользователя со статистикой
@login_required
def profile_view(request):
    stats = (
        MoodEntry.objects
        .filter(user=request.user)
        .values('emotion__name', 'emotion__color')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    return render(request, 'mood/profile.html', {
        'user': request.user,
        'stats': stats,
    })