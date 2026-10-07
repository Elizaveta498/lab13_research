from pathlib import Path

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect

from .forms import ResearchForm, UploadFileForm
from .models import Research
from . import utils


def index(request):
    
    records = Research.objects.all()
    files = utils.list_data_files()
    return render(request, 'research/index.html', {
        'records': records,
        'files': files,
    })


def add_research(request):
    
    if request.method == 'POST':
        form = ResearchForm(request.POST)
        if form.is_valid():
            obj = form.save()
            try:
                path = utils.save_records_to_file([obj.to_dict()])
                messages.success(request, f'Исследование сохранено. Файл: {path.name}')
            except Exception as e:
                messages.error(request, f'Ошибка сохранения файла: {e}')
            return redirect('research:index')
        else:
            messages.error(request, 'Исправьте ошибки в форме.')
    else:
        form = ResearchForm()
    return render(request, 'research/add.html', {'form': form})


def upload_file(request):
    
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded = form.cleaned_data['file']
            safe_name = utils.sanitize_filename(uploaded.name)
            target = utils.get_data_dir() / safe_name

            with open(target, 'wb+') as dest:
                for chunk in uploaded.chunks():
                    dest.write(chunk)

            try:
                records = utils.load_and_validate_json(target)
            except ValidationError as e:
                utils.delete_file(target)
                messages.error(request, f'Файл не валиден и удалён: {e}')
                return redirect('research:upload')

            imported = 0
            for r in records:
                try:
                    Research.objects.create(
                        title=r['title'],
                        author=r['author'],
                        field=r['field'],
                        description=r['description'],
                        start_date=r['start_date'],
                        end_date=r.get('end_date') or None,
                        status=r['status'],
                        budget=r.get('budget') or 0,
                    )
                    imported += 1
                except Exception:
                    continue

            messages.success(
                request,
                f'Файл "{safe_name}" загружен. Импортировано записей: {imported}.'
            )
            return redirect('research:index')
        else:
            messages.error(request, 'Ошибка в форме загрузки.')
    else:
        form = UploadFileForm()
    return render(request, 'research/upload.html', {'form': form})


def files_list(request):
    
    files = utils.list_data_files()
    return render(request, 'research/files.html', {'files': files})


def file_detail(request, filename: str):
    
    safe_name = Path(filename).name
    try:
        data = utils.read_data_file(safe_name)
    except ValidationError as e:
        messages.error(request, str(e))
        return redirect('research:files')

    records = data.get('records', []) if isinstance(data, dict) else data
    return render(request, 'research/file_detail.html', {
        'filename': safe_name,
        'records': records,
        'raw': data,
    })


def export_all(request):
    
    records = [r.to_dict() for r in Research.objects.all()]
    if not records:
        messages.warning(request, 'Нет данных для экспорта.')
        return redirect('research:index')

    path = utils.save_records_to_file(records)
    messages.success(request, f'Экспортировано в файл: {path.name}')
    return redirect('research:index')


def file_download(request, filename: str):
    
    safe_name = Path(filename).name
    path = utils.get_data_dir() / safe_name
    if not path.exists():
        raise Http404('Файл не найден')
    with open(path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{safe_name}"'
        return response


def file_delete(request, filename: str):
    
    if request.method != 'POST':
        return redirect('research:files')

    safe_name = Path(filename).name
    utils.delete_file(utils.get_data_dir() / safe_name)
    messages.success(request, f'Файл "{safe_name}" удалён.')
    return redirect('research:files')


