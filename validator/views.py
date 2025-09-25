from django.shortcuts import render
from .forms import PESELForm
from .services.pesel import validate_pesel

def index(request):
    if request.method == 'POST':
        form = PESELForm(request.POST)
        if form.is_valid():
            result = validate_pesel(form.cleaned_data['pesel'])
            context = {'form': form, 'result': result}
            return render(request, 'validator/index.html', context)
    else:
        form = PESELForm()
    return render(request, 'validator/index.html', {'form': form})
