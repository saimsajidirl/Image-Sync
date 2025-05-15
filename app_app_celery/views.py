from django.shortcuts import render
from django.http import JsonResponse
from .tasks import add_resize_task
from .forms import ImageUploadForm
import os
from django.conf import settings
from .models import UploadedImage
def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            images_uploaded = []
            for i in range(1, 3):
                image_file = request.FILES.get(f'image{i}')
                if image_file:
                    if UploadedImage.objects.filter(image=image_file.name).exists():
                        continue
                    image_path = os.path.join(settings.MEDIA_ROOT, 'uploaded_images/', image_file.name)
                    os.makedirs(os.path.dirname(image_path), exist_ok=True)
                    with open(image_path, 'wb+') as destination:
                        for chunk in image_file.chunks():
                            destination.write(chunk)
                    add_resize_task(image_path)
                    UploadedImage.objects.create(image=image_file)
                    images_uploaded.append(image_file.name)
            if images_uploaded:
                return JsonResponse({'status': f'Images uploaded and resizing tasks added for: {", ".join(images_uploaded)}'})
            else:
                return JsonResponse({'status': 'No new images uploaded (duplicates found).'})
    else:
        form = ImageUploadForm()

    current_images = UploadedImage.objects.all()
    return render(request, 'upload.html', {'form': form, 'current_images': current_images})
