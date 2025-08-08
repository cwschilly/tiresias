![GitHub](https://img.shields.io/github/license/hpc-simtools/ips-framework)

# Tiresias: The Blind Seer

Will Christopher Nolan's _The Odyssey_ (2026) make money? Will it win any awards? And most importantly of all, _will **you** like it??_

Tiresias ([who?](https://en.wikipedia.org/wiki/Tiresias)) is here to peer into the future.

<!-- Read all about it [here](calebschilly.substack.com). -->

## Usage

For now, clone the repo and install the `tiresias` package into your favorite Python environment:

```sh
git clone https://github.com/cwschilly/tiresias.git
cd tiresias
pip install .
```

Then just run:

```sh
python main.py
```

I'm hoping to move all this into a web app soon, which will remove the installation step and make the runtime even simpler.
In the meantime, this is what we've got.

## Contributing

`tiresias` is, of course, open-source. Feel free to [open issues](https://github.com/cwschilly/tiresias/issues/new), put up PRs with cool features, and generally ~~steal~~ use my IP. There's a short developer's guide in the
`doc/` folder if you're interested in contributing.

And if you do use the code, I would appreciate a citation.

---

### Sources

Training data was obtained from the following sources:

- [Letterboxd](letterboxd.com) _(Average and personalized ratings)_
- [Collider](https://collider.com/christopher-nolan-movies-oscar-nominations-ranked/) _(Oscar Noms/Wins)_
- [Collider](https://collider.com/christopher-nolan-movie-budgets-ranked/) _(Budgets)_
- [Cineworld](https://www.cineworld.co.uk/static/en/uk/blog/christopher-nolan-six-memorable-imax-movie-scenes) _(IMAX Releases)_
- [MovieWeb](https://movieweb.com/christopher-nolan-movies-ranked-by-box-office-performance/) _(Box Office)_
- [Box Office Mojo](https://www.boxofficemojo.com/year/) _(Annual Box Office)_
