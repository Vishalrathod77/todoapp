from django.shortcuts import render, HttpResponse, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q
import json
from django.views.decorators.csrf import csrf_exempt

from home.models import Tasks

# Create your views here.
def home(request):
    context = {'success': False}
    if request.method == 'POST':
        title = request.POST['title']
        desc = request.POST['desc']
        
        ins = Tasks(taskTitle=title, taskDesc=desc)
        ins.save()
        context = {'success': True}

    return render(request, 'index.html', context)

def tasks(request):
    search_query = request.GET.get('search', '')
    if search_query:
        # Search in both title and description, order by newest first
        allTasks = Tasks.objects.filter(
            Q(taskTitle__icontains=search_query) | 
            Q(taskDesc__icontains=search_query)
        ).order_by('-time')
    else:
        # If no search query, get all tasks ordered by newest first
        allTasks = Tasks.objects.all().order_by('-time')
    
    context = {
        'tasks': allTasks,
        'search_query': search_query
    }
    return render(request, 'tasks.html', context)

def delete(request, title):
    if request.method == "POST":
        try:
            task = get_object_or_404(Tasks, taskTitle=title)
            task.delete()
            messages.success(request, 'Task deleted successfully!')
            return JsonResponse({'message': 'Task deleted successfully!'}, status=200)
        except Exception as e:
            messages.error(request, f'Error deleting task: {str(e)}')
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def update(request, id):
    if request.method == "POST":
        try:
            task = get_object_or_404(Tasks, id=id)
            data = json.loads(request.body)
            
            task.taskTitle = data['title']
            task.taskDesc = data['desc']
            task.save()
            
            messages.success(request, 'Task updated successfully!')
            return JsonResponse({'message': 'Task updated successfully!'}, status=200)
        except Exception as e:
            messages.error(request, f'Error updating task: {str(e)}')
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)
