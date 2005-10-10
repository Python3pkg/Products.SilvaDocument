from Products.Silva.mangle import String

request = context.REQUEST
node = request.node

node.setAttribute('type', String.inputConvert(request['element_type']))

lookup = {'left':'L', 'center':'C', 'right':'R'}

columns = context.get_columns()
# process column info
column_info = []
for column in range(columns):
    key = 'column_align_%s' % column
    if request.has_key(key):
       align = lookup.get(request[key], 'L')
    else:
       align = 'L'
    key = 'column_width_%s' % column
    if request.has_key(key):
       width = request[key]
       try:
         width = int(width)
         if width < 1:
             width = 1
       except ValueError:
         width = '*'
    else:
       width = '*'
       
    column_info.append('%s:%s' % (align, width))

node.setAttribute('column_info', String.inputConvert(' '.join(column_info)))
