
CKEDITOR.dialog.add('silvalink', function( editor ) {
    var dialog;
    return {
        title: 'Hello world',
        contents: [
            {id: 'hello_tab',
             label: '',
             title: '',
             expand: true,
             padding: 0,
             elements: [
                 {type: 'html',
                  id: 'text',
                  html: '',
                  focus: true,
                  onLoad: function(data) {
                      console.log(this);
                      console.log(this.getElement());
                      var div = $(this.getElement().$);
                      jQuery.ajax({
                          url: '/prout/cs_citation/get_rendered_form_for_editor',
                          dataType: 'html',
                          data: {docref: 757107539},
                          success: function (stuff, status, request) {
                              div.html(stuff);
                          }
                      });
                      console.log(this.getDialog().getContentElement('hello_tab', 'text'));
                  }
                 },
                 {type: 'reference',
                  id: 'reference',
                 }
             ]
            }
        ]
    };
});

