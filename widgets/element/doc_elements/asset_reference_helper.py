## Script (Python) "asset_reference_helper"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=lookup_type=None,path=None,filter=None,asset_context,folder_context=None
##title=

# renders the javascript event handler code for the asset lookup.

params = [] 
if filter is not None:
    params.append("filter=%s" %filter)
if folder_context is not None:
    params.append("folder_context=%s" % '/'.join(folder_context))
if asset_context is not None:
    params.append("asset_context=%s" % '/'.join(asset_context))

return 'getAssetReference(\'%s/edit/%s_lookup?%s\',\'<a href=\"_id_\">_reference_</a>\', \'focusbox\', \'data\', 1);;return false;;' % (path, lookup_type, "&".join(params)) 
