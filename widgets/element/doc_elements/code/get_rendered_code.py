code = context.get_code_object()

if not code:
    return '<span class="warning">[Code element is broken]</span>'

ret = code()
if not same_type(ret, u''):
    encoding = context.service_old_codesource_charset.charset()
    ret = unicode(ret, encoding, 'replace')

return ret
