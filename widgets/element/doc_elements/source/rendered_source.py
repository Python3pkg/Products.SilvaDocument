request = context.REQUEST
source = context.get_source()
uparameters = context.get_parameters()

parameters = {}
for key, value in uparameters.items():
    parameters[key.encode('ascii')] = value

try:
    html = source.to_html(request, **parameters)
except (Exception), err:
    html = """
<div class="warning"><b>[external source element is broken]</b><br />
error message: %s
</div>""" % err
except:
    # Ugh, bare except to catch *all* cases...
    html = """
<div class="warning"><b>[external source element is broken]</b><br />
Unfortunatly however, there no error message available...
</div>"""

return html
