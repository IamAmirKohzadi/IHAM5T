{% extends "mail_templated/base.tpl" %}

{% block subject %}
Acc Activation
{% endblock %}

{% block html %}
This is your token:
{{token}}

{% endblock %}