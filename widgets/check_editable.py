## Script (Python) "check_editable"

node = container.REQUEST.other['node']
content = node.get_content()

if content.get_editable() is None:
  return 0
if not content.sec_create_lock():
  return 0
content.sec_update_last_author_info()
return 1
