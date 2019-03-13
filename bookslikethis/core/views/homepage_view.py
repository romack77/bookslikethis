"""Homepage view."""
from django import views
from django import shortcuts


class HomepageView(views.View):

    def get(self, request):
        return shortcuts.render(request, 'index.html')
