# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core import conf as silvaconf
from Products.SilvaDocument import install

silvaconf.extension_name('SilvaDocument')
silvaconf.extension_title('Silva Obsolete Document')
silvaconf.extension_depends(["Silva", "SilvaExternalSources"])


# add some scheme to urlparse
import urlparse


SCHEME_HTTP_LIKE_CAPABILITIES = [
    'uses_relative',
    'uses_netloc',
    'uses_params',
    'uses_query',
    'uses_fragment',
]

EXTRA_SCHEMES = [
    ('itms',   SCHEME_HTTP_LIKE_CAPABILITIES),
    ('webcal', SCHEME_HTTP_LIKE_CAPABILITIES),
    ('tel', SCHEME_HTTP_LIKE_CAPABILITIES),
]

def add_scheme(scheme, capabilities):
    for capability in capabilities:
        schemes = getattr(urlparse, capability)
        if not scheme in schemes:
            schemes.append(scheme)

def update_url_parse_schemes():
    for (scheme, caps) in EXTRA_SCHEMES:
        add_scheme(scheme, caps)

update_url_parse_schemes()



