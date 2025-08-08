# Developers' Guide to Tiresias

I hope you find the concept as Tiresias as fun as I do.
If you have any ideas for ways to make the model better/cooler/dumber, feel free to jump in and start developing.

Here are some general guidelines I'd like to have in place for development:

1. Start with Issues

Before starting anything, please open an issue that describes the change you would like to make.
Then create a branch off of that issue (make sure your branch targets `develop`) and get to work.

2. Open PRs

I've added branch protections so that we can't push directly to `main` or `develop`.
When you're ready to merge your branch, open up a PR that targets `develop`.

Be sure to request me (@cwschilly) as a reviewer.

3. Maintain formatting

I'm still in the process of adding tests to the repo. For now, all we have is a simple linter to
make sure the code formatting is consistent. I've set this to be fairly strict; let's see how long
we can stick with it.

Generally, the linter looks for the following conventions:

- Max line length: 90 characters
- Name variables according to the following cases:
    - Class: `PascalCase`
    - Function: `camelCase`
    - Variable: `snake_case`
    - Constant: `UPPER_CASE`

Here are some other formatting guidelines I'd like to enforce:
- Add docstring to all new files/functions with a short description of what's included
- Favor well-named variables over extensive comments
- Prefer clear code over fancy code
