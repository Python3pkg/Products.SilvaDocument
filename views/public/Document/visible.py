##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=object=None
##title=
# $Id: visible.py,v 1.1 2003/07/28 13:54:56 zagy Exp $

if object is None:
    return 1
if object.meta_type == 'Silva AutoTOC':
    return 0
return 1

