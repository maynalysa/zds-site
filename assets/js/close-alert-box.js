/* ===== Zeste de Savoir ====================================================
   Close alert-boxes
   ---------------------------------
   Author: Alex-D / Alexandre Demode
   ========================================================================== */

(function($, undefined){
    "use strict";
    
    $(".main").on("click", ".close-alert-box:not(.open-modal)", function(e) {
        $(this).parents(".alert-box:first").slideUp(150, function(){
            $(this).remove();
        });
        e.preventDefault();
    });
})(jQuery);