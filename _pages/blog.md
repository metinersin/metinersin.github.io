---
layout: default
title: Blog
permalink: /blog
---

## My Blog Posts

<ul>
  {% for post in site.posts %}
  <li><a href="{{ post.url }}" class="post-preview">{{ post.title }}</a></li>
  {% endfor %}
</ul>
