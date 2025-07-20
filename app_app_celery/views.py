from django.shortcuts import render
from django.http import JsonResponse
from .tasks import add_resize_task
from .forms import ImageUploadForm
import os
from django.conf import settings
from .models import UploadedImage
from PIL import Image

def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image1 = request.FILES.get('image1')
            image2 = request.FILES.get('image2')
            if image1 and image2:
                if image1.name == image2.name:
                    # Merge images side by side
                    img1 = Image.open(image1)
                    img2 = Image.open(image2)
                    # Ensure both images are in the same mode
                    if img1.mode != img2.mode:
                        img2 = img2.convert(img1.mode)
                    # Ensure both images are the same height
                    if img1.height != img2.height:
                        # Resize img2 to img1's height
                        img2 = img2.resize((int(img2.width * img1.height / img2.height), img1.height))
                    total_width = img1.width + img2.width
                    max_height = max(img1.height, img2.height)
                    merged_img = Image.new(img1.mode, (total_width, max_height))
                    merged_img.paste(img1, (0, 0))
                    merged_img.paste(img2, (img1.width, 0))
                    merged_name = f"merged_{image1.name}"
                    merged_path = os.path.join(settings.MEDIA_ROOT, 'uploaded_images/', merged_name)
                    os.makedirs(os.path.dirname(merged_path), exist_ok=True)
                    merged_img.save(merged_path)
                    add_resize_task(merged_path)
                    UploadedImage.objects.create(image=merged_name)
                    return JsonResponse({'status': f'Merged image created and resizing task added for: {merged_name}'})
                else:
                    return JsonResponse({'status': 'images are not same'})
            # Fallback to original logic if not both images are uploaded
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
