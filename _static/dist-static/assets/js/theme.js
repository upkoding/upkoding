/*!
  * Pipeline Bootstrap Theme
  * Copyright 2018-2021 Medium Rare (#)
  */
(function (global, factory) {
  typeof exports === 'object' && typeof module !== 'undefined' ? factory(exports, require('jquery')) :
  typeof define === 'function' && define.amd ? define(['exports', 'jquery'], factory) :
  (global = typeof globalThis !== 'undefined' ? globalThis : global || self, factory(global.theme = {}, global.jQuery));
}(this, (function (exports, jQuery) { 'use strict';

  function _interopDefaultLegacy (e) { return e && typeof e === 'object' && 'default' in e ? e : { 'default': e }; }

  var jQuery__default = /*#__PURE__*/_interopDefaultLegacy(jQuery);

  //

  var mrUtil = function ($) {
    var VERSION = '1.2.0';
    var Tagname = {
      SCRIPT: 'script'
    };
    var Selector = {
      RECAPTCHA: '[data-recaptcha]'
    }; // Activate tooltips

    $('body').tooltip({
      selector: '[data-toggle="tooltip"]',
      container: 'body'
    }); // Activate popovers

    $('body').popover({
      selector: '[data-toggle="popover"]',
      container: 'body'
    }); // Activate toasts

    $('.toast').toast();
    var Util = {
      version: VERSION,
      selector: Selector,
      activateIframeSrc: function activateIframeSrc(iframe) {
        var $iframe = $(iframe);

        if ($iframe.attr('data-src')) {
          $iframe.attr('src', $iframe.attr('data-src'));
        }
      },
      idleIframeSrc: function idleIframeSrc(iframe) {
        var $iframe = $(iframe);
        $iframe.attr('data-src', $iframe.attr('src')).attr('src', '');
      },
      forEach: function forEach(array, callback, scope) {
        if (array) {
          if (array.length) {
            for (var i = 0; i < array.length; i += 1) {
              callback.call(scope, i, array[i]); // passes back stuff we need
            }
          } else if (array[0] || mrUtil.isElement(array)) {
            callback.call(scope, 0, array);
          }
        }
      },
      dedupArray: function dedupArray(arr) {
        return arr.reduce(function (p, c) {
          // create an identifying String from the object values
          var id = JSON.stringify(c); // if the JSON string is not found in the temp array
          // add the object to the output array
          // and add the key to the temp array

          if (p.temp.indexOf(id) === -1) {
            p.out.push(c);
            p.temp.push(id);
          }

          return p; // return the deduped array
        }, {
          temp: [],
          out: []
        }).out;
      },
      isElement: function isElement(obj) {
        return !!(obj && obj.nodeType === 1);
      },
      getFuncFromString: function getFuncFromString(funcName, context) {
        var findFunc = funcName || null; // if already a function, return

        if (typeof findFunc === 'function') return funcName; // if string, try to find function or method of object (of "obj.func" format)

        if (typeof findFunc === 'string') {
          if (!findFunc.length) return null;
          var target = context || window;
          var func = findFunc.split('.');

          while (func.length) {
            var ns = func.shift();
            if (typeof target[ns] === 'undefined') return null;
            target = target[ns];
          }

          if (typeof target === 'function') return target;
        } // return null if could not parse


        return null;
      },
      getScript: function getScript(source, callback) {
        var script = document.createElement(Tagname.SCRIPT);
        var prior = document.getElementsByTagName(Tagname.SCRIPT)[0];
        script.async = 1;
        script.defer = 1;

        script.onreadystatechange = function (_, isAbort) {
          if (isAbort || !script.readyState || /loaded|complete/.test(script.readyState)) {
            script.onload = null;
            script.onreadystatechange = null;
            script = undefined;

            if (!isAbort && callback && typeof callback === 'function') {
              callback();
            }
          }
        };

        script.onload = script.onreadystatechange;
        script.src = source;
        prior.parentNode.insertBefore(script, prior);
      },
      isIE: function isIE() {
        var ua = window.navigator.userAgent;
        var isIE = /MSIE|Trident/.test(ua);
        return isIE;
      }
    };
    return Util;
  }(jQuery__default['default']);

  var commonjsGlobal = typeof globalThis !== 'undefined' ? globalThis : typeof window !== 'undefined' ? window : typeof global !== 'undefined' ? global : typeof self !== 'undefined' ? self : {};

  function createCommonjsModule(fn, basedir, module) {
  	return module = {
  		path: basedir,
  		exports: {},
  		require: function (path, base) {
  			return commonjsRequire(path, (base === undefined || base === null) ? module.path : base);
  		}
  	}, fn(module, module.exports), module.exports;
  }

  function commonjsRequire () {
  	throw new Error('Dynamic requires are not currently supported by @rollup/plugin-commonjs');
  }

  var simpleLightbox = createCommonjsModule(function (module) {
  (function(root, factory) {

      if ( module.exports) {
          module.exports = factory();
      } else {
          root.SimpleLightbox = factory();
      }

  }(commonjsGlobal, function() {

      function assign(target) {

          for (var i = 1; i < arguments.length; i++) {

              var obj = arguments[i];

              if (obj) {
                  for (var key in obj) {
                      obj.hasOwnProperty(key) && (target[key] = obj[key]);
                  }
              }

          }

          return target;

      }

      function addClass(element, className) {

          if (element && className) {
              element.className += ' ' + className;
          }

      }

      function removeClass(element, className) {

          if (element && className) {
              element.className = element.className.replace(
                  new RegExp('(\\s|^)' + className + '(\\s|$)'), ' '
              ).trim();
          }

      }

      function parseHtml(html) {

          var div = document.createElement('div');
          div.innerHTML = html.trim();

          return div.childNodes[0];

      }

      function matches(el, selector) {

          return (el.matches || el.matchesSelector || el.msMatchesSelector).call(el, selector);

      }

      function getWindowHeight() {

          return 'innerHeight' in window
              ? window.innerHeight
              : document.documentElement.offsetHeight;

      }

      function SimpleLightbox(options) {

          this.init.apply(this, arguments);

      }

      SimpleLightbox.defaults = {

          // add custom classes to lightbox elements
          elementClass: '',
          elementLoadingClass: 'slbLoading',
          htmlClass: 'slbActive',
          closeBtnClass: '',
          nextBtnClass: '',
          prevBtnClass: '',
          loadingTextClass: '',

          // customize / localize controls captions
          closeBtnCaption: 'Close',
          nextBtnCaption: 'Next',
          prevBtnCaption: 'Previous',
          loadingCaption: 'Loading...',

          bindToItems: true, // set click event handler to trigger lightbox on provided $items
          closeOnOverlayClick: true,
          closeOnEscapeKey: true,
          nextOnImageClick: true,
          showCaptions: true,

          captionAttribute: 'title', // choose data source for library to glean image caption from
          urlAttribute: 'href', // where to expect large image

          startAt: 0, // start gallery at custom index
          loadingTimeout: 100, // time after loading element will appear

          appendTarget: 'body', // append elsewhere if needed

          beforeSetContent: null, // convenient hooks for extending library behavoiur
          beforeClose: null,
          afterClose: null,
          beforeDestroy: null,
          afterDestroy: null,

          videoRegex: new RegExp(/youtube.com|vimeo.com/) // regex which tests load url for iframe content

      };

      assign(SimpleLightbox.prototype, {

          init: function(options) {

              options = this.options = assign({}, SimpleLightbox.defaults, options);

              var self = this;
              var elements;

              if (options.$items) {
                  elements = options.$items.get();
              }

              if (options.elements) {
                  elements = [].slice.call(
                      typeof options.elements === 'string'
                          ? document.querySelectorAll(options.elements)
                          : options.elements
                  );
              }

              this.eventRegistry = {lightbox: [], thumbnails: []};
              this.items = [];
              this.captions = [];

              if (elements) {

                  elements.forEach(function(element, index) {

                      self.items.push(element.getAttribute(options.urlAttribute));
                      self.captions.push(element.getAttribute(options.captionAttribute));

                      if (options.bindToItems) {

                          self.addEvent(element, 'click', function(e) {

                              e.preventDefault();
                              self.showPosition(index);

                          }, 'thumbnails');

                      }

                  });

              }

              if (options.items) {
                  this.items = options.items;
              }

              if (options.captions) {
                  this.captions = options.captions;
              }

          },

          addEvent: function(element, eventName, callback, scope) {

              this.eventRegistry[scope || 'lightbox'].push({
                  element: element,
                  eventName: eventName,
                  callback: callback
              });

              element.addEventListener(eventName, callback);

              return this;

          },

          removeEvents: function(scope) {

              this.eventRegistry[scope].forEach(function(item) {
                  item.element.removeEventListener(item.eventName, item.callback);
              });

              this.eventRegistry[scope] = [];

              return this;

          },

          next: function() {

              return this.showPosition(this.currentPosition + 1);

          },

          prev: function() {

              return this.showPosition(this.currentPosition - 1);

          },

          normalizePosition: function(position) {

              if (position >= this.items.length) {
                  position = 0;
              } else if (position < 0) {
                  position = this.items.length - 1;
              }

              return position;

          },

          showPosition: function(position) {

              var newPosition = this.normalizePosition(position);

              if (typeof this.currentPosition !== 'undefined') {
                  this.direction = newPosition > this.currentPosition ? 'next' : 'prev';
              }

              this.currentPosition = newPosition;

              return this.setupLightboxHtml()
                  .prepareItem(this.currentPosition, this.setContent)
                  .show();

          },

          loading: function(on) {

              var self = this;
              var options = this.options;

              if (on) {

                  this.loadingTimeout = setTimeout(function() {

                      addClass(self.$el, options.elementLoadingClass);

                      self.$content.innerHTML =
                          '<p class="slbLoadingText ' + options.loadingTextClass + '">' +
                              options.loadingCaption +
                          '</p>';
                      self.show();

                  }, options.loadingTimeout);

              } else {

                  removeClass(this.$el, options.elementLoadingClass);
                  clearTimeout(this.loadingTimeout);

              }

          },

          prepareItem: function(position, callback) {

              var self = this;
              var url = this.items[position];

              this.loading(true);

              if (this.options.videoRegex.test(url)) {

                  callback.call(self, parseHtml(
                      '<div class="slbIframeCont"><iframe class="slbIframe" frameborder="0" allowfullscreen src="' + url + '"></iframe></div>')
                  );

              } else {

                  var $imageCont = parseHtml(
                      '<div class="slbImageWrap"><img class="slbImage" src="' + url + '" /></div>'
                  );

                  this.$currentImage = $imageCont.querySelector('.slbImage');

                  if (this.options.showCaptions && this.captions[position]) {
                      $imageCont.appendChild(parseHtml(
                          '<div class="slbCaption">' + this.captions[position] + '</div>')
                      );
                  }

                  this.loadImage(url, function() {

                      self.setImageDimensions();

                      callback.call(self, $imageCont);

                      self.loadImage(self.items[self.normalizePosition(self.currentPosition + 1)]);

                  });

              }

              return this;

          },

          loadImage: function(url, callback) {

              if (!this.options.videoRegex.test(url)) {

                  var image = new Image();
                  callback && (image.onload = callback);
                  image.src = url;

              }

          },

          setupLightboxHtml: function() {

              var o = this.options;

              if (!this.$el) {

                  this.$el = parseHtml(
                      '<div class="slbElement ' + o.elementClass + '">' +
                          '<div class="slbOverlay"></div>' +
                          '<div class="slbWrapOuter">' +
                              '<div class="slbWrap">' +
                                  '<div class="slbContentOuter">' +
                                      '<div class="slbContent"></div>' +
                                      '<button type="button" title="' + o.closeBtnCaption + '" class="slbCloseBtn ' + o.closeBtnClass + '">×</button>' +
                                      (this.items.length > 1
                                          ? '<div class="slbArrows">' +
                                               '<button type="button" title="' + o.prevBtnCaption + '" class="prev slbArrow' + o.prevBtnClass + '">' + o.prevBtnCaption + '</button>' +
                                               '<button type="button" title="' + o.nextBtnCaption + '" class="next slbArrow' + o.nextBtnClass + '">' + o.nextBtnCaption + '</button>' +
                                            '</div>'
                                          : ''
                                      ) +
                                  '</div>' +
                              '</div>' +
                          '</div>' +
                      '</div>'
                  );

                  this.$content = this.$el.querySelector('.slbContent');

              }

              this.$content.innerHTML = '';

              return this;

          },

          show: function() {

              if (!this.modalInDom) {

                  document.querySelector(this.options.appendTarget).appendChild(this.$el);
                  addClass(document.documentElement, this.options.htmlClass);
                  this.setupLightboxEvents();
                  this.modalInDom = true;

              }

              return this;

          },

          setContent: function(content) {

              var $content = typeof content === 'string'
                  ? parseHtml(content)
                  : content
              ;

              this.loading(false);

              this.setupLightboxHtml();

              removeClass(this.$content, 'slbDirectionNext');
              removeClass(this.$content, 'slbDirectionPrev');

              if (this.direction) {
                  addClass(this.$content, this.direction === 'next'
                      ? 'slbDirectionNext'
                      : 'slbDirectionPrev'
                  );
              }

              if (this.options.beforeSetContent) {
                  this.options.beforeSetContent($content, this);
              }

              this.$content.appendChild($content);

              return this;

          },

          setImageDimensions: function() {

              if (this.$currentImage) {
                  this.$currentImage.style.maxHeight = getWindowHeight() + 'px';
              }

          },

          setupLightboxEvents: function() {

              var self = this;

              if (this.eventRegistry.lightbox.length) {
                  return this;
              }

              this.addEvent(this.$el, 'click', function(e) {

                  var $target = e.target;

                  if (matches($target, '.slbCloseBtn') || (self.options.closeOnOverlayClick && matches($target, '.slbWrap'))) {

                      self.close();

                  } else if (matches($target, '.slbArrow')) {

                      matches($target, '.next') ? self.next() : self.prev();

                  } else if (self.options.nextOnImageClick && self.items.length > 1 && matches($target, '.slbImage')) {

                      self.next();

                  }

              }).addEvent(document, 'keyup', function(e) {

                  self.options.closeOnEscapeKey && e.keyCode === 27 && self.close();

                  if (self.items.length > 1) {
                      (e.keyCode === 39 || e.keyCode === 68) && self.next();
                      (e.keyCode === 37 || e.keyCode === 65) && self.prev();
                  }

              }).addEvent(window, 'resize', function() {

                  self.setImageDimensions();

              });

              return this;

          },

          close: function() {

              if (this.modalInDom) {

                  this.runHook('beforeClose');
                  this.removeEvents('lightbox');
                  this.$el && this.$el.parentNode.removeChild(this.$el);
                  removeClass(document.documentElement, this.options.htmlClass);
                  this.modalInDom = false;
                  this.runHook('afterClose');

              }

              this.direction = undefined;
              this.currentPosition = this.options.startAt;

          },

          destroy: function() {

              this.close();
              this.runHook('beforeDestroy');
              this.removeEvents('thumbnails');
              this.runHook('afterDestroy');

          },

          runHook: function(name) {

              this.options[name] && this.options[name](this);

          }

      });

      SimpleLightbox.open = function(options) {

          var instance = new SimpleLightbox(options);

          return options.content
              ? instance.setContent(options.content).show()
              : instance.showPosition(instance.options.startAt);

      };

      SimpleLightbox.registerAsJqueryPlugin = function($) {

          $.fn.simpleLightbox = function(options) {

              var lightboxInstance;
              var $items = this;

              return this.each(function() {
                  if (!$.data(this, 'simpleLightbox')) {
                      lightboxInstance = lightboxInstance || new SimpleLightbox($.extend({}, options, {$items: $items}));
                      $.data(this, 'simpleLightbox', lightboxInstance);
                  }
              });

          };

          $.SimpleLightbox = SimpleLightbox;

      };

      if (typeof window !== 'undefined' && window.jQuery) {
          SimpleLightbox.registerAsJqueryPlugin(window.jQuery);
      }

      return SimpleLightbox;

  }));
  });

  // simple lightbox

  var lightbox = function ($) {
    simpleLightbox.registerAsJqueryPlugin($);
    $('.simpleLightbox a').simpleLightbox();
  }(jQuery__default['default']);

  function asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) {
    try {
      var info = gen[key](arg);
      var value = info.value;
    } catch (error) {
      reject(error);
      return;
    }

    if (info.done) {
      resolve(value);
    } else {
      Promise.resolve(value).then(_next, _throw);
    }
  }

  function _asyncToGenerator(fn) {
    return function () {
      var self = this,
          args = arguments;
      return new Promise(function (resolve, reject) {
        var gen = fn.apply(self, args);

        function _next(value) {
          asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value);
        }

        function _throw(err) {
          asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err);
        }

        _next(undefined);
      });
    };
  }

  (function ($) {
    var loading = false;
    var blockId = $("#codeblock-editor").data("block-id");
    var codeblockForm = $("#codeblock-form");
    var codeblockRun = $("#codeblock-run");
    var codeblockOutput = $("#codeblock-output");
    var codeblockSuccess = $("#codeblock-success");
    var codeblockSuccessAction = $("#codeblock-success-action");

    function setLoading(yes) {
      loading = yes;

      if (yes) {
        codeblockRun.text(codeblockRun.data("text-loading"));
      } else {
        codeblockRun.text(codeblockRun.data("text"));
      }
    }

    function renderOutput(output) {
      if (output.length > 0) {
        var text = "";
        output.forEach(function (o) {
          text += text === "" ? ">> " + o.title : "\n\n>> " + o.title;

          if (o.text !== null) {
            text += "\n" + o.text;
          }
        });
        codeblockOutput.text(text).removeClass("d-none");
      } else {
        codeblockOutput.text("").addClass("d-none");
      }
    }

    codeblockSuccessAction.on("click", function () {
      codeblockSuccess.modal("hide");
      window.location.reload();
    });
    codeblockForm.on("submit", function (e) {
      e.preventDefault();
      if (loading) return;
      setLoading(true);
      var form = new FormData();
      form.append("csrfmiddlewaretoken", csrfmiddlewaretoken);
      form.append("action", "code_submission");
      form.append("code_block_id", blockId);
      form.append("code_block", editor.getValue());
      var output = [];
      fetch("", {
        method: "post",
        body: form
      }).then( /*#__PURE__*/function () {
        var _ref = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee(resp) {
          var data, completed, result, compile_output, is_expecting_output, is_output_match, status, stderr, stdout, description, error;
          return regeneratorRuntime.wrap(function _callee$(_context) {
            while (1) {
              switch (_context.prev = _context.next) {
                case 0:
                  _context.next = 2;
                  return resp.json();

                case 2:
                  data = _context.sent;

                  if (resp.ok) {
                    completed = data.completed, result = data.result;
                    compile_output = result.compile_output, is_expecting_output = result.is_expecting_output, is_output_match = result.is_output_match, status = result.status, stderr = result.stderr, stdout = result.stdout;
                    description = status.description; // compile output

                    if (compile_output !== null) {
                      output.push({
                        title: "Compile output",
                        text: compile_output
                      });
                    } // stderr


                    if (stderr !== null) {
                      output.push({
                        title: description,
                        text: stderr
                      });
                    } // stdout


                    if (stdout !== null) {
                      output.push({
                        title: "Output",
                        text: stdout
                      });
                    }

                    if (completed) {
                      codeblockSuccess.modal({
                        backdrop: "static"
                      });
                    } else {
                      if (is_expecting_output && !is_output_match && stderr === null) {
                        output.push({
                          title: description,
                          text: "Output program tidak sesuai dengan yang diharapkan!"
                        });
                      }

                      renderOutput(output);
                    }
                  } else {
                    // error
                    error = null;
                    Object.entries(data).forEach(function (item) {
                      error = item[1][0].message;
                    });
                    output.push({
                      title: error,
                      text: null
                    });
                    renderOutput(output);
                  }

                case 4:
                case "end":
                  return _context.stop();
              }
            }
          }, _callee);
        }));

        return function (_x) {
          return _ref.apply(this, arguments);
        };
      }())["finally"](function (_) {
        setLoading(false);
      });
    });
  })(jQuery__default['default']);

  var runtime_1 = createCommonjsModule(function (module) {
  /**
   * Copyright (c) 2014-present, Facebook, Inc.
   *
   * This source code is licensed under the MIT license found in the
   * LICENSE file in the root directory of this source tree.
   */

  var runtime = (function (exports) {

    var Op = Object.prototype;
    var hasOwn = Op.hasOwnProperty;
    var undefined$1; // More compressible than void 0.
    var $Symbol = typeof Symbol === "function" ? Symbol : {};
    var iteratorSymbol = $Symbol.iterator || "@@iterator";
    var asyncIteratorSymbol = $Symbol.asyncIterator || "@@asyncIterator";
    var toStringTagSymbol = $Symbol.toStringTag || "@@toStringTag";

    function define(obj, key, value) {
      Object.defineProperty(obj, key, {
        value: value,
        enumerable: true,
        configurable: true,
        writable: true
      });
      return obj[key];
    }
    try {
      // IE 8 has a broken Object.defineProperty that only works on DOM objects.
      define({}, "");
    } catch (err) {
      define = function(obj, key, value) {
        return obj[key] = value;
      };
    }

    function wrap(innerFn, outerFn, self, tryLocsList) {
      // If outerFn provided and outerFn.prototype is a Generator, then outerFn.prototype instanceof Generator.
      var protoGenerator = outerFn && outerFn.prototype instanceof Generator ? outerFn : Generator;
      var generator = Object.create(protoGenerator.prototype);
      var context = new Context(tryLocsList || []);

      // The ._invoke method unifies the implementations of the .next,
      // .throw, and .return methods.
      generator._invoke = makeInvokeMethod(innerFn, self, context);

      return generator;
    }
    exports.wrap = wrap;

    // Try/catch helper to minimize deoptimizations. Returns a completion
    // record like context.tryEntries[i].completion. This interface could
    // have been (and was previously) designed to take a closure to be
    // invoked without arguments, but in all the cases we care about we
    // already have an existing method we want to call, so there's no need
    // to create a new function object. We can even get away with assuming
    // the method takes exactly one argument, since that happens to be true
    // in every case, so we don't have to touch the arguments object. The
    // only additional allocation required is the completion record, which
    // has a stable shape and so hopefully should be cheap to allocate.
    function tryCatch(fn, obj, arg) {
      try {
        return { type: "normal", arg: fn.call(obj, arg) };
      } catch (err) {
        return { type: "throw", arg: err };
      }
    }

    var GenStateSuspendedStart = "suspendedStart";
    var GenStateSuspendedYield = "suspendedYield";
    var GenStateExecuting = "executing";
    var GenStateCompleted = "completed";

    // Returning this object from the innerFn has the same effect as
    // breaking out of the dispatch switch statement.
    var ContinueSentinel = {};

    // Dummy constructor functions that we use as the .constructor and
    // .constructor.prototype properties for functions that return Generator
    // objects. For full spec compliance, you may wish to configure your
    // minifier not to mangle the names of these two functions.
    function Generator() {}
    function GeneratorFunction() {}
    function GeneratorFunctionPrototype() {}

    // This is a polyfill for %IteratorPrototype% for environments that
    // don't natively support it.
    var IteratorPrototype = {};
    IteratorPrototype[iteratorSymbol] = function () {
      return this;
    };

    var getProto = Object.getPrototypeOf;
    var NativeIteratorPrototype = getProto && getProto(getProto(values([])));
    if (NativeIteratorPrototype &&
        NativeIteratorPrototype !== Op &&
        hasOwn.call(NativeIteratorPrototype, iteratorSymbol)) {
      // This environment has a native %IteratorPrototype%; use it instead
      // of the polyfill.
      IteratorPrototype = NativeIteratorPrototype;
    }

    var Gp = GeneratorFunctionPrototype.prototype =
      Generator.prototype = Object.create(IteratorPrototype);
    GeneratorFunction.prototype = Gp.constructor = GeneratorFunctionPrototype;
    GeneratorFunctionPrototype.constructor = GeneratorFunction;
    GeneratorFunction.displayName = define(
      GeneratorFunctionPrototype,
      toStringTagSymbol,
      "GeneratorFunction"
    );

    // Helper for defining the .next, .throw, and .return methods of the
    // Iterator interface in terms of a single ._invoke method.
    function defineIteratorMethods(prototype) {
      ["next", "throw", "return"].forEach(function(method) {
        define(prototype, method, function(arg) {
          return this._invoke(method, arg);
        });
      });
    }

    exports.isGeneratorFunction = function(genFun) {
      var ctor = typeof genFun === "function" && genFun.constructor;
      return ctor
        ? ctor === GeneratorFunction ||
          // For the native GeneratorFunction constructor, the best we can
          // do is to check its .name property.
          (ctor.displayName || ctor.name) === "GeneratorFunction"
        : false;
    };

    exports.mark = function(genFun) {
      if (Object.setPrototypeOf) {
        Object.setPrototypeOf(genFun, GeneratorFunctionPrototype);
      } else {
        genFun.__proto__ = GeneratorFunctionPrototype;
        define(genFun, toStringTagSymbol, "GeneratorFunction");
      }
      genFun.prototype = Object.create(Gp);
      return genFun;
    };

    // Within the body of any async function, `await x` is transformed to
    // `yield regeneratorRuntime.awrap(x)`, so that the runtime can test
    // `hasOwn.call(value, "__await")` to determine if the yielded value is
    // meant to be awaited.
    exports.awrap = function(arg) {
      return { __await: arg };
    };

    function AsyncIterator(generator, PromiseImpl) {
      function invoke(method, arg, resolve, reject) {
        var record = tryCatch(generator[method], generator, arg);
        if (record.type === "throw") {
          reject(record.arg);
        } else {
          var result = record.arg;
          var value = result.value;
          if (value &&
              typeof value === "object" &&
              hasOwn.call(value, "__await")) {
            return PromiseImpl.resolve(value.__await).then(function(value) {
              invoke("next", value, resolve, reject);
            }, function(err) {
              invoke("throw", err, resolve, reject);
            });
          }

          return PromiseImpl.resolve(value).then(function(unwrapped) {
            // When a yielded Promise is resolved, its final value becomes
            // the .value of the Promise<{value,done}> result for the
            // current iteration.
            result.value = unwrapped;
            resolve(result);
          }, function(error) {
            // If a rejected Promise was yielded, throw the rejection back
            // into the async generator function so it can be handled there.
            return invoke("throw", error, resolve, reject);
          });
        }
      }

      var previousPromise;

      function enqueue(method, arg) {
        function callInvokeWithMethodAndArg() {
          return new PromiseImpl(function(resolve, reject) {
            invoke(method, arg, resolve, reject);
          });
        }

        return previousPromise =
          // If enqueue has been called before, then we want to wait until
          // all previous Promises have been resolved before calling invoke,
          // so that results are always delivered in the correct order. If
          // enqueue has not been called before, then it is important to
          // call invoke immediately, without waiting on a callback to fire,
          // so that the async generator function has the opportunity to do
          // any necessary setup in a predictable way. This predictability
          // is why the Promise constructor synchronously invokes its
          // executor callback, and why async functions synchronously
          // execute code before the first await. Since we implement simple
          // async functions in terms of async generators, it is especially
          // important to get this right, even though it requires care.
          previousPromise ? previousPromise.then(
            callInvokeWithMethodAndArg,
            // Avoid propagating failures to Promises returned by later
            // invocations of the iterator.
            callInvokeWithMethodAndArg
          ) : callInvokeWithMethodAndArg();
      }

      // Define the unified helper method that is used to implement .next,
      // .throw, and .return (see defineIteratorMethods).
      this._invoke = enqueue;
    }

    defineIteratorMethods(AsyncIterator.prototype);
    AsyncIterator.prototype[asyncIteratorSymbol] = function () {
      return this;
    };
    exports.AsyncIterator = AsyncIterator;

    // Note that simple async functions are implemented on top of
    // AsyncIterator objects; they just return a Promise for the value of
    // the final result produced by the iterator.
    exports.async = function(innerFn, outerFn, self, tryLocsList, PromiseImpl) {
      if (PromiseImpl === void 0) PromiseImpl = Promise;

      var iter = new AsyncIterator(
        wrap(innerFn, outerFn, self, tryLocsList),
        PromiseImpl
      );

      return exports.isGeneratorFunction(outerFn)
        ? iter // If outerFn is a generator, return the full iterator.
        : iter.next().then(function(result) {
            return result.done ? result.value : iter.next();
          });
    };

    function makeInvokeMethod(innerFn, self, context) {
      var state = GenStateSuspendedStart;

      return function invoke(method, arg) {
        if (state === GenStateExecuting) {
          throw new Error("Generator is already running");
        }

        if (state === GenStateCompleted) {
          if (method === "throw") {
            throw arg;
          }

          // Be forgiving, per 25.3.3.3.3 of the spec:
          // https://people.mozilla.org/~jorendorff/es6-draft.html#sec-generatorresume
          return doneResult();
        }

        context.method = method;
        context.arg = arg;

        while (true) {
          var delegate = context.delegate;
          if (delegate) {
            var delegateResult = maybeInvokeDelegate(delegate, context);
            if (delegateResult) {
              if (delegateResult === ContinueSentinel) continue;
              return delegateResult;
            }
          }

          if (context.method === "next") {
            // Setting context._sent for legacy support of Babel's
            // function.sent implementation.
            context.sent = context._sent = context.arg;

          } else if (context.method === "throw") {
            if (state === GenStateSuspendedStart) {
              state = GenStateCompleted;
              throw context.arg;
            }

            context.dispatchException(context.arg);

          } else if (context.method === "return") {
            context.abrupt("return", context.arg);
          }

          state = GenStateExecuting;

          var record = tryCatch(innerFn, self, context);
          if (record.type === "normal") {
            // If an exception is thrown from innerFn, we leave state ===
            // GenStateExecuting and loop back for another invocation.
            state = context.done
              ? GenStateCompleted
              : GenStateSuspendedYield;

            if (record.arg === ContinueSentinel) {
              continue;
            }

            return {
              value: record.arg,
              done: context.done
            };

          } else if (record.type === "throw") {
            state = GenStateCompleted;
            // Dispatch the exception by looping back around to the
            // context.dispatchException(context.arg) call above.
            context.method = "throw";
            context.arg = record.arg;
          }
        }
      };
    }

    // Call delegate.iterator[context.method](context.arg) and handle the
    // result, either by returning a { value, done } result from the
    // delegate iterator, or by modifying context.method and context.arg,
    // setting context.delegate to null, and returning the ContinueSentinel.
    function maybeInvokeDelegate(delegate, context) {
      var method = delegate.iterator[context.method];
      if (method === undefined$1) {
        // A .throw or .return when the delegate iterator has no .throw
        // method always terminates the yield* loop.
        context.delegate = null;

        if (context.method === "throw") {
          // Note: ["return"] must be used for ES3 parsing compatibility.
          if (delegate.iterator["return"]) {
            // If the delegate iterator has a return method, give it a
            // chance to clean up.
            context.method = "return";
            context.arg = undefined$1;
            maybeInvokeDelegate(delegate, context);

            if (context.method === "throw") {
              // If maybeInvokeDelegate(context) changed context.method from
              // "return" to "throw", let that override the TypeError below.
              return ContinueSentinel;
            }
          }

          context.method = "throw";
          context.arg = new TypeError(
            "The iterator does not provide a 'throw' method");
        }

        return ContinueSentinel;
      }

      var record = tryCatch(method, delegate.iterator, context.arg);

      if (record.type === "throw") {
        context.method = "throw";
        context.arg = record.arg;
        context.delegate = null;
        return ContinueSentinel;
      }

      var info = record.arg;

      if (! info) {
        context.method = "throw";
        context.arg = new TypeError("iterator result is not an object");
        context.delegate = null;
        return ContinueSentinel;
      }

      if (info.done) {
        // Assign the result of the finished delegate to the temporary
        // variable specified by delegate.resultName (see delegateYield).
        context[delegate.resultName] = info.value;

        // Resume execution at the desired location (see delegateYield).
        context.next = delegate.nextLoc;

        // If context.method was "throw" but the delegate handled the
        // exception, let the outer generator proceed normally. If
        // context.method was "next", forget context.arg since it has been
        // "consumed" by the delegate iterator. If context.method was
        // "return", allow the original .return call to continue in the
        // outer generator.
        if (context.method !== "return") {
          context.method = "next";
          context.arg = undefined$1;
        }

      } else {
        // Re-yield the result returned by the delegate method.
        return info;
      }

      // The delegate iterator is finished, so forget it and continue with
      // the outer generator.
      context.delegate = null;
      return ContinueSentinel;
    }

    // Define Generator.prototype.{next,throw,return} in terms of the
    // unified ._invoke helper method.
    defineIteratorMethods(Gp);

    define(Gp, toStringTagSymbol, "Generator");

    // A Generator should always return itself as the iterator object when the
    // @@iterator function is called on it. Some browsers' implementations of the
    // iterator prototype chain incorrectly implement this, causing the Generator
    // object to not be returned from this call. This ensures that doesn't happen.
    // See https://github.com/facebook/regenerator/issues/274 for more details.
    Gp[iteratorSymbol] = function() {
      return this;
    };

    Gp.toString = function() {
      return "[object Generator]";
    };

    function pushTryEntry(locs) {
      var entry = { tryLoc: locs[0] };

      if (1 in locs) {
        entry.catchLoc = locs[1];
      }

      if (2 in locs) {
        entry.finallyLoc = locs[2];
        entry.afterLoc = locs[3];
      }

      this.tryEntries.push(entry);
    }

    function resetTryEntry(entry) {
      var record = entry.completion || {};
      record.type = "normal";
      delete record.arg;
      entry.completion = record;
    }

    function Context(tryLocsList) {
      // The root entry object (effectively a try statement without a catch
      // or a finally block) gives us a place to store values thrown from
      // locations where there is no enclosing try statement.
      this.tryEntries = [{ tryLoc: "root" }];
      tryLocsList.forEach(pushTryEntry, this);
      this.reset(true);
    }

    exports.keys = function(object) {
      var keys = [];
      for (var key in object) {
        keys.push(key);
      }
      keys.reverse();

      // Rather than returning an object with a next method, we keep
      // things simple and return the next function itself.
      return function next() {
        while (keys.length) {
          var key = keys.pop();
          if (key in object) {
            next.value = key;
            next.done = false;
            return next;
          }
        }

        // To avoid creating an additional object, we just hang the .value
        // and .done properties off the next function object itself. This
        // also ensures that the minifier will not anonymize the function.
        next.done = true;
        return next;
      };
    };

    function values(iterable) {
      if (iterable) {
        var iteratorMethod = iterable[iteratorSymbol];
        if (iteratorMethod) {
          return iteratorMethod.call(iterable);
        }

        if (typeof iterable.next === "function") {
          return iterable;
        }

        if (!isNaN(iterable.length)) {
          var i = -1, next = function next() {
            while (++i < iterable.length) {
              if (hasOwn.call(iterable, i)) {
                next.value = iterable[i];
                next.done = false;
                return next;
              }
            }

            next.value = undefined$1;
            next.done = true;

            return next;
          };

          return next.next = next;
        }
      }

      // Return an iterator with no values.
      return { next: doneResult };
    }
    exports.values = values;

    function doneResult() {
      return { value: undefined$1, done: true };
    }

    Context.prototype = {
      constructor: Context,

      reset: function(skipTempReset) {
        this.prev = 0;
        this.next = 0;
        // Resetting context._sent for legacy support of Babel's
        // function.sent implementation.
        this.sent = this._sent = undefined$1;
        this.done = false;
        this.delegate = null;

        this.method = "next";
        this.arg = undefined$1;

        this.tryEntries.forEach(resetTryEntry);

        if (!skipTempReset) {
          for (var name in this) {
            // Not sure about the optimal order of these conditions:
            if (name.charAt(0) === "t" &&
                hasOwn.call(this, name) &&
                !isNaN(+name.slice(1))) {
              this[name] = undefined$1;
            }
          }
        }
      },

      stop: function() {
        this.done = true;

        var rootEntry = this.tryEntries[0];
        var rootRecord = rootEntry.completion;
        if (rootRecord.type === "throw") {
          throw rootRecord.arg;
        }

        return this.rval;
      },

      dispatchException: function(exception) {
        if (this.done) {
          throw exception;
        }

        var context = this;
        function handle(loc, caught) {
          record.type = "throw";
          record.arg = exception;
          context.next = loc;

          if (caught) {
            // If the dispatched exception was caught by a catch block,
            // then let that catch block handle the exception normally.
            context.method = "next";
            context.arg = undefined$1;
          }

          return !! caught;
        }

        for (var i = this.tryEntries.length - 1; i >= 0; --i) {
          var entry = this.tryEntries[i];
          var record = entry.completion;

          if (entry.tryLoc === "root") {
            // Exception thrown outside of any try block that could handle
            // it, so set the completion value of the entire function to
            // throw the exception.
            return handle("end");
          }

          if (entry.tryLoc <= this.prev) {
            var hasCatch = hasOwn.call(entry, "catchLoc");
            var hasFinally = hasOwn.call(entry, "finallyLoc");

            if (hasCatch && hasFinally) {
              if (this.prev < entry.catchLoc) {
                return handle(entry.catchLoc, true);
              } else if (this.prev < entry.finallyLoc) {
                return handle(entry.finallyLoc);
              }

            } else if (hasCatch) {
              if (this.prev < entry.catchLoc) {
                return handle(entry.catchLoc, true);
              }

            } else if (hasFinally) {
              if (this.prev < entry.finallyLoc) {
                return handle(entry.finallyLoc);
              }

            } else {
              throw new Error("try statement without catch or finally");
            }
          }
        }
      },

      abrupt: function(type, arg) {
        for (var i = this.tryEntries.length - 1; i >= 0; --i) {
          var entry = this.tryEntries[i];
          if (entry.tryLoc <= this.prev &&
              hasOwn.call(entry, "finallyLoc") &&
              this.prev < entry.finallyLoc) {
            var finallyEntry = entry;
            break;
          }
        }

        if (finallyEntry &&
            (type === "break" ||
             type === "continue") &&
            finallyEntry.tryLoc <= arg &&
            arg <= finallyEntry.finallyLoc) {
          // Ignore the finally entry if control is not jumping to a
          // location outside the try/catch block.
          finallyEntry = null;
        }

        var record = finallyEntry ? finallyEntry.completion : {};
        record.type = type;
        record.arg = arg;

        if (finallyEntry) {
          this.method = "next";
          this.next = finallyEntry.finallyLoc;
          return ContinueSentinel;
        }

        return this.complete(record);
      },

      complete: function(record, afterLoc) {
        if (record.type === "throw") {
          throw record.arg;
        }

        if (record.type === "break" ||
            record.type === "continue") {
          this.next = record.arg;
        } else if (record.type === "return") {
          this.rval = this.arg = record.arg;
          this.method = "return";
          this.next = "end";
        } else if (record.type === "normal" && afterLoc) {
          this.next = afterLoc;
        }

        return ContinueSentinel;
      },

      finish: function(finallyLoc) {
        for (var i = this.tryEntries.length - 1; i >= 0; --i) {
          var entry = this.tryEntries[i];
          if (entry.finallyLoc === finallyLoc) {
            this.complete(entry.completion, entry.afterLoc);
            resetTryEntry(entry);
            return ContinueSentinel;
          }
        }
      },

      "catch": function(tryLoc) {
        for (var i = this.tryEntries.length - 1; i >= 0; --i) {
          var entry = this.tryEntries[i];
          if (entry.tryLoc === tryLoc) {
            var record = entry.completion;
            if (record.type === "throw") {
              var thrown = record.arg;
              resetTryEntry(entry);
            }
            return thrown;
          }
        }

        // The context.catch method must only be called with a location
        // argument that corresponds to a known catch block.
        throw new Error("illegal catch attempt");
      },

      delegateYield: function(iterable, resultName, nextLoc) {
        this.delegate = {
          iterator: values(iterable),
          resultName: resultName,
          nextLoc: nextLoc
        };

        if (this.method === "next") {
          // Deliberately forget the last sent value so that we don't
          // accidentally pass it on to the delegate.
          this.arg = undefined$1;
        }

        return ContinueSentinel;
      }
    };

    // Regardless of whether this script is executing as a CommonJS module
    // or not, return the runtime object so that we can declare the variable
    // regeneratorRuntime in the outer scope, which allows this module to be
    // injected easily by `bin/regenerator --include-runtime script.js`.
    return exports;

  }(
    // If this script is executing as a CommonJS module, use module.exports
    // as the regeneratorRuntime namespace. Otherwise create a new empty
    // object. Either way, the resulting object will be used to initialize
    // the regeneratorRuntime variable at the top of this file.
     module.exports 
  ));

  try {
    regeneratorRuntime = runtime;
  } catch (accidentalStrictMode) {
    // This module should not be running in strict mode, so the above
    // assignment should always work unless something is misconfigured. Just
    // in case runtime.js accidentally runs in strict mode, we can escape
    // strict mode using a global Function call. This could conceivably fail
    // if a Content Security Policy forbids using Function, but in that case
    // the proper solution is to fix the accidental strict mode problem. If
    // you've misconfigured your bundler to force strict mode and applied a
    // CSP to forbid Function, and you're not willing to fix either of those
    // problems, please detail your unique predicament in a GitHub issue.
    Function("r", "regeneratorRuntime = r")(runtime);
  }
  });

  (function ($) {
    var reviewForm = $("#timeline-form");
    var reviewFormMessage = $("#timeline-form #timeline-input-message");
    var reviewActionBtn = $("#timeline-form .timeline-btn-action");
    var reviewAlertMessage = $("#timeline-form #timeline-alert");
    var reviewList = $("#timeline-events");
    var loading = false;

    function showAlert(alertType, message) {
      reviewAlertMessage.removeClass("alert-success alert-danger").text(message).addClass(alertType).removeClass("d-none");
    }

    function runReviewAction(target) {
      if (loading) return;
      var btn = $(target);
      var action = btn.data("action");
      btn.text(btn.data("loading-text"));
      fetch(reviewForm.data("url"), {
        method: "post",
        headers: {
          "x-CSRFToken": window.csrfmiddlewaretoken,
          "Content-Type": "application/javascript"
        },
        body: JSON.stringify({
          action: action,
          message: reviewFormMessage.val()
        })
      }).then( /*#__PURE__*/function () {
        var _ref = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee(resp) {
          var _yield$resp$json, message, html;

          return regeneratorRuntime.wrap(function _callee$(_context) {
            while (1) {
              switch (_context.prev = _context.next) {
                case 0:
                  if (!resp.ok) {
                    _context.next = 10;
                    break;
                  }

                  _context.next = 3;
                  return resp.json();

                case 3:
                  _yield$resp$json = _context.sent;
                  message = _yield$resp$json.message;
                  html = _yield$resp$json.html;
                  if (message !== null) showAlert("alert-success", message);

                  if (html !== null) {
                    reviewList.append(html);
                    Prism.highlightAll();
                  }

                  _context.next = 15;
                  break;

                case 10:
                  _context.t0 = showAlert;
                  _context.next = 13;
                  return resp.text();

                case 13:
                  _context.t1 = _context.sent;
                  (0, _context.t0)("alert-danger", _context.t1);

                case 15:
                case "end":
                  return _context.stop();
              }
            }
          }, _callee);
        }));

        return function (_x) {
          return _ref.apply(this, arguments);
        };
      }())["finally"](function () {
        loading = false;
        reviewFormMessage.val("");
        btn.text(btn.data("text"));
      });
    }

    reviewActionBtn.on("click", function (e) {
      runReviewAction(e.target);
    });
  })(jQuery__default['default']);

  var showMainToast = function showMainToast($, title, message) {
    var toastMain = $("#toast-main");
    var toastMainTitle = $("#toast-main .toast-main-title");
    var toastMainTime = $("#toast-main .toast-main-time");
    var toastMainText = $("#toast-main .toast-main-text");
    toastMainTitle.text(title);
    toastMainText.text(message);
    toastMain.toast("show");
  };

  (function ($) {
    var btn = $(".cancel-challenge");
    var url = btn.data("challenge-url");
    btn.on("click", function (e) {
      showMainToast($, "Mohon ditunggu", "Sedang membatalkan tantangan...");
      var data = new FormData();
      data.append("action", "delete");
      data.append("csrfmiddlewaretoken", window.csrfmiddlewaretoken);
      fetch(url, {
        method: "post",
        body: data
      }).then( /*#__PURE__*/function () {
        var _ref = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee(resp) {
          return regeneratorRuntime.wrap(function _callee$(_context) {
            while (1) {
              switch (_context.prev = _context.next) {
                case 0:
                  if (!resp.ok) {
                    _context.next = 6;
                    break;
                  }

                  _context.next = 3;
                  return resp.text();

                case 3:
                  window.location.href = _context.sent;
                  _context.next = 7;
                  break;

                case 6:
                  showMainToast($, "Oops!", "Gagal membatalkan tantangan.");

                case 7:
                case "end":
                  return _context.stop();
              }
            }
          }, _callee);
        }));

        return function (_x) {
          return _ref.apply(this, arguments);
        };
      }());
    });
  })(jQuery__default['default']);

  // import './chat';

  (function () {
    if (typeof $ === "undefined") {
      throw new TypeError("Medium Rare JavaScript requires jQuery. jQuery must be included before theme.js.");
    }
  })();

  exports.lightbox = lightbox;
  exports.mrUtil = mrUtil;

  Object.defineProperty(exports, '__esModule', { value: true });

})));
//# sourceMappingURL=theme.js.map
