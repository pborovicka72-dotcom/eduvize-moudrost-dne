"""Publish the selected approved corpus; no private profile or browser authority."""
import hashlib
import json
from importlib.resources import files
from typing import Annotated, Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr


class Settings(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    audience: Literal['all', 'primary', 'secondary']
    dailyCount: Annotated[StrictInt, Field(ge=1, le=3)]
    authorRepeat: Literal['avoid', 'allow']
    topics: Annotated[list[Annotated[StrictStr, Field(min_length=1, max_length=300)]], Field(max_length=1000)]
    authors: Annotated[list[Annotated[StrictStr, Field(min_length=1, max_length=300)]], Field(max_length=1000)]
    showSourceLink: StrictBool


def catalog():
    raw = files('eduvize_wisdom').joinpath('data/approved.json').read_bytes()
    rows = json.loads(raw)
    if not isinstance(rows, list) or not rows:
        raise ValueError('Approved Wisdom catalog unavailable')
    result = []
    for row in rows:
        if row.get('language') != 'cs':
            continue
        quote = {}
        for field in ('id', 'text', 'author', 'topic', 'work_title', 'source', 'source_url', 'rights'):
            value = row.get(field, '')
            if not isinstance(value, str) or len(value) > (12000 if field == 'text' else 2048):
                raise ValueError('Invalid approved Wisdom record')
            quote[field] = value
        if not all(quote[k].strip() for k in ('id', 'text', 'author')):
            raise ValueError('Incomplete approved Wisdom record')
        # Only a safe public citation can become an interactive link.
        url = urlsplit(quote['source_url'])
        if url.scheme != 'https' or not url.hostname or url.username or url.password:
            quote['source_url'] = ''
        quote['audience'] = row.get('audience', 'all')
        if quote['audience'] not in ('all', 'primary', 'secondary'):
            raise ValueError('Invalid approved audience')
        result.append(quote)
    if not result or len({q['id'] for q in result}) != len(result):
        raise ValueError('Empty or duplicate approved Wisdom catalog')
    return result, hashlib.sha256(raw).hexdigest()


def selected(settings, rows):
    return [q for q in rows if
            (not settings['topics'] or q['topic'] in settings['topics']) and
            (not settings['authors'] or q['author'] in settings['authors']) and
            (settings['audience'] == 'all' or q['audience'] == 'all' or q['audience'] == settings['audience'])]


def validate(payload, presentation):
    settings = Settings.model_validate(payload).model_dump()
    rows, _ = catalog()
    for field, singular in (('topics', 'topic'), ('authors', 'author')):
        values = settings[field]
        if len(values) != len(set(values)) or set(values) - {q[singular] for q in rows}:
            raise ValueError('Unknown or duplicate Wisdom selection')
    if not selected(settings, rows):
        raise ValueError('No approved quotes match the selected settings')
    return settings


def prepare(actor, payload, connection):
    # Pure packaged data only. Core owns ownership, licence and atomic publication.
    settings = validate(payload, None)
    rows, digest = catalog()
    quotes = selected(settings, rows)
    for quote in quotes:
        quote.pop('audience')
    return {'settings': settings, 'catalogSHA256': digest, 'quotes': quotes}, []


def get_output_adapters():
    from eduvize_admin.output_registry import Adapter
    return {'wisdom': Adapter(validate, '/eduvize-moudrost-dne/published.html', prepare=prepare)}
