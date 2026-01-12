{% extends "mail_templated/base.tpl" %}

{% block subject %}
Acc Activation
{% endblock %}

{% block html %}
by pressing on this
<a href="{{ site_url }}/accounts/api/v1/activation/confirm/{{ token }}">
  link
</a>
you can activate your email!
{% endblock %}
