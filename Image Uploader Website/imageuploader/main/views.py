from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import ImageForm
from .models import Image

# Create your views here.

def home(request):
    if request.method == "POST":
      print("POST data:", request.POST)

      if 'delete_id' in request.POST:
       image_id = request.POST.get('delete_id')
       print(f"delete image with ID: {image_id}")
       image = get_object_or_404(Image, id=image_id)
       image.delete()
       print(request,'Image deleted successfully')
       return redirect('/')     
    

      form = ImageForm(request.POST, request.FILES)
      if form.is_valid():
        form.save()
        print("image uploaded successfully")
        messages.success(request, 'Image uplaoded successfully')
        return redirect('/')
      else:
          print("Form error", form.errors)


    form = ImageForm()
    img = Image.objects.all().order_by('-date')
    return render(request, 'myapp/home.html', {'img': img, 'form': form})
