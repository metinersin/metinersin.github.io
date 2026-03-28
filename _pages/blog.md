---
layout: default
title: Blog
permalink: /blog
description: Short posts, textbook solutions, and mathematics writing.
---

This page collects shorter writing, notes, and textbook solutions.

<div class="post-list">
  {% for post in site.posts %}
  <article class="post-list__item">
    <p class="post-list__meta">{{ post.date | date: "%b %-d, %Y" }}</p>
    <h2><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h2>
    {% if post.categories and post.categories.size > 0 %}
    <p class="post-list__tags">{{ post.categories | join: ", " }}</p>
    {% endif %}
  </article>
  {% endfor %}
</div>
