# Books Like This
Finds books based on similar story features.
Story features are tropes pulled from
[tvtropes.org](https://tvtropes.org), a community-driven wiki
devoted to the analysis of fictional media.

See it in action:
[bookslikethis.herokuapp.com](https://bookslikethis.herokuapp.com)

## How it works
This can be thought of as a specialized search engine, where books
are both the search terms and the results, and results are ranked
by similarity, using tropes as features. This also shares some
techniques with content-based recommendation systems.

Similarity scoring uses several layers to get good results. For instance:
* Jaccard similarity (set-based) is used to avoid penalizing
books with different numbers of tagged tropes (which is often
due to missing data/popularity differences).
* Tropes are weighted because they are not equally meaningful
for recommending a book. For instance, plot tropes, such as
Alien Invasion, receive more weight.
* Tropes are further weighted by distinctiveness (using dunning
log likelihood). This compares the queried books with the rest
of the catalog, to find which tropes make them special.
* Results are also weighted by genre. Staying within genre
gives subjectively better results.

## Stack
Built with Python, Django, Postgres, React, and Webpack. Running on Heroku.

## Installation
Prerequisites:
```
python 3
make
postgres
node/npm
```

To install:
```
make
```

To run tests:
```
make test
```

To populate the database, activate the virtualenv in .venv, then:
```
cd bookslikethis
python manage.py migrate
python manage.py load_data <files>
```

This expects JSON Lines data which is not provided.
See [load_data_test.py](bookslikethis/core/management/commands/load_data_test.py)
for example format.

## License

This project is licensed under the MIT License - see the
[LICENSE.txt](LICENSE.txt) file for details.

Note that if you use this with any tvtropes.org data (not included), that
would be subject to the [CC BY-NC-SA 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/) license.
