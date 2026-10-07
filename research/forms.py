from datetime import date

from django import forms
from django.core.exceptions import ValidationError

from .models import Research


class ResearchForm(forms.ModelForm):
    

    class Meta:
        model = Research
        fields = [
            'title', 'author', 'field', 'description',
            'start_date', 'end_date', 'status', 'budget',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название'}),
            'author': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ФИО'}),
            'field': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например, физика'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if len(title) < 3:
            raise ValidationError('Название должно содержать минимум 3 символа.')
        return title

    def clean_budget(self):
        budget = self.cleaned_data.get('budget')
        if budget is not None and budget < 0:
            raise ValidationError('Бюджет не может быть отрицательным.')
        return budget

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_date')
        end = cleaned.get('end_date')
        if start and end and end < start:
            raise ValidationError('Дата окончания не может быть раньше даты начала.')
        return cleaned


class UploadFileForm(forms.Form):
    

    file = forms.FileField(
        label='Выберите JSON-файл',
        widget=forms.ClearableFileInput(
            attrs={'class': 'form-control', 'accept': '.json'}
        ),
    )

    def clean_file(self):
        f = self.cleaned_data['file']
        if not f.name.lower().endswith('.json'):
            raise ValidationError('Допускаются только файлы формата .json')
        if f.size > 5 * 1024 * 1024:
            raise ValidationError('Размер файла не должен превышать 5 МБ.')
        return f