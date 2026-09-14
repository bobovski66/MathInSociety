# Uploading this course to GitHub

This folder is ready to replace the contents of the MathInSociety repository.

- `index.html` is the main course page.
- `labs/`, `applications/`, and `demos/` contain the revised instructional pages.
- `readings/` contains the ten textbook chapter PDFs.
- `materials/modules/` contains ten separate student printable packets. Each PDF contains that module's summary, prequiz, and matching quiz.
- `materials/instructor_keys/` contains the matching instructor answer keys.
- `.github/workflows/build-printables.yml` recompiles all module PDFs when their LaTeX sources change.

The Modules view in `index.html` links directly to the appropriate PDF in `materials/modules/` for each module.

If replacing an older repository checkout, remove obsolete monolithic printable files such as `materials/math107_student_printables.*` and `materials/math107_answer_keys.*` so there is only one authoritative version of each handout.

## Student lab submission

Each file in `labs/` includes a **Print Completed Lab** section. Students can complete the lab in the browser, enter their name, and print directly to a physical printer. The print stylesheet replaces form controls with readable static answer text. The same button can also be used to save a PDF if desired.
