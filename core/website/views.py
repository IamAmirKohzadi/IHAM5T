from django.views.generic import TemplateView

# Renders the website home page.
class HomeView(TemplateView):
    template_name = "website/index.html"

# Renders the about page.
class AboutView(TemplateView):
    template_name = "website/about.html"

# Renders the contact page.
class ContactView(TemplateView):
    template_name = "website/contact.html"

# Renders the blog newsletter landing page.
class NewsletterView(TemplateView):
    template_name = "blogApi/blog-newsletter.html"

# Renders the blog home page shell.
class BlogHome(TemplateView):
    template_name = "blogApi/blog-home.html"

# Renders the blog single-post page shell.
class BlogSingle(TemplateView):
    template_name = "blogApi/blog-single.html"

