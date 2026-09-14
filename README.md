# MATH& 107 — Math in Society — Fall 2026 Web Course

Static, browser-based course site modeled on the Precalculus course shell.

Current revision: **v0.12 — print-friendly lab submissions**

All ten weeks now have full exercise-based lab/application passes.

- Week 1: number systems and recursion
- Week 2: counts, samples, probability, and distributions
- Week 3: center, spread, consistency, and outliers
- Week 4: normal distributions, z-scores, sampling, and confidence intervals
- Week 5: decimal/binary representation, approximation, compression, parity, and information
- Week 6: simple and compound interest, Rule of 72, and loan repayment
- Week 7: cost, revenue, profit, break-even, marginal analysis, and graph reading
- Week 8: convex sets, half-planes, feasible regions, vertices, and the corner-point principle
- Week 9: linear-program setup, maximization, minimization, objective sensitivity, and multiple optima
- Week 10: stable/sensitive recursion, Collatz, fractals, logistic dynamics, and scale-dependent measurement

Student-facing interactive work saves locally in the browser where appropriate. The final two weeks use the same computation-first design as Weeks 1–8, with open-ended writing minimized in favor of numerical entries, selections, and interactive experiments.

## Instructional design

The course pages are written to be self-contained for students. Each lab and application introduces the meaning and units of the quantities before asking for a calculation, gives the small set of formulas or notation needed on that page, and uses specific interpretation questions rather than broad reflection prompts. Interactive demos include a short use guide so students know what to vary and what mathematical relationship to watch. The printable summaries, prequizzes, and matching quizzes use the same notation, contexts, and computational emphasis as the online labs and mastery quizzes.

## Module printables

The Modules view links a separate PDF packet for each module. Each packet contains the summary, prequiz, and matching quiz. Matching instructor keys are stored in `materials/instructor_keys/`. The included GitHub Action recompiles all module PDFs when their LaTeX sources change.
## Printing completed HTML labs

All ten HTML labs can now be submitted directly on paper without first creating a PDF. At the bottom of each lab, students can enter their name and choose **Print Completed Lab**. Before the browser print dialog opens, the page converts typed inputs and selected dropdown choices into static print-only answer text, so completed responses do not depend on how a particular browser renders form controls. Students may select a physical printer or choose **Save as PDF** from the same print dialog. The student name is remembered locally on that browser for the next lab.

