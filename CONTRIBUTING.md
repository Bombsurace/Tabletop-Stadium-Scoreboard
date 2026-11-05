# Contributing

Thanks for helping. All of these are useful:

- **Build photos and "it worked with part X" reports.** These are especially welcome for parts marked *untested* in
  the [parts list](docs/parts.md). Use the *Build report* issue form.
- **Bug reports.** Use the *Bug report* form and include the [logs](docs/troubleshooting.md#collecting-logs).
- **Ideas.** Use the *Feature request* form. Check the [roadmap](README.md#roadmap) first.
- **Pull requests** for code, docs or models.

## Pull requests

1. Fork, then branch from `main`.
2. Keep each pull request to one change. Describe what it does and how you tested it.
3. **Code:** run `python server.py --demo` and check the board at 1024 × 600 and 1280 × 400. Keep `espn.py` the only
   file that knows ESPN's data format.
4. **Models:** change sizes in `frame/field_frame.py` (named numbers at the top), run `python field_frame.py --check`,
   and include a photo of a test print if the change affects fit.
5. **Docs:** plain, short sentences. Mark anything you haven't built yourself as *untested*.

By contributing you agree your code is licensed MIT and your model changes CC BY-NC-SA 4.0, matching the project.

## Be kind

Be welcoming and patient. Many people building this are new to Linux, soldering or 3D printing.
