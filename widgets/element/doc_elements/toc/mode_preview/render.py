#XXX removed append_to_url (it used to be /edit/tab_preview)
# as it was causing errors in the preview tab...:
# since links in the lower-frame of the preview tab don't have
# a target, they load within the lower frame, creating an
# infinite loop.  This needs to be readdressed when the link
# rendering is revised, see:
# https://bugs.launchpad.net/silva/+bug/101364
# https://bugs.launchpad.net/silva/+bug/100917
# https://bugs.launchpad.net/silva/+bug/100158
# https://bugs.launchpad.net/silva/+bug/101245
return context.content(public=0)
