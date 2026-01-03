{% extends "mail_templated/base.tpl" %}

{% block subject %}
Password reset
{% endblock %}

{% block html %}
<p>We received a request to reset your password.</p>
<p>
  Click this link to choose a new password:
  <a href="{{ protocol }}://{{ domain }}/accounts/reset/{{ uid }}/{{ token }}/">Reset password</a>
</p>
<p>If you did not request this, you can ignore this email.</p>
{% endblock %}
