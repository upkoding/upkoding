//
//
// dropzone.js
//
// Initializes dropzone plugin on elements to facilitate drag/drop for uploads
//

import jQuery from 'jquery';
// import Dropzone from 'dropzone';

window.Dropzone.autoDiscover = false;

(($) => {
  $(() => {
    let template = `<li class="list-group-item dz-preview dz-file-preview">
      <div class="media align-items-center dz-details">
        <ul class="avatars">
          <li>
            <div class="avatar bg-primary dz-file-representation">
              <i class="material-icons">attach_file</i>
            </div>
          </li>
        </ul>
        <div class="media-body d-flex justify-content-between align-items-center">
          <div class="dz-file-details">
            <span class="dz-filename"><span data-dz-name></span></span<br>
            <span class="text-small dz-size" data-dz-size></span>
          </div>
          <img alt="Loader" src="assets/img/loader.svg" class="dz-loading" />
          <div class="dropdown">
            <button class="btn-options" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
              <i class="material-icons">more_vert</i>
            </button>
            <div class="dropdown-menu dropdown-menu-right">
              <a class="dropdown-item text-danger" href="#" data-dz-remove>Delete</a>
            </div>
          </div>
          <button class="btn btn-danger btn-sm dz-remove" data-dz-remove>
            Cancel
          </button>
        </div>
      </div>
      <div class="progress dz-progress">
        <div class="progress-bar dz-upload" data-dz-uploadprogress></div>
      </div>
    </li>`;
    template = document.querySelector('.dz-template') ? document.querySelector('.dz-template').innerHTML : template;
    $('.dropzone').dropzone({
      previewTemplate: template,
      thumbnailWidth: 320,
      thumbnailHeight: 320,
      thumbnailMethod: 'contain',
      previewsContainer: '.dropzone-previews',
    });
  });
})(jQuery);
