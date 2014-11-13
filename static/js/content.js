jQuery(document).ready(function(){

    // add exists function to jQuery
    jQuery.fn.exists = function () {
        return this.length !== 0;
    }

    addCommentHandlers();
    removeUnusedPhotoDivs();

    jQuery('#retrieve').on('click', function (event) {
        var posts = jQuery('.post-stuff')
        var lastPost = posts[posts.length - 1]
        jQuery.get(
            '/more', 
            {'last_post': lastPost.dataset['id']},
            function (data, status, jqXHR) {
                if (data == 'nothing') {
                    jQuery('.retrieve-button').css('display', 'none');
                    jQuery('.replace-me').replaceWith(createGotoArchiveHtml());
                    return;

                }
                jQuery('.replace-me').replaceWith(data);
                removeUnusedPhotoDivs();
                addCommentHandlers();
                Galleria.loadTheme('/themes/galleria.classicmod.js');
                Galleria.run('.galleria');
            });
    });

    
    var galleria_elements = jQuery('.galleria');
    if (galleria_elements.size() > 0) { 
        Galleria.loadTheme('/themes/galleria.classicmod.js');
        Galleria.run('.galleria');
    }

    
});

function removeUnusedPhotoDivs() {
    photo_divs = jQuery('.image-div');
    jQuery.each(photo_divs, function(index, photo_div) {
        images = jQuery(photo_div).find('img');
        if (images.length == 0) {
            jQuery(photo_div).remove();
        }
    });
}

function addCommentHandlers() {
    comment_div = jQuery('.comments');
    jQuery.each(comment_div, function(index, comments){

        comments = jQuery(comments);
        comment_wrapper = comments.find('.comment-wrapper');
        comment_wrapper.css('max-height', '0');
        comment_wrapper.css('visibility', 'hidden');

        comment_heading = comments.find('.comment-heading');
        comment_heading.data('open', 'false');

        comment_chevron = comments.find('.comment-chevron');

        comment_heading.on('click', function(event){
            toggleCommentVisibility(event);
        });

        comment_chevron.on('click', function(event){
                toggleCommentVisibility(event);
        });

        comments.find('.comment-form').on('submit', function(event){
            event.preventDefault();
            that = this;
            jQuery.post("/addcomment", jQuery(this).serialize(), function(){
                comments = jQuery(that).parents(".comments");
                comment_view = comments.find(".comment-view");
                comment_html = createCommentHtml(that.name, that.comment);
                comment_view.append(comment_html);
            });
            comments.find('.comment-form').css('display', '');
            comments.find('.comment-button').css('display', '');
        });
        comments.find('.abort-comment').on('click', function (event) {
            comments.find('.comment-input').each(function (index, input) {
                input.value = '';
            });
            comments.find('.comment-form').css('display', '');
            comments.find('.comment-button').css('display', '');
        });

        comments.find('.comment-button').on('click', function (event) {
            jQuery(this).css('display','none');
            comments.find('.comment-form').css('display', 'block');
        });
    });
}


function toggleCommentVisibility(event){
    comments = jQuery(event.currentTarget).parents(".comments");
    wrapper = comments.find(".comment-wrapper");
    chevron = comments.find(".comment-chevron");
    if (!chevron.exists()) {
        chevron = comments.find(".comment-chevron-open");
    }
    heading = comments.find(".comment-heading");
    if (heading.data('open') == 'false'){
        wrapper.css('visibility', 'visible');
        wrapper.css('max-height', '10000px');
        chevron.css('transform', 'rotate(180deg)');
        chevron.css('-webkit-transform', 'rotate(180deg)');
        chevron.addClass('comment-chevron-open');
        chevron.removeClass('comment-chevron');
        heading.data('open', 'true');
    } else {
        wrapper.css('visibility', 'hidden');
        wrapper.css('max-height', '0');
        chevron.removeClass('comment-chevron-open');
        chevron.addClass('comment-chevron');
        chevron.css('transform', 'rotate(0deg)');
        chevron.css('-webkit-transform', 'rotate(0deg)');
        heading.data('open', 'false');
    }
}

function createCommentHtml(name, comment) {
    var html =  "<div class='comment-view-item flexbox'><div class='comment-view-name flex-item'>" +
                escape(name.value) +
                ":</div><div class='comment-view-comment flex-item'>" +
                escape(comment.value) +
                "</div></div>";
    return jQuery(html);
}

function createGotoArchiveHtml() {
    var html =  '<div class="transbox flex-item">' +
                '<div class="content">' +
                '<h3>Wenn du noch mehr sehen willst, dann schau doch mal ins <a href="/archive">Archiv</a></h3>' +
                '</div>' +
                '</div>';
    return jQuery(html);
}

function escape(unsafe) {
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
 }
