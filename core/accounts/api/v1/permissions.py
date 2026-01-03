from django.shortcuts import redirect


class RedirectAuthenticatedMixin:
    redirect_url_name = "website:index"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.redirect_url_name)
        return super().dispatch(request, *args, **kwargs)


class RedirectAuthenticatedApiMixin(RedirectAuthenticatedMixin):
    pass
