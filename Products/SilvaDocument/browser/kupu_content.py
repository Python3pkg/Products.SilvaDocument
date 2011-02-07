# Copyright (c) 2010-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from datetime import datetime

from Products.SilvaDocument.interfaces import IDocument

from five import grok
from zope.component import getUtility
from zope.intid.interfaces import IIntIds

from silva.core.views.interfaces import IVirtualSite
from silva.core.smi.interfaces import ISMILayer



class KupuContent(grok.View):
    """Return content to edit in Kupu with the correct CSS.
    """
    grok.context(IDocument)
    grok.name(u'kupu_content')
    grok.layer(ISMILayer)
    grok.require('silva.ChangeSilvaContent')

    @property
    def headers(self):
        # This is a property in order to have a recent last-modified date
        return [('Expires', 'Mon, 26 Jul 1997 05:00:00 GMT'),
                ('Last-Modified', datetime.now().strftime(
                    "%a, %d %b %Y %H:%M:%S GMT")),
                ('Cache-Control', 'no-cache, must-revalidate'),
                ('Cache-Control', 'post-check=0, pre-check=0'),
                ('Pragma', 'no-cache'),
                ('Content-Type', 'text/html;charset=utf-8'),]

    def update(self):
        for key, value in self.headers:
            self.response.setHeader(key, value)

        version = self.context.get_editable()
        self.root_url = IVirtualSite(self.request).get_root_url()
        self.docref = getUtility(IIntIds).register(version)
        self.title = version.get_title_or_id()
        self.document = version.get_document_xml_as(
            format='kupu', request=self.request)
        self.metadata = ''


kupucontent = grok.PageTemplate("""
<html>
<head>
<title tal:content="view/title">Title</title>
<link type="text/css" rel="stylesheet"
      tal:attributes="href string:${view/root_url}/globals/frontend.css" />
<link type="text/css" rel="stylesheet"
      tal:attributes="href string:${view/root_url}/globals/kupu.css" />
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<meta name="docref" tal:attributes="content view/docref" />
<tal:metadata tal:replace="structure view/metadata" />
</head>
<tal:body tal:replace="structure view/document">Content</tal:body>
</html>
""")
