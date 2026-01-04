from django.shortcuts import redirect


# Redirect authenticated users away from auth-only pages.
class RedirectAuthenticatedMixin:
    redirect_url_name = "website:index"

    def dispatch(self, request, *args, **kwargs):
        # Redirect logged-in users before running the view.
        if request.user.is_authenticated:
            return redirect(self.redirect_url_name)
        return super().dispatch(request, *args, **kwargs)


# API-friendly alias for the same redirect behavior.
class RedirectAuthenticatedApiMixin(RedirectAuthenticatedMixin):
    pass
