{% extends "base.html" %}{% block content %}
<div class="card"><h3>Downloaded Documents</h3><table><tr><th>Status</th><th>Size</th><th>Content Type</th><th>Final URL</th><th>Message</th><th>Downloaded</th></tr>{% for d in docs %}<tr><td>{{d.status}}</td><td>{{d.file_size}}</td><td>{{d.content_type}}</td><td><a href="{{d.final_url}}" target="_blank">{{d.final_url}}</a></td><td>{{d.message}}</td><td>{{d.downloaded_at}}</td></tr>{% endfor %}</table></div>
{% endblock %}
