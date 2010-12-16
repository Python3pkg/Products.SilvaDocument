$(document).ready(function(){
    var element = $('#editor textarea');
    $.each($('div.externalsource', $(element)), function(index, item) {
      $(item).attr('contenteditable', 'false');
    });
    element.ckeditor(function(){}, {
      entities: false,
      toolbar: 'silva',
      toolbar_silva: [
        ['SilvaAjaxSave', '-', 'Source'],
        ['Cut','Copy','Paste','PasteText','PasteFromWord','-','Scayt'],
        ['Undo','Redo','-','Find','Replace','-','SelectAll','RemoveFormat'],
        ['Image','Flash','Table','HorizontalRule','Smiley','SpecialChar','PageBreak'],
        '/',
        ['Styles','Format'],
        ['Bold','Italic','Strike'],
        ['NumberedList','BulletedList','-','Outdent','Indent','Blockquote'],
        ['Link','Unlink','Anchor'],
        ['Maximize','-','About']
      ],
      extraPlugins: 'silvaajaxsave'
    });
});
