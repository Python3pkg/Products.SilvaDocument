$(document).ready(function(){
    var element = $('#editor textarea');
    $.each($('div.externalsource', $(element)), function(index, item) {
      console.log(item);
      $(item).attr('contenteditable', 'false');
    });
    element.ckeditor(function(){}, {toolbar: 'Full'});
});
