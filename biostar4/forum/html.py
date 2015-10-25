import bleach, re, logging, requests
from markdown2 import markdown
from html5lib.tokenizer import HTMLTokenizer

logger = logging.getLogger('biostar')

TAGS = "li ul ol a p div br code pre h1 h2 h3 h4 hr span s sub sup b i img strong \
    strike em underline super table thead tr th td tbody".split()

STYLES = 'color font-weight background-color width height'.split()

ATTRS = {
    'a': ['href', 'rel'],
    'img': ['src', 'alt', 'width', 'height'],
}

def strip_tags(text):
    """
    Strip html tags from text
    """
    result = bleach.clean(text, tags=[], attributes=[], styles={}, strip=True)
    return result


def require_protocol(attrs, new=False):
    """
    Used as a markdown2 callback.
    Linkify only if protocols are present.
    """
    if new:
        href, _text = attrs['href'], attrs['_text']
        if href != _text:
            # This has already been linkified.
            return attrs
        # Don't linkify links with no protocols.
        if href[:4] not in ('http', 'ftp:'):
            return None
    return attrs


def sanitize(text, user=None, trusted=False):
    """
    Sanitize text and expand links to match content
    """
    if not text.strip():
        # No content there.
        return ""

    try:
        # Apply the markdown transformation.
        # We'll protect against library crashes by a generic Exception catch.
        html = markdown(text, extras=["fenced-code-blocks", "code-friendly", "nofollow", "spoiler"])
    except Exception as exc:
        logger.error('crash during markdown conversion: %s' % exc)
        html = text

    if not trusted:
        html = bleach.clean(html, tags=TAGS, attributes=ATTRS, styles=STYLES)

    return html
