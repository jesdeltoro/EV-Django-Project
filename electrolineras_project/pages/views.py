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


class StaffRequiredMixin(object):
    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
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
    
    def form_valid(self, form):
        """Process the form if it's valid."""
        try:
            # Save the form data to create the page
            response = super().form_valid(form)
            # Add a success message
            messages.success(self.request, "La página se ha creado correctamente.")
            return response
        except Exception as e:
            # Log the exception
            print(f"Error saving page: {e}")
            # Add an error message
            messages.error(self.request, f"Error al crear la página: {e}")
            return redirect('pages:pages')
    
    def form_invalid(self, form):
        """Process the form if it's invalid."""
        # Log form errors to console for debugging
        print(f"Form validation errors: {form.errors}")
        # Add an error message 
        messages.error(self.request, "Revisa los errores en el formulario.")
        return super().form_invalid(form)
    
@method_decorator(staff_member_required, name='dispatch')    
class PageUpdate(UpdateView):
    model = Page
    form_class = PageForm
    template_name = 'pages/page_update_form.html'
    def get_success_url(self):
        return reverse_lazy('pages:update', args=[self.object.id]) + '?ok'

@method_decorator(staff_member_required, name='dispatch')    
class PageDelete(DeleteView):
    model = Page
    success_url = reverse_lazy('pages:pages')



