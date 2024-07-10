---
layout: post
title:  "David Marker, Model Theory: An Introduction, Exercise 2.5.15"
date:   2024-06-25 15:38 +0300
categories: mathematics model-theory textbook-solutions
---

**Exercise 2.5.15** We say that $$T$$ has a ∀∃-axiomatization if it can be axiomatized by sentences of the form ∀v1 . . . ∀vn∃w1 . . . ∃wm φ(v,w) where φ is a quantifier-free formula.

**Proof:** (i $$\Rightarrow$$ ii) Let $$\psi(v)$$ be a universal formula such that $$T \vDash \forall v ( \phi(v) \leftrightarrow \psi(v) )$$. Let $$\cal{M}$$ and $$\cal{N}$$ be models of $$T$$ with $$\cal{M} \subseteq \cal{N}$$, $$a \in M$$, and $$\cal{N} \vDash \phi(a)$$. We have:

$$
\begin{align*}
\cal{N} \vDash \phi(a) \\
\cal{N} \vDash \psi(a) \\
\cal{M} \vDash \psi(a) \\
\cal{M} \vDash \phi(a)
\end{align*}
$$

(ii $$\Rightarrow$$ i) Consider the following collection: 

$$
\Gamma := \{\psi(v) : \psi(v) \text{ is a universal formula} \text{ and } T \cup \{\phi(v)\} \vDash \psi(v) \}
$$

By compactness and by the fact that $$\Gamma$$ is closed under conjunctions, $$T \cup \Gamma \vDash \phi(v)$$ implies that $$T \cup {\psi(v)} \vDash \phi(v)$$, and hence, $$T \vDash \forall v (\phi(v) \leftrightarrow \psi(v))$$ for some $$\psi(v) \in \Gamma$$. To that end, let $$\cal{M} \vDash T \cup \Gamma$$. We will show that $$\cal{M} \vDash \phi(v)$$. Consider the theory $$T' := T \cup \diag \cal{M} \cup \{\phi(v)\}$$. For a contradiction, assume $$T' \vDash \bot$$. By compactness, there exists $$a \in M$$, $$\chi(a, v) \in \diag \cal{M}$$ such that $$T \cup \{\phi(v), \chi(a, v)\} \vDash \bot$$. This means $$T \cup \{\phi(v)\} \vDash \forall x \, \neg \chi(x, v)$$ showing $$\forall x \, \neg \chi(x, v) \in \Gamma$$. Thus, $$\cal{M} \vDash \forall x \, \neg \chi(x, v)$$ but $$\cal{M} \vDash \chi(a, v)$$, a contradiction. Therefore, $$T'$$ is satisfiable. Let $$\cal{N} \vDash T'$$. Then, by ii, $$\cal{M} \vDash \phi(v)$$.  
