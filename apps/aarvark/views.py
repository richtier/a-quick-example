# C6002 (reverse-lazy-misuse)
# C9000 (queryset-length)
from django.urls import reverse_lazy

from django.views.generic import View

from .models import Group


class LocalListView(View):
    template_name = 'local/local_list.html'
    model = LocalEstoque
    context_object_name = 'all_locais'
    success_url = reverse_lazy('listalocalview')
    permission_codename = 'view_localestoque'

    def view_context(self, context):
        context['title_complete'] = 'LOCAIS DE ESTOQUE'
        context['add_url'] = reverse_lazy('addlocalview')
        return context


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = Group.objects.filter(oferta_trimestral=oferta,)

        if len(items) == 0:
            context['problem'] = 'There is a problem. Please contact support.'

        return context
