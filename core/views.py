from django.shortcuts import render
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
    FormView,
)
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
    PermissionRequiredMixin,
)



class HomeView(TemplateView):
    template_name = "core/index.html"

class NiveisView(TemplateView):
    template_name = "core/niveis.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # gera lista de 1 a 10
        context["niveis"] = range(1, 11)
        return context

class GamePageView(TemplateView):
    template_name = "core/game.html"

class CadastrarQuestoesView(TemplateView):
    template_name = "core/cadastrar_questoes.html"



    