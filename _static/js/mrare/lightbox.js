// simple lightbox

import jQuery from 'jquery';
import SimpleLightbox from 'simple-lightbox';

const lightbox = (($) => {
  SimpleLightbox.registerAsJqueryPlugin($);
  $('.simpleLightbox a').simpleLightbox();
})(jQuery);

export default lightbox;
