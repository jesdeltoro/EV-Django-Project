from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from .forms import PageForm
from .models import Page
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator


from django.views import View

class StaffRequiredMixin(View):
    """
    Este mixin requerirá que el usuario sea miembro del staff
    """
    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        # Usar la forma moderna de super() sin argumentos
        return super().dispatch(request, *args, **kwargs)
    

class PageListView(ListView):
    model = Page


class PageDetailView(DetailView):
    model = Page
    pk_url_kwarg = 'page_id'
    slug_url_kwarg = 'page_slug'
    
@method_decorator(staff_member_required, name='dispatch')
class PageCreate(CreateView):
    model = Page
    form_class = PageForm
    success_url = reverse_lazy('pages:pages')

@method_decorator(staff_member_required, name='dispatch')    
class PageUpdate(UpdateView):
    model = Page
    form_class = PageForm
    template_name = 'pages/page_update_form.html'
    def get_success_url(self):
        obj = self.get_object()
        return reverse_lazy('pages:update', args=[obj.pk]) + '?ok'

@method_decorator(staff_member_required, name='dispatch')    
class PageDelete(DeleteView):
    model = Page
    success_url = reverse_lazy('pages:pages')



