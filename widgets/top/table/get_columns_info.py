## Script (Python) "get_columns_info"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
request = context.REQUEST
node = request.node
columns = int(node.getAttribute('columns'))
if node.hasAttribute('column_info'):
    column_info = node.getAttribute('column_info')
else:
    result = []
    for i in range(columns):
        result.append({'align': 'left', 'width': 1, 'html_width':'%s%%' % (100/columns) })
    request.set('columns_info', result)
    return result

lookup = { 'L':'left', 'C':'center', 'R': 'right' }

result = []
for info in column_info.split():
    info = info.split(':')
    try:
        align = info[0]
    except IndexError:
        align = 'L'
    try:
        width = int(info[1])
    except IndexError:
        width = 0
    except ValueError:
        width = 0
    info_dict = {
        'align': lookup.get(align, 'L'),
        }
    if width:
        info_dict['width'] = width
    result.append(info_dict)

# too much info, ignore it
if len(result) > columns:
    result = result[:columns]
# not enough info, take average and add to missing columns
elif len(result) < columns:
    total = 0
    for info in result:
        total += info.get('width', 0)
    average = total / len(result)
    if average > 0:
        for i in range(columns - len(result)):
            result.append({'align': 'left', 'width': average })

# calculate percentages
total = 0
for info in result:
    total += info.get('width', 0)
for info in result:
    if info.get('width'):
        percentage = int((float(info['width'])/total) * 100)
        info['html_width'] = '%s%%' % percentage

# so rows can get it without going through this rigmarole again..
request.set('columns_info', result)
return result
