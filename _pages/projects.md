---
layout: default
title: Projects
permalink: /projects
description: Software projects, research code, and technical experiments.
---

<p class="projects-intro">
  This page collects software projects, research code, and technical experiments.
</p>

<div class="project-grid">
  {% for project in site.data.projects %}
  <article class="project-card">
    <div class="project-card__header">
      <p class="project-card__eyebrow">Project {{ forloop.index }}</p>
      <h2>{{ project.name }}</h2>
      <p class="project-card__summary">{{ project.summary }}</p>
    </div>

    {% if project.stack %}
    <section class="project-card__section" aria-label="Technology stack">
      <h3>Stack</h3>
      <ul class="project-chip-list">
        {% for item in project.stack %}
        <li>{{ item }}</li>
        {% endfor %}
      </ul>
    </section>
    {% endif %}

    {% if project.links %}
    <section class="project-card__section" aria-label="Project links">
      <h3>Links</h3>
      <div class="project-link-list">
        {% for link in project.links %}
        <a class="project-link" href="{{ link.url }}">{{ link.label }}</a>
        {% endfor %}
      </div>
    </section>
    {% endif %}

    {% if project.notes %}
    <section class="project-card__section">
      <h3>Notes</h3>
      <p>{{ project.notes }}</p>
    </section>
    {% endif %}
  </article>
  {% endfor %}
</div>
