##parameters=model=None, toc_depth=-1

from Products.Silva.adapters import tocrendering

adapter = tocrendering.getTOCRenderingAdapter(model)
return adapter.render_tree(toc_depth)
