---
layout: post
title:  "David Marker, Model Theory: An Introduction, Exercise 2.5.2"
date:   2024-06-24 18:00 +0300
categories: mathematics model-theory textbook-solutions
---

**Exercise 2.5.2** Suppose that $$T$$ has arbitrarily large finite models. Show that $$T$$ has an infinite model.

**Proof:** Let $$\phi_n$$ be the sentence asserting that "there exists at least $$n$$ elements" which is expressible in first-order logic. Consider the theory $$ T' = T \cup \{\phi_n : n \in \mathbb{N}\} $$. Because $$T$$ has arbitrarily large models, the theory $$T \cup \{\phi_n : n \leq N\}$$ is satisfiable for any $$N$$. Therefore, by compactness, $$T'$$ is also satisfiable. Clearly, any model of $$T'$$ is an infinite model of $$T$$.

<!-- uu $$ \text{Let $\phi_n$ be the sentence asserting that "there exists at least $n$ elements" which is expressible in first-order logic. Consider the theory $T' = T \cup \{\phi_n : n \in \mathbb{N}\}$. Because $T$ has arbitraryly large models, the theory $T \cup \{\phi_n : n \leq N\}$ is satisfiable for any $N$. Therefore, by compactness, $T'$ is also satisfiable. Clearly, any model of $T'$ is an infinite model of $T$.} $$ -->
