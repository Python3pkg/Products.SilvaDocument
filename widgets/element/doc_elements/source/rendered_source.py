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
    html = """<div class="warning"><b>[""" + \
    unicode(_("external source element is broken")) + \
    "]</b><br /> " + unicode(_("error message:")) + " " + str(err) + "</div>"
except:
    # Ugh, bare except to catch *all* cases...
    html = """<div class="warning"><b>[""" + \
    unicode(_("external source element is broken")) + "]</b><br />" + \
    unicode(_("Unfortunately however, there no error message available...")) + \
    "</div>"

return html
