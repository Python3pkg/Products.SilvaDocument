
(function($) {
    CKEDITOR.plugins.add('silvalink', {
        requires: ['dialog'],
        init: function(editor) {
            editor.addCommand(
                'silvalink',
                new CKEDITOR.dialogCommand('silvalink'));
            editor.ui.addButton('SilvaLink', {
                label : 'Link da page',
                command : 'silvalink'
            });

            // XXX template URL.
            var templateURL = $('head base').attr('href').replace(/\/edit$/, '/++resource++Products.SilvaDocument.smi/test.jst')
            var createReferenceUI = function(referenceTemplate) {
                // Create the reference UI element with the given
                // template.
                CKEDITOR.tools.extend(CKEDITOR.ui.dialog, {
                    reference: function(dialog, elementDefinition, htmlList) {
                        if (!arguments.length)
                            return;
                        var innerHTML = function() {
                            return referenceTemplate.expand({id: elementDefinition.id});
                        };
                        CKEDITOR.ui.dialog.uiElement.call(
                            this, dialog, elementDefinition, htmlList, 'div', null, null, innerHTML);
                    }
                }, true);
                CKEDITOR.ui.dialog.reference.prototype = new CKEDITOR.ui.dialog.uiElement;
                referenceBuilder = {
                    build : function(dialog, elementDefinition, output) {
                        return new CKEDITOR.ui.dialog[elementDefinition.type](dialog, elementDefinition, output);
                    }
                };
                CKEDITOR.dialog.addUIElement('reference', referenceBuilder);
            };

            // Fetch reference UI template from the server and create
            // the UI element.
            $.ajax({
                url: templateURL,
                dataType: 'html',
                success: function(template) {
                    createReferenceUI(new jsontemplate.Template(template, {}));
                }
            });

            CKEDITOR.dialog.add('silvalink', this.path + 'dialogs/link.js');


        }
    });
})(jQuery);

