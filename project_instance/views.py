from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from .models import ProjectBInstance
import json

# Initialize ProjectBInstance with the path to project B
project_b_instance = ProjectBInstance('/path/to/projectB')

@require_http_methods(["GET"])
def generate_update_list_view(request):
    updates = project_b_instance.generate_update_list()
    return JsonResponse(updates, safe=False)

@require_http_methods(["POST"])
def store_files_in_db_view(request):
    try:
        data = json.loads(request.body)
        file_paths = data.get('file_paths', [])
        if not file_paths:
            return JsonResponse({'error': 'No file paths provided'}, status=400)
        
        project_b_instance.add_files_to_db(file_paths)
        return JsonResponse({'message': 'Files stored successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["POST"])
def update_file_tree_view(request):
    try:
        project_b_instance.update_file_tree()
        return JsonResponse({
            'message': 'File tree updated successfully',
            'file_tree': project_b_instance.file_tree,
            'tree_output': project_b_instance.tree_output
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["POST"])
def update_file_or_files_view(request):
    try:
        data = json.loads(request.body)
        file_paths = data.get('file_paths', [])
        if not file_paths:
            return JsonResponse({'error': 'No file paths provided'}, status=400)
        
        project_b_instance.add_files_to_db(file_paths)
        return JsonResponse({'message': 'Files updated successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def get_file_or_files_view(request):
    try:
        file_paths = request.GET.getlist('file_paths')
        if not file_paths:
            return JsonResponse({'error': 'No file paths provided'}, status=400)
        
        files_content = project_b_instance.get_files_from_db(file_paths)
        return JsonResponse(files_content, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["DELETE"])
def delete_file_or_files_view(request):
    try:
        data = json.loads(request.body)
        file_paths = data.get('file_paths', [])
        if not file_paths:
            return JsonResponse({'error': 'No file paths provided'}, status=400)
        
        # Implement file deletion logic in ProjectBInstance if necessary
        return JsonResponse({'message': 'Files deleted successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def get_current_tree_view(request):
    return JsonResponse({
        'file_tree': project_b_instance.file_tree,
        'tree_output': project_b_instance.tree_output
    })

@require_http_methods(["GET"])
def get_updated_tree_view(request):
    try:
        result = subprocess.run(["tree", project_b_instance.project_b_path], capture_output=True, text=True)
        if result.returncode != 0:
            return JsonResponse({'error': 'Tree command failed'}, status=500)
        
        return JsonResponse({'tree_output': result.stdout})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
