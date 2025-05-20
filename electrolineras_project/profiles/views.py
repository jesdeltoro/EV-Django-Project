from django.shortcuts import get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from registration.models import Profile
from django.contrib.auth.mixins import LoginRequiredMixin


# Create your views here.
class ProfileListView(ListView):
    model = Profile
    template_name = 'profiles/profile_list.html'
    paginate_by= 10

class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'profiles/profile_detail.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Profile, user__username=self.kwargs['username'])
