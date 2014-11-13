jQuery(document).ready(function(){
	var form = jQuery('.edit_form');
	var select = jQuery('.post_select');
	select.on('change', function (event) {
		var selected_option = jQuery(this).find(":selected");
		jQuery.get('/postdata', {post_id: selected_option.attr('value')}, function (data, textStatus, jqXHR) {
			var content_div = jQuery('.post-stuff');
			content_div.html(data);
		});
	});
})