jQuery(document).ready(function(){

    var form = jQuery('.post-form');
    form.on('submit', function (event) {
        event.preventDefault();
        that = this;
            jQuery.post("/addPost", jQuery(this).serialize(), function(message){
                jQuery('.message').text(message);
            });
    });
    form.find('.btn-info').on('click', function (event) {
    	var text = form.find("#post-content")[0].value;
    	jQuery('.preview-div').html(text);
    });

});