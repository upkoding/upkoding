//
//
// filter.js
//
// Initialises the List.js plugin and provides interface to list objects
//

import jQuery from 'jquery';
import List from 'list.js';
import mrUtil from './util';

const mrFilterList = (($) => {
  /**
   * Check for List.js dependency
   * List.js - http://listjs.com
   */
  if (typeof List === 'undefined') {
    throw new Error('mrFilterList requires list.js (http://listjs.com)');
  }

  /**
   * ------------------------------------------------------------------------
   * Constants
   * ------------------------------------------------------------------------
   */

  const NAME = 'mrFilterList';
  const VERSION = '1.0.0';
  const DATA_KEY = 'mr.filterList';
  const EVENT_KEY = `.${DATA_KEY}`;
  const DATA_API_KEY = '.data-api';
  const JQUERY_NO_CONFLICT = $.fn[NAME];

  const Event = {
    LOAD_DATA_API: `load${EVENT_KEY}${DATA_API_KEY}`,
  };

  const Selector = {
    FILTER: '[data-filter-list]',
    DATA_ATTR: 'filter-list',
    DATA_ATTR_CAMEL: 'filterList',
    DATA_FILTER_BY: 'data-filter-by',
    DATA_FILTER_BY_CAMEL: 'filterBy',
    FILTER_INPUT: 'filter-list-input',
    FILTER_TEXT: 'filter-by-text',
  };

  /**
   * ------------------------------------------------------------------------
   * Class Definition
   * ------------------------------------------------------------------------
   */

  class FilterList {
    constructor(element) {
      // The current data-filter-list element
      this.element = element;

      // Get class of list elements to be used within this data-filter-list element
      const listData = element.dataset[Selector.DATA_ATTR_CAMEL];

      // data-filter-by rules collected from filterable elements
      // to be passed to List.js
      this.valueNames = [];

      // List.js instances included in this filterList
      this.lists = [];

      // Find all matching list elements and initialise List.js on each
      this.initAllLists(listData);

      // Bind the search input to each list in the array of lists
      this.bindInputEvents();
    }

    // version getter
    static get VERSION() {
      return VERSION;
    }

    initAllLists(listData) {
      // Initialise each list matching the selector in data-filter-list attribute
      mrUtil.forEach(this.element.querySelectorAll(`.${listData}`), (index, listElement) => {
        this.initList(this.element, listElement);
      });
    }

    initList(element, listElement) {
      // Each individual list needs a unique ID to be added
      // as a class as List.js identifies lists by class
      const listID = `${Selector.DATA_ATTR}-${new Date().getTime()}`;

      // Use the first child of the list and parse all data-filter-by attributes inside.
      // Pass to parseFilters to construct an array of valueNames appropriate for List.js
      const filterables = listElement.querySelectorAll(`*:first-child [${Selector.DATA_FILTER_BY}]`);
      mrUtil.forEach(filterables, (index, filterElement) => {
        // Parse the comma separated values in the data-filter-by attribute
        // on each filterable element
        this.parseFilters(
          listElement,
          filterElement,
          filterElement.dataset[Selector.DATA_FILTER_BY_CAMEL],
        );
      });

      // De-duplicate the array by creating new set of stringified objects and
      // mapping back to parsed objects.
      // This is necessary because similar items in the list element could produce
      // the same rule in the valueNames array.
      this.valueNames = mrUtil.dedupArray(this.valueNames);

      // Add unique ID as class to the list so List.js can handle it individually
      listElement.classList.add(listID);

      // Set up the list instance using the List.js library
      const list = new List(element, {
        valueNames: this.valueNames,
        listClass: listID,
      });

      // Add this list instance to the array associated with this filterList instance
      // as each filterList can have miltiple list instances connected to the
      // same filter-list-input
      this.lists.push(list);
    }

    parseFilters(listElement, filterElement, filterBy) {
      // Get a jQuery instance of the list for easier class manipulation on multiple elements
      const $listElement = $(listElement);
      let filters = [];
      // Get array of filter-by instructions from the data-filter-by attribute
      try {
        filters = filterBy.split(',');
      } catch (err) {
        throw new Error(`Cannot read comma separated data-filter-by attribute: "
          ${filterBy}" on element: 
          ${this.element}`);
      }

      filters.forEach((filter) => {
        // Store appropriate rule for List.js in the valueNames array
        if (filter === 'text') {
          if (filterElement.className !== `${filterElement.nodeName}-${Selector.FILTER_TEXT}`) {
            this.valueNames.push(`${filterElement.className} ${filterElement.nodeName}-${Selector.FILTER_TEXT}`);
          }
          $listElement.find(`${filterElement.nodeName.toLowerCase()}[${Selector.DATA_FILTER_BY}*="text"]`)
            // Prepend element type to class on filterable element as List.js needs separate classes
            .addClass(`${filterElement.nodeName}-${Selector.FILTER_TEXT}`);
        } else if (filter.indexOf('data-') === 0) {
          $listElement.find(`[${Selector.DATA_FILTER_BY}*="${filter}"]`).addClass(`filter-by-${filter}`);
          this.valueNames.push({ name: `filter-by-${filter}`, data: filter.replace('data-', '') });
        } else if (filterElement.getAttribute(filter)) {
          $listElement.find(`[${Selector.DATA_FILTER_BY}*="${filter}"]`).addClass(`filter-by-${filter}`);
          this.valueNames.push({ name: `filter-by-${filter}`, attr: filter });
        }
      });
    }

    bindInputEvents() {
      const filterInput = this.element.querySelector(`.${Selector.FILTER_INPUT}`);
      // Store reference to data-filter-list element on the input itself
      $(filterInput).data(DATA_KEY, this);
      filterInput.addEventListener('keyup', this.searchLists, false);
      filterInput.addEventListener('paste', this.searchLists, false);
      // Handle submit to disable page reload
      filterInput.closest('form').addEventListener('submit', (evt) => {
        if (evt.preventDefault) {
          // evt.preventDefault();
        }
      });
    }

    searchLists(event) {
      // Retrieve the filterList object from the element
      const filterList = $(this).data(DATA_KEY);
      // Apply the currently searched term to the List.js instances in this filterList instance
      mrUtil.forEach(filterList.lists, (index, list) => {
        list.search(event.target.value);
      });
    }

    static jQueryInterface() {
      return this.each(function jqEachFilterList() {
        const $element = $(this);
        let data = $element.data(DATA_KEY);
        if (!data) {
          data = new FilterList(this);
          $element.data(DATA_KEY, data);
        }
      });
    }
  }
  // END Class definition

  /**
   * ------------------------------------------------------------------------
   * Initialise by data attribute
   * ------------------------------------------------------------------------
   */

  $(window).on(Event.LOAD_DATA_API, () => {
    const filterLists = $.makeArray($(Selector.FILTER));

    /* eslint-disable no-plusplus */
    for (let i = filterLists.length; i--;) {
      const $list = $(filterLists[i]);
      FilterList.jQueryInterface.call($list, $list.data());
    }
  });

  /**
   * ------------------------------------------------------------------------
   * jQuery
   * ------------------------------------------------------------------------
   */
  /* eslint-disable no-param-reassign */
  $.fn[NAME] = FilterList.jQueryInterface;
  $.fn[NAME].Constructor = FilterList;
  $.fn[NAME].noConflict = function FilterListNoConflict() {
    $.fn[NAME] = JQUERY_NO_CONFLICT;
    return FilterList.jQueryInterface;
  };
  /* eslint-enable no-param-reassign */

  return FilterList;
})(jQuery);

export default mrFilterList;
