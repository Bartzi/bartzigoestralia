jQuery(document).ready(function(){
    // set opacity of arrow on mouse-over
    menu = jQuery('.menu');
    arrow = jQuery('.menu-arrow');
    menu_items = jQuery('.menu-item');

    menu.on('mouseenter', function(event){
        menu_items.addClass('menu-item-trans');
        arrow.css('opacity', 0);
        menu_items.css('visibility', 'visible');
    });

    menu.on('mouseleave', function(event){
        menu_items.removeClass('menu-item-trans');
        arrow.css('opacity', 100);
        menu_items.css('visibility', 'hidden');
    });
});
