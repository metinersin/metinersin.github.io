---
layout: post
title:  "David Marker, Model Theory: An Introduction, Exercise 2.5.10"
date:   2024-06-24 18:50 +0300
categories: mathematics model-theory textbook-solutions
---

**Exercise 2.5.10** Let $$T$$ be an $$\cal{L}$$-theory and $$T_\forall$$ be all of the universal sentences $$\phi$$ such that $$T \vDash \phi$$. Show that $$\cal{A}$$ $$\vDash T_\forall$$ if and only if there is $$\cal{M}$$ $$\vDash T$$ with $$\cal{A} \subseteq \cal{M}$$.

**Proof:** ($$\Rightarrow$$) Consider the theory $$T' := T \cup \diag \cal{A}$$. Any model of $$T'$$ is an extension of $$\cal{A}$$ which is also a model of $$T$$. For a contradiction, assume that $$T'$$ is unsatisfiable. By compactness, there exists a quantifier free $$\cal{L}$$-formula $$\phi(\bar{a})$$ with $$\bar{a} \in A$$ such that $$T \cup \{\phi(\bar{a})\} \vDash \bot$$ implying $$T \vDash \forall \bar{x} \ \neg \phi(\bar{x})$$. Therefore, $$\forall \bar{x} \ \neg \phi(\bar{x}) \in T_\forall$$ and hence $$\cal{A} \vDash \forall \bar{x} \ \neg \phi(\bar{x})$$. In particular, $$\cal{A} \vDash \neg \phi(\bar{a})$$ which is a contradiction.
