
import logging

from silva.core.upgrade.upgrade import BaseUpgrader, AnyMetaType, content_path
from Products.SilvaDocument.interfaces import IDocument

logger = logging.getLogger('silva.core.upgrade')


VERSION_A2='2.2a2'


class SilvaXMLUpgrader(BaseUpgrader):
    '''Upgrades all SilvaXML (documents), converting
       <toc> elements to cs_toc sources and
       <citation> elements to cs_citation sources'''

    def validate(self, doc):
        return IDocument.providedBy(doc)

    def upgrade(self, doc):
        # The 3.0 upgrader only upgrade the published, working and
        # last closed version. Only apply this upgrader on thoses.
        for version_id in [doc.get_public_version(),
                           doc.get_unapproved_version(),
                           doc.get_last_closed_version()]:
            if version_id is None:
                continue
            version = doc._getOb(version_id, None)
            if version is None or not hasattr(version, 'content'):
                continue
            dom = version.content
            if hasattr(dom, 'documentElement'):
                self._upgrade_tocs(version, dom.documentElement)
                self._upgrade_citations(version, dom.documentElement)
        return doc

    def _upgrade_citations(self, version, doc_el):
        cites = doc_el.getElementsByTagName('cite')
        if cites:
            logger.info(u'Upgrading CITE Elements in %s', content_path(version))
        for c in cites:
            author = source = ''
            citation = []
            #html isn't currently allowed in author, source, so
            # we don't need to "sanity" check them!
            for node in c.childNodes:
                if not node.firstChild:
                    continue
                val = node.firstChild.\
                    writeStream().getvalue().replace('&lt;','<')
                if node.nodeType == node.ELEMENT_NODE:
                    if node.nodeName == 'author':
                        author = val
                    elif node.nodeName == 'source':
                        source = val
                    else:
                        citation.append(val)
                else:
                    citation.append(val)
            citation = ''.join(citation)

            cs = doc_el.createElement('source')
            cs.setAttribute('id','cs_citation')

            p = doc_el.createElement('parameter')
            p.setAttribute('type','string')
            p.setAttribute('key','source')
            p.appendChild(doc_el.createTextNode(source))
            cs.appendChild(p)

            p = doc_el.createElement('parameter')
            p.setAttribute('type','string')
            p.setAttribute('key','author')
            p.appendChild(doc_el.createTextNode(author))
            cs.appendChild(p)

            p = doc_el.createElement('parameter')
            p.setAttribute('type','string')
            p.setAttribute('key','citation')
            p.appendChild(doc_el.createTextNode(citation))
            cs.appendChild(p)

            c.parentNode.replaceChild(cs,c)

    def _upgrade_tocs(self, version, doc_el):
        tocs = doc_el.getElementsByTagName('toc')
        if tocs:
            logger.info('Upgrading TOC Elements in: %s' %
                        ('/'.join(version.getPhysicalPath())))
        path = '/'.join(version.get_container().getPhysicalPath())
        for t in tocs:
            depth = t.getAttribute('toc_depth')
            if not depth:
                depth = '0'

            cs = doc_el.createElement('source')
            cs.setAttribute('id','cs_toc')

            p = doc_el.createElement('parameter')
            p.setAttribute('type','string')
            p.setAttribute('key','paths')
            p.appendChild(doc_el.createTextNode(path))
            cs.appendChild(p)

            p = doc_el.createElement('parameter')
            p.setAttribute('type','boolean')
            p.setAttribute('key','show_icon')
            p.appendChild(doc_el.createTextNode('0'))
            cs.appendChild(p)

            #don't add this parameter, instead let silva
            # use the default value, which is to show
            # all publishable types
            #p = doc_el.createElement('parameter')
            #p.setAttribute('type','list')
            #p.setAttribute('key','toc_types')
            #toc_types = tocrendering.compute_default_show_types()
            #s = str(toc_types)
            #p.appendChild(doc_el.createTextNode(str(toc_types))
            #"['Silva Document','Silva Folder','Silva Publication']"))
            #cs.appendChild(p)

            p = doc_el.createElement('parameter')
            p.setAttribute('type','string')
            p.setAttribute('key','css_class')
            cs.appendChild(p)

            # make sure the sort order is the old default, of
            # "silva folder order"
            p = doc_el.createElement('parameter')
            p.setAttribute('type','string')
            p.setAttribute('key','sort_on')
            p.appendChild(doc_el.createTextNode('silva'))
            cs.appendChild(p)

            p = doc_el.createElement('parameter')
            p.setAttribute('type','string')
            p.setAttribute('key','capsule_title')
            cs.appendChild(p)

            p = doc_el.createElement('parameter')
            p.setAttribute('type','string')
            p.setAttribute('key','depth')
            p.appendChild(doc_el.createTextNode(depth))
            cs.appendChild(p)

            p = doc_el.createElement('parameter')
            p.setAttribute('type','boolean')
            p.setAttribute('key','display_headings')
            p.appendChild(doc_el.createTextNode('0'))
            cs.appendChild(p)

            p = doc_el.createElement('parameter')
            p.setAttribute('type','string')
            p.setAttribute('key','alignment')
            cs.appendChild(p)

            p = doc_el.createElement('parameter')
            p.setAttribute('type','string')
            p.setAttribute('key','css_style')
            cs.appendChild(p)

            p = doc_el.createElement('parameter')
            p.setAttribute('type','string')
            p.setAttribute('key','order')
            p.appendChild(doc_el.createTextNode('normal'))
            cs.appendChild(p)

            p = doc_el.createElement('parameter')
            p.setAttribute('type','boolean')
            p.setAttribute('key','link_headings')
            p.appendChild(doc_el.createTextNode('0'))
            cs.appendChild(p)

            p = doc_el.createElement('parameter')
            p.setAttribute('type','boolean')
            p.setAttribute('key','show_desc')
            p.appendChild(doc_el.createTextNode('0'))
            cs.appendChild(p)

            t.parentNode.replaceChild(cs,t)

xml_ugrader = SilvaXMLUpgrader(VERSION_A2, AnyMetaType)
