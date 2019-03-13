from django.contrib.postgres import indexes


class GistIndexTrigrams(indexes.GistIndex):
    """A GIST index with trigram similarity support.

    This is useful for text search scenarios.

    This requires Postgres as well as the Postgres pgtrgm extension.
    See: https://www.postgresql.org/docs/9.1/pgtrgm.html
    """

    def create_sql(self, model, schema_editor, using=''):
        statement = super().create_sql(model, schema_editor, using=using)
        statement.template = (
            'CREATE INDEX %(name)s ON %(table)s%(using)s '
            '(%(columns)s gist_trgm_ops)%(extra)s')
        return statement
