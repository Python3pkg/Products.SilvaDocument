from Products.Silva.i18n import translate as _

request = context.REQUEST
source = context.get_source()
uparameters = context.get_parameters()

parameters = {}
for key, value in uparameters.items():
    parameters[key.encode('ascii')] = value

try:
    html = source.to_html(request, **parameters)
except (Exception), err:
    html = _("""<div class="warning"><b>[external source element is broken]</b><br /> error message: ${error}
</div>""")
    html.set_mapping({'error': err})
except:
    # Ugh, bare except to catch *all* cases...
    html = _("""<div class="warning"><b>[external source element is broken]</b><br />
Unfortunatly however, there no error message available... </div>""")

return html
