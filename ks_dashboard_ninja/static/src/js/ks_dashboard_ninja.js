odoo.define('ks_dashboard_ninja.ks_dashboard', function (require) {
    "use strict";

    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var viewRegistry = require('web.view_registry');

    var _t = core._t;
    var QWeb = core.qweb;
    var utils = require('web.utils');
    var config = require('web.config');
    var framework = require('web.framework');
    var time = require('web.time');
    var datepicker = require("web.datepicker");
    var Widget = require('web.Widget');
    var ajax = require('web.ajax');
    var field_utils = require('web.field_utils');
    var ControlPanelMixin = require('web.ControlPanelMixin');
    var crash_manager = require('web.crash_manager');
    var KsGlobalFunction = require('ks_dashboard_ninja.KsGlobalFunction');

    var KsQuickEditView = require('ks_dashboard_ninja.quick_edit_view');

    var KsDashboardNinja = Widget.extend(ControlPanelMixin, {
        // To show or hide top control panel flag.
        need_control_panel: false,

        /**
         * @override
         */

        jsLibs: ['/ks_dashboard_ninja/static/lib/js/jquery.ui.touch-punch.min.js',
                 '/ks_dashboard_ninja/static/lib/js/jsPDF.js',
                '/ks_dashboard_ninja/static/lib/js/Chart.bundle.min.js',
                '/ks_dashboard_ninja/static/lib/js/chartjs-plugin-datalabels.js',
        ],
        cssLibs: ['/ks_dashboard_ninja/static/lib/css/Chart.css',
                '/ks_dashboard_ninja/static/lib/css/Chart.min.css'],

        init: function (parent, state, params) {
            this._super.apply(this, arguments);
            this.action_manager = parent;
            this.ksIsDashboardManager = false;
            this.ksDashboardEditMode = false;
            this.ksNewDashboardName = false;
            this.file_type_magic_word = {
                '/': 'jpg',
                'R': 'gif',
                'i': 'png',
                'P': 'svg+xml',
            };
            this.ksAllowItemClick = true;

            //Dn Filters Iitialization
            var l10n = _t.database.parameters;
            this.form_template = 'ks_dashboard_ninja_template_view';
            this.date_format = time.strftime_to_moment_format(_t.database.parameters.date_format)
            this.date_format = this.date_format.replace(/\bYY\b/g, "YYYY");
            this.datetime_format = time.strftime_to_moment_format((_t.database.parameters.date_format + ' ' + l10n.time_format))
            //            this.is_dateFilter_rendered = false;
            this.ks_date_filter_data;

            // Adding date filter selection options in dictionary format : {'id':{'days':1,'text':"Text to show"}}
            this.ks_date_filter_selections = {
                'l_none': 'Date Filter',
                'l_day': 'Today',
                't_week': 'This Week',
                't_month': 'This Month',
                't_quarter': 'This Quarter',
                't_year': 'This Year',
                'n_day': 'Next Day',
                'n_week': 'Next Week',
                'n_month': 'Next Month',
                'n_quarter': 'Next Quarter',
                'n_year': 'Next Year',
                'ls_day': 'Last Day',
                'ls_week': 'Last Week',
                'ls_month': 'Last Month',
                'ls_quarter': 'Last Quarter',
                'ls_year': 'Last Year',
                'l_week': 'Last 7 days',
                'l_month': 'Last 30 days',
                'l_quarter': 'Last 90 days',
                'l_year': 'Last 365 days',
                'l_custom': 'Custom Filter',
            };
            // To make sure date filter show date in specific order.
            this.ks_date_filter_selection_order = ['l_day', 't_week','t_month','t_quarter','t_year','n_day',
                    'n_week','n_month','n_quarter','n_year','ls_day','ls_week','ls_month','ls_quarter',
                    'ls_year','l_week','l_month', 'l_quarter','l_year','l_custom'];

            this.ks_dashboard_id = state.params.ks_dashboard_id;

            this.gridstack_options = {
                staticGrid: true,
                float: false
            };
            this.gridstackConfig = {};
            this.grid = false;
            this.chartMeasure = {};
            this.chart_container = {};

            this.ksChartColorOptions = ['default', 'cool', 'warm', 'neon'];
            this.ksUpdateDashboardItem = this.ksUpdateDashboardItem.bind(this);


            this.ksDateFilterSelection = false;
            this.ksDateFilterStartDate = false;
            this.ksDateFilterEndDate = false;
            this.ksUpdateDashboard = {};
        },

        getContext: function () {
            var self = this;
            var context = {
                ksDateFilterSelection: self.ksDateFilterSelection,
                ksDateFilterStartDate: self.ksDateFilterStartDate,
                ksDateFilterEndDate: self.ksDateFilterEndDate,
            }
            return Object.assign(context,odoo.session_info.user_context)
        },

        on_attach_callback: function () {
            var self = this;
            if(self.ks_dashboard_data){
                self.ksRenderDashboard();
                self.ks_set_update_interval();
                if (self.ks_dashboard_data && self.ks_dashboard_data.ks_item_data) self._ksSaveCurrentLayoutLocally();
            }
        },

        ks_set_update_interval : function(){
            var self = this;
            if (self.ks_dashboard_data.ks_item_data){

                Object.keys(self.ks_dashboard_data.ks_item_data).forEach(function (item_id){
                    var item_data =  self.ks_dashboard_data.ks_item_data[item_id]
                    var updateValue = item_data["ks_update_items_data"];
                    if (updateValue){
                        if (!(item_id in self.ksUpdateDashboard)){
                             if(['ks_tile','ks_list_view','ks_kpi'].indexOf(item_data['ks_dashboard_item_type'])>=0){
                                var ksItemUpdateInterval = setInterval(function(){self.ksFetchUpdateItem(item_id)}, updateValue);
                            }
                            else {
                                var ksItemUpdateInterval = setInterval(function(){self.ksFetchChartItem(item_id)}, updateValue);
                            }
                            self.ksUpdateDashboard[item_id] = ksItemUpdateInterval;
                        }
                    }
                });
            }
        },

        // Note : this is exceptionally bind to this function.
        ksUpdateDashboardItem : function (items) {
            var self = this;

            for (var i=0;i<items.length;i++){
                var item_data = self.ks_dashboard_data.ks_item_data[items[i]];

                if (item_data['ks_dashboard_item_type'] == 'ks_list_view'){
                    var item_view = self.$el.find(".grid-stack-item[data-gs-id="+item_data.id+"]");
                    item_view.find('.card-body').empty();
                    item_view.find('.card-body').append(self.renderListViewData(item_data));
                }
                else if (item_data['ks_dashboard_item_type'] === 'ks_tile'){
                    var item_view = self._ksRenderDashboardTile(item_data)
                    self.$el.find(".grid-stack-item[data-gs-id="+item_data.id+"]").empty();
                    self.$el.find(".grid-stack-item[data-gs-id="+item_data.id+"]").append($(item_view).find('.ks_dashboarditem_id'));
                }
                else if(item_data['ks_dashboard_item_type'] === 'ks_kpi'){
                    var item_view = self.renderKpi(item_data);
                    self.$el.find(".grid-stack-item[data-gs-id="+item_data.id+"]").empty();
                    self.$el.find(".grid-stack-item[data-gs-id="+item_data.id+"]").append($(item_view).find('.ks_dashboarditem_id'));
                }
                else{
                    self.grid.removeWidget(self.$el.find(".grid-stack-item[data-gs-id="+item_data.id+"]"));
                    self.ksRenderDashboardItems([item_data]);
                }

            }
            self.grid.setStatic(true);
        },

        on_detach_callback : function(){
            var self = this;
            self.ks_remove_update_interval();
            if(self.ksDashboardEditMode) self._ksSaveCurrentLayout();

            self.ksDateFilterSelection = false;
            self.ksDateFilterStartDate = false;
            self.ksDateFilterEndDate = false;
            self.ks_fetch_data();
        },

        ks_remove_update_interval : function(){
            var self = this;
            if (self.ksUpdateDashboard){
                Object.keys(self.ksUpdateDashboard).forEach(function(itemInterval){

                    clearInterval(self.ksUpdateDashboard[itemInterval]);
                    delete self.ksUpdateDashboard[itemInterval]
                });
            }
        },


        events: {
            'click #ks_add_item_selection > li': 'onAddItemTypeClick',
            'click .ks_dashboard_add_layout': '_onKsAddLayoutClick',
            'click .ks_dashboard_edit_layout': '_onKsEditLayoutClick',
            'click .ks_dashboard_select_item': 'onKsSelectItemClick',
            'click .ks_dashboard_save_layout': '_onKsSaveLayoutClick',
            'click .ks_dashboard_cancel_layout': '_onKsCancelLayoutClick',
            'click .ks_item_click': '_onKsItemClick',
            //            'click .ks_dashboard_item_action': '_onKsItemActionClick',
            'click .ks_dashboard_item_customize': '_onKsItemCustomizeClick',
            'click .ks_dashboard_item_delete': '_onKsDeleteItemClick',
            'change .ks_dashboard_header_name': '_onKsInputChange',
            'click .ks_duplicate_item': 'onKsDuplicateItemClick',
            'click .ks_move_item': 'onKsMoveItemClick',
            'click .ks_qe_dropdown_menu ': function (e) {
                e.stopPropagation();
            },
            'click .ks_dashboard_menu_container ': function (e) {
                e.stopPropagation();
            },
            'show.bs.dropdown .ks_dashboard_item_button_container': 'onKsDashboardMenuContainerShow',
            'hide.bs.dropdown .ks_dashboard_item_button_container': 'onKsDashboardMenuContainerHide',
            'click .ks_dashboard_item_action': 'ksStopClickPropagation',

            //  Dn Filters Events
            'click .ks-options-btn': '_onksOptionsClick',
            'click .print-dashboard-btn': '_onKsDashboardPrint',
            'click .apply-dashboard-date-filter': '_onKsApplyDateFilter',
            'click .clear-dashboard-date-filter': '_onKsClearDateValues',
            'change #ks_start_date_picker': '_ksShowApplyClearDateButton',
            'change #ks_end_date_picker': '_ksShowApplyClearDateButton',
            'click #ks_date_selector_container>li': '_ksOnDateFilterMenuSelect',
            'click #ks_item_info': 'ksOnListItemInfoClick',
            'click .ks_chart_color_options': 'ksRenderChartColorOptions',
            'click #ks_chart_canvas_id': 'onChartCanvasClick',
            'click .ks_dashboard_item_chart_info': 'onChartMoreInfoClick',
            'click .chart_xls_export': 'ksChartExportXLS',
            'click .chart_pdf_export': 'ksChartExportPdf',
            'click .ks_dashboard_quick_edit_action_popup': 'ksOnQuickEditView',
            'click .ks_dashboard_item_drill_up':'ksOnDrillUp',
        },


        willStart: function () {
            var self = this;
            return $.when(ajax.loadLibs(this), this._super()).then(function () {
                return self.ks_fetch_data();
            });
        },

        start: function () {
            var self = this;
            self.set({ 'title':self.ks_dashboard_data.name})
            self.ks_set_default_chart_view();
            return this._super();
        },

        ksOnQuickEditView : function(e){
            var self = this;
            var item_id = e.currentTarget.dataset.itemId;
            var item_data = this.ks_dashboard_data.ks_item_data[item_id];
            var item_el = $.find(`[data-gs-id=${item_id}]`);
            var $quickEditButton = $(QWeb.render('ksQuickEditButtonContainer',{
                grid : $.extend({},item_el[0].dataset)
            }));
            $(item_el).before($quickEditButton);

            var ksQuickEditViewWidget = new KsQuickEditView.QuickEditView(this,{
                item : item_data,
            });

            var item_right_position = $(item_el).position().left + $(item_el).width();
            var item_gap_from_right = $(item_el).parent().width() - item_right_position;
            if(item_gap_from_right<280) {
                $($quickEditButton.find('.ks_qe_dropdown_menu')).css("left", "calc(100% - "+`${280-item_gap_from_right}px)`);
            }

            ksQuickEditViewWidget.appendTo($quickEditButton.find('.dropdown-menu'));

            ksQuickEditViewWidget.on("canBeDestroyed",this,function(result){
                if(ksQuickEditViewWidget){
                    ksQuickEditViewWidget = false;
                    $quickEditButton.find('.ks_dashboard_item_action').click();
                }
            });

            ksQuickEditViewWidget.on("canBeRendered",this,function(result){
               $quickEditButton.find('.ks_dashboard_item_action').click();
            });

            ksQuickEditViewWidget.on("openFullItemForm",this,function(result){
               ksQuickEditViewWidget.destroy();
               $quickEditButton.find('.ks_dashboard_item_action').click();
               self.ks_open_item_form_page(parseInt(item_id));
            });


            $quickEditButton.on("hide.bs.dropdown",function(ev){

                if (ksQuickEditViewWidget){
                    ksQuickEditViewWidget.ksDiscardChanges();
                    ksQuickEditViewWidget = false;
                    self.ks_set_update_interval();
                    $quickEditButton.remove();
                }else{
                    self.ks_set_update_interval();
                    $quickEditButton.remove();
                }

            });

            $quickEditButton.on("show.bs.dropdown",function(){
                self.ks_remove_update_interval();
            });

            e.stopPropagation();
        },

        ks_set_default_chart_view: function () {
            Chart.plugins.unregister(ChartDataLabels);
            Chart.plugins.register({
                afterDraw: function (chart) {
                    if (chart.data.labels.length === 0) {
                        // No data is present
                        var ctx = chart.chart.ctx;
                        var width = chart.chart.width;
                        var height = chart.chart.height
                        chart.clear();

                        ctx.save();
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.font = "3rem 'Lucida Grande'";
                        ctx.fillText('No data available', width / 2, height / 2);
                        ctx.restore();
                    }
                }
            });

            Chart.Legend.prototype.afterFit = function() {
                    var chart_type = this.chart.config.type;
                    if(chart_type === "pie" || chart_type ==="doughnut" ) {
                        this.height = this.height;
                    }else{
                        this.height = this.height + 20;
                    };
            };
        },

        ksRenderChartColorOptions: function (e) {
            var self = this;
            if (!$(e.currentTarget).parent().hasClass('ks_date_filter_selected')) {
                //            FIXME : Correct this later.
                var $parent = $(e.currentTarget).parent().parent();
                $parent.find('.ks_date_filter_selected').removeClass('ks_date_filter_selected')
                $(e.currentTarget).parent().addClass('ks_date_filter_selected')
                var item_data = self.ks_dashboard_data.ks_item_data[$parent.data().itemId];
                var chart_data = JSON.parse(item_data.ks_chart_data);
                var data = $parent.data();
                this.ksChartColors(e.currentTarget.dataset.chartColor, this.chart_container[$parent.data().itemId], $parent.data().chartType, $parent.data().chartFamily, item_data.ks_bar_chart_stacked, item_data.ks_semi_circle_chart,item_data.ks_show_data_value,chart_data)
                this._rpc({
                    model: 'ks_dashboard_ninja.item',
                    method: 'write',
                    args: [$parent.data().itemId, {
                        "ks_chart_item_color": e.currentTarget.dataset.chartColor
                    }],
                });
            }
        },


        //To fetch dashboard data.
        ks_fetch_data: function () {
            var self = this;
            return this._rpc({
                model: 'ks_dashboard_ninja.board',
                method: 'ks_fetch_dashboard_data',
                args: [self.ks_dashboard_id],
                context: self.getContext(),
            }).done(function (result) {
                self.ks_dashboard_data = result;
            });
        },

        on_reverse_breadcrumb: function (state) {
            var self = this;
            this.action_manager.do_push_state(state);
            return $.when(self.ks_fetch_data());
        },

        ksStopClickPropagation: function (e) {
            this.ksAllowItemClick = false;
        },

        onKsDashboardMenuContainerShow: function (e) {
            $(e.currentTarget).addClass('ks_dashboard_item_menu_show');
            this.ks_remove_update_interval();
             //            Dynamic Bootstrap menu populate Image Report
            if($(e.target).hasClass('ks_dashboard_more_action')){
                var chart_id = e.target.dataset.itemId;
                var name = this.ks_dashboard_data.ks_item_data[chart_id].name;
                var base64_image = this.chart_container[chart_id].toBase64Image();
                $(e.target).find('.dropdown-menu').empty();
                $(e.target).find('.dropdown-menu').append($(QWeb.render('ksMoreChartOptions', {
                href: base64_image, download_fileName:name,chart_id:chart_id })))
            }
        },

        onKsDashboardMenuContainerHide: function (e) {
            $(e.currentTarget).removeClass('ks_dashboard_item_menu_show');
            this.ks_set_update_interval();
        },

        ks_get_dark_color: function (color, opacity, percent) {
            var num = parseInt(color.slice(1), 16),
                amt = Math.round(2.55 * percent),
                R = (num >> 16) + amt,
                G = (num >> 8 & 0x00FF) + amt,
                B = (num & 0x0000FF) + amt;
            return "#" + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 + (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 + (B < 255 ? B < 1 ? 0 : B : 255)).toString(16).slice(1) + "," + opacity;
        },

        //        Number Formatter into shorthand function
        ksNumFormatter: function (num, digits) {
            var negative;
            var si = [{
                    value: 1,
                    symbol: ""
                },
                {
                    value: 1E3,
                    symbol: "k"
                },
                {
                    value: 1E6,
                    symbol: "M"
                },
                {
                    value: 1E9,
                    symbol: "G"
                },
                {
                    value: 1E12,
                    symbol: "T"
                },
                {
                    value: 1E15,
                    symbol: "P"
                },
                {
                    value: 1E18,
                    symbol: "E"
                }
            ];
            if(num<0){
                num = Math.abs(num)
                negative = true
            }
            var rx = /\.0+$|(\.[0-9]*[1-9])0+$/;
            var i;
            for (i = si.length - 1; i > 0; i--) {
                if (num >= si[i].value) {
                    break;
                }
            }
            if(negative){
                return "-" +(num / si[i].value).toFixed(digits).replace(rx, "$1") + si[i].symbol;
            }else{
                return (num / si[i].value).toFixed(digits).replace(rx, "$1") + si[i].symbol;
            }
        },


        //    This is to convert color #value into RGB format to add opacity value.
        _ks_get_rgba_format: function (val) {
            var rgba = val.split(',')[0].match(/[A-Za-z0-9]{2}/g);
            rgba = rgba.map(function (v) {
                return parseInt(v, 16)
            }).join(",");
            return "rgba(" + rgba + "," + val.split(',')[1] + ")";
        },

        ksRenderDashboard: function () {
            var self = this;
            self.$el.empty();
            self.$el.addClass('ks_dashboard_ninja d-flex flex-column');

            var $ks_header = $(QWeb.render('ksDashboardNinjaHeader', {
                ks_dashboard_name: self.ks_dashboard_data.name,
                ks_dashboard_manager: self.ks_dashboard_data.ks_dashboard_manager,
                date_selection_data: self.ks_date_filter_selections,
                date_selection_order: self.ks_date_filter_selection_order
            }));

            if (!config.device.isMobile) {
                $ks_header.addClass("ks_dashboard_header_sticky")
            }

            self.$el.append($ks_header);

            self.ksRenderDashboardMainContent();
        },

        ksRenderDashboardMainContent: function () {
            var self = this;
            if (self.ks_dashboard_data.ks_item_data) {
                var items = self.ksSortItems(self.ks_dashboard_data.ks_item_data);
                var $dashboard_body_container = $(QWeb.render('ks_main_body_container'))
                var $gridstackContainer = $dashboard_body_container.find(".grid-stack");

                self._renderDateFilterDatePicker();
                self.$el.find('.ks_dashboard_link').removeClass("ks_hide");
                self.$el.find('.print-dashboard-btn').removeClass("ks_hide");
                $('.ks_dashboard_items_list').remove();

                $dashboard_body_container.appendTo(self.$el)
                $gridstackContainer.gridstack(self.gridstack_options);
                self.grid = $gridstackContainer.data('gridstack');

                self.ksRenderDashboardItems(items);
                self.grid.setStatic(true);
                self._ksSaveCurrentLayout();
            } else if (!self.ks_dashboard_data.ks_item_data) {
                 self.$el.find('.ks_dashboard_link').addClass("ks_hide");
                self._ksRenderNoItemView();
            }
        },

        ksSortItems: function(ks_item_data){
            var items = []
            var self = this;
            var item_data = Object.assign({}, ks_item_data);
            if (self.ks_dashboard_data.ks_gridstack_config) {
               self.gridstackConfig = JSON.parse(self.ks_dashboard_data.ks_gridstack_config);
               var a = Object.values(self.gridstackConfig);
               var b = Object.keys(self.gridstackConfig);

               for(var i = 0; i<a.length;i++ ){
                   a[i]['id'] = b[i];
               }

               a.sort(function(a,b){
                   return (36*a.y+a.x) - (36*b.y+b.x);
               });

               for (var i = 0; i < a.length; i++)
               {
                   if(item_data[a[i]['id']]){
                        items.push(item_data[a[i]['id']]);
                        delete item_data[a[i]['id']];
                   }
               }
            }
           return items.concat(Object.values(item_data));
        },

        ksRenderDashboardItems: function (items) {
            var self = this;
            var item_view;
            self.$el.find('.print-dashboard-btn').addClass("ks_pro_print_hide");

            if (self.ks_dashboard_data.ks_gridstack_config) {
                self.gridstackConfig = JSON.parse(self.ks_dashboard_data.ks_gridstack_config);
            }

            for (var i = 0; i < items.length; i++) {
                if(self.grid){
                    if (items[i].ks_dashboard_item_type === 'ks_tile') {
                        item_view = self._ksRenderDashboardTile(items[i])
                        if (items[i].id in self.gridstackConfig) {
                            self.grid.addWidget($(item_view), self.gridstackConfig[items[i].id].x, self.gridstackConfig[items[i].id].y, self.gridstackConfig[items[i].id].width, self.gridstackConfig[items[i].id].height, false, 6, null, 2, 2, items[i].id);
                        } else {
                            self.grid.addWidget($(item_view), 0, 0, 11, 2, true, 6, null, 2, 2, items[i].id);
                        }
                    } else if (items[i].ks_dashboard_item_type === 'ks_list_view') {
                        self._renderListView(items[i], self.grid)
                    } else if (items[i].ks_dashboard_item_type === 'ks_kpi') {
                        var $kpi_preview = self.renderKpi(items[i])
                        var item_id = items[i].id;
                        if (item_id in self.gridstackConfig) {
                           self.grid.addWidget($kpi_preview, self.gridstackConfig[item_id].x, self.gridstackConfig[item_id].y, self.gridstackConfig[item_id].width, self.gridstackConfig[item_id].height, false, 8, null, 2, 3, item_id);
                        } else {
                            self.grid.addWidget($kpi_preview, 0, 0, 8, 2, true, 8, null, 2, 3, item_id);
                        }
                    } else {
                        self._renderGraph(items[i], self.grid)
                    }
                }
            }
            self.grid.setStatic(true);
        },

        _ksRenderDashboardTile: function (tile) {
            var self = this;
            var ks_container_class = 'grid-stack-item',
                ks_inner_container_class = 'grid-stack-item-content';

            var ks_icon_url, item_view;
            var ks_rgba_background_color, ks_rgba_font_color, ks_rgba_default_icon_color;
            var style_main_body, style_image_body_l2, style_domain_count_body, style_button_customize_body,
                style_button_delete_body;
            var data_count = self.ksNumFormatter(tile.ks_record_count, 1);
            var count = field_utils.format.float(tile.ks_record_count, Float64Array)

            if (tile.ks_icon_select == "Custom") {
                if (tile.ks_icon) {
                    ks_icon_url = 'data:image/' + (self.file_type_magic_word[tile.ks_icon] || 'png') + ';base64,' + tile.ks_icon;
                } else {
                    ks_icon_url = false;
                }
            }

            tile.ksIsDashboardManager = self.ks_dashboard_data.ks_dashboard_manager;
            ks_rgba_background_color = self._ks_get_rgba_format(tile.ks_background_color);
            ks_rgba_font_color = self._ks_get_rgba_format(tile.ks_font_color);
            ks_rgba_default_icon_color = self._ks_get_rgba_format(tile.ks_default_icon_color);
            style_main_body = "background-color:" + ks_rgba_background_color + ";color : " + ks_rgba_font_color + ";";
            switch (tile.ks_layout) {
                case 'layout1':
                    item_view = QWeb.render('ks_dashboard_item_layout1', {
                        item: tile,
                        style_main_body: style_main_body,
                        ks_icon_url: ks_icon_url,
                        ks_rgba_default_icon_color: ks_rgba_default_icon_color,
                        ks_container_class: ks_container_class,
                        ks_inner_container_class: ks_inner_container_class,
                        ks_dashboard_list: self.ks_dashboard_data.ks_dashboard_list,
                        data_count: data_count,
                        count: count,
                    });
                    break;

                case 'layout2':
                    var ks_rgba_dark_background_color_l2 = self._ks_get_rgba_format(self.ks_get_dark_color(tile.ks_background_color.split(',')[0], tile.ks_background_color.split(',')[1], -10));
                    style_image_body_l2 = "background-color:" + ks_rgba_dark_background_color_l2 + ";";
                    item_view = QWeb.render('ks_dashboard_item_layout2', {
                        item: tile,
                        style_image_body_l2: style_image_body_l2,
                        style_main_body: style_main_body,
                        ks_icon_url: ks_icon_url,
                        ks_rgba_default_icon_color: ks_rgba_default_icon_color,
                        ks_container_class: ks_container_class,
                        ks_inner_container_class: ks_inner_container_class,
                        ks_dashboard_list: self.ks_dashboard_data.ks_dashboard_list,
                        data_count: data_count,
                        count: count,
                    });
                    break;

                case 'layout3':
                    item_view = QWeb.render('ks_dashboard_item_layout3', {
                        item: tile,
                        style_main_body: style_main_body,
                        ks_icon_url: ks_icon_url,
                        ks_rgba_default_icon_color: ks_rgba_default_icon_color,
                        ks_container_class: ks_container_class,
                        ks_inner_container_class: ks_inner_container_class,
                        ks_dashboard_list: self.ks_dashboard_data.ks_dashboard_list,
                        data_count: data_count,
                        count: count,
                    });
                    break;

                case 'layout4':
                    style_main_body = "color : " + ks_rgba_font_color + ";border : solid;border-width : 1px;border-color:" + ks_rgba_background_color + ";"
                    style_image_body_l2 = "background-color:" + ks_rgba_background_color + ";";
                    style_domain_count_body = "color:" + ks_rgba_background_color + ";";
                    item_view = QWeb.render('ks_dashboard_item_layout4', {
                        item: tile,
                        style_main_body: style_main_body,
                        style_image_body_l2: style_image_body_l2,
                        style_domain_count_body: style_domain_count_body,
                        ks_icon_url: ks_icon_url,
                        ks_rgba_default_icon_color: ks_rgba_default_icon_color,
                        ks_container_class: ks_container_class,
                        ks_inner_container_class: ks_inner_container_class,
                        ks_dashboard_list: self.ks_dashboard_data.ks_dashboard_list,
                        data_count: data_count,
                        count: count,
                    });
                    break;

                case 'layout5':
                    item_view = QWeb.render('ks_dashboard_item_layout5', {
                        item: tile,
                        style_main_body: style_main_body,
                        ks_icon_url: ks_icon_url,
                        ks_rgba_default_icon_color: ks_rgba_default_icon_color,
                        ks_container_class: ks_container_class,
                        ks_inner_container_class: ks_inner_container_class,
                        ks_dashboard_list: self.ks_dashboard_data.ks_dashboard_list,
                        data_count: data_count,
                        count: count,
                    });
                    break;

                case 'layout6':
                    ks_rgba_default_icon_color = self._ks_get_rgba_format(tile.ks_default_icon_color);
                    item_view = QWeb.render('ks_dashboard_item_layout6', {
                        item: tile,
                        style_image_body_l2: style_image_body_l2,
                        style_main_body: style_main_body,
                        ks_icon_url: ks_icon_url,
                        ks_rgba_default_icon_color: ks_rgba_default_icon_color,
                        ks_container_class: ks_container_class,
                        ks_inner_container_class: ks_inner_container_class,
                        ks_dashboard_list: self.ks_dashboard_data.ks_dashboard_list,
                        data_count: data_count,
                        count: count,
                    });
                    break;

                default:
                    item_view = QWeb.render('ks_dashboard_item_layout_default', {
                        item: tile
                    });
                    break;
            }
            return item_view;
        },

        _renderGraph: function (item, grid) {
            var self = this;
            var chart_data = JSON.parse(item.ks_chart_data);
            var isDrill = item.isDrill ? item.isDrill : false;
            var chart_id = item.id,
                chart_title = item.name;
            var chart_title = item.name;
            var chart_type = item.ks_dashboard_item_type.split('_')[1];
            switch (chart_type) {
                case "pie":
                case "doughnut":
                case "polarArea":
                    var chart_family = "circle";
                    break;
                case "bar":
                case "horizontalBar":
                case "line":
                case "area":
                    var chart_family = "square"
                    break;
                default:
                    var chart_family = "none";
                    break;
            }

            var $ks_gridstack_container = $(QWeb.render('ks_gridstack_container', {
                ks_chart_title: chart_title,
                ksIsDashboardManager: self.ks_dashboard_data.ks_dashboard_manager,
                ks_dashboard_list: self.ks_dashboard_data.ks_dashboard_list,
                chart_id: chart_id,
                chart_family: chart_family,
                chart_type: chart_type,
                item:item,
                ksChartColorOptions: this.ksChartColorOptions,
                isdrill: isDrill,
            })).addClass('ks_dashboarditem_id');
            $ks_gridstack_container.find('.ks_li_' + item.ks_chart_item_color).addClass('ks_date_filter_selected');
            if (chart_id in self.gridstackConfig) {
                grid.addWidget($ks_gridstack_container, self.gridstackConfig[chart_id].x, self.gridstackConfig[chart_id].y, self.gridstackConfig[chart_id].width, self.gridstackConfig[chart_id].height, false, 11, null, 3, null, chart_id);
            } else {
                grid.addWidget($ks_gridstack_container, 0, 0, 11, 4, true, 11, null, 3, null, chart_id);
            }
            self._renderChart($ks_gridstack_container,item);
        },

        _renderChart($ks_gridstack_container,item){
            var self = this;
            var chart_data = JSON.parse(item.ks_chart_data);
            var isDrill = item.isDrill ? item.isDrill : false;
            var chart_id = item.id,
                chart_title = item.name;
            var chart_title = item.name;
            var chart_type = item.ks_dashboard_item_type.split('_')[1];
            switch (chart_type) {
                case "pie":
                case "doughnut":
                case "polarArea":
                    var chart_family = "circle";
                    break;
                case "bar":
                case "horizontalBar":
                case "line":
                case "area":
                    var chart_family = "square"
                    break;
                default:
                    var chart_family = "none";
                    break;
            }
             $ks_gridstack_container.find('.ks_color_pallate').data({chartType:chart_type,chartFamily:chart_family});
            {chartType:"pie"}
            var $ksChartContainer = $('<canvas id="ks_chart_canvas_id" data-chart-id='+chart_id+'/>');
            $ks_gridstack_container.find('.card-body').append($ksChartContainer);

            item.$el = $ks_gridstack_container;
            if(chart_family === "circle"){
                if (chart_data && chart_data['labels'].length > 30){
                    $ks_gridstack_container.find(".ks_dashboard_color_option").remove();
                    $ks_gridstack_container.find(".card-body").empty().append($("<div style='font-size:18px;'>Too many records for selected Chart Type. Consider using <strong>Domain</strong> to filter records or <strong>Record Limit</strong> to limit the no of records under <strong>30.</strong>"));
                    return ;
                }
            }
            if(chart_data["ks_show_second_y_scale"] && item.ks_dashboard_item_type === 'ks_bar_chart'){
                var scales  = {}
                scales.yAxes = [
                    {
                        type: "linear",
                        display: true,
                        position: "left",
                        id: "y-axis-0",
                        gridLines:{
                            display: true,
                        },
                        labels: {
                            show:true,
                        },
                        ticks:{
                            autoSkip: false,
                        },
                    },
                    {
                        type: "linear",
                        display: true,
                        position: "right",
                        id: "y-axis-1",
                        labels: {
                            show:true,
                        },
                        ticks: {
                            autoSkip: false,
                            beginAtZero: true,
                            callback : function(value, index, values){
                                var ks_selection = chart_data.ks_selection;
                                if (ks_selection === 'monetary'){
                                    var ks_currency_id = chart_data.ks_currency;
                                    var ks_data = KsGlobalFunction.ksNumFormatter(value,1);
                                    ks_data = KsGlobalFunction.ks_monetary(ks_data, ks_currency_id);
                                    return ks_data;
                                }
                                else if (ks_selection === 'custom'){
                                    var ks_field = chart_data.ks_field;
                                    return KsGlobalFunction.ksNumFormatter(value,1) +' '+ ks_field;
                                }
                                else {
                                    return KsGlobalFunction.ksNumFormatter(value,1);
                                }
                            }
                        }
                    }
                ]

            }
            var chart_plugin = [];
            if (item.ks_show_data_value) {
                chart_plugin.push(ChartDataLabels);
            }
            var ksMyChart = new Chart($ksChartContainer[0], {
                type: chart_type === "area" ? "line" : chart_type,
                plugins: chart_plugin,
                data: {
                    labels: chart_data['labels'],
                    groupByIds:chart_data['groupByIds'],
                    domains:chart_data['domains'],
                    datasets: chart_data.datasets,
                },
                options: {
                    maintainAspectRatio: false,
                    responsiveAnimationDuration: 1000,
                    animation: {
                        easing: 'easeInQuad',
                    },
                    scales: scales,
                    layout: {
                        padding: {
                            bottom: 0,
                        }
                    },
                    plugins: {
                            datalabels: {
                                backgroundColor: function(context) {
                                    return context.dataset.backgroundColor;
                                },
                                borderRadius: 4,
                                color: 'white',
                                font: {
                                    weight: 'bold'
                                },
                                anchor: 'center',
                                display: 'auto',
                                clamp: true,
                                formatter : function(value, ctx) {
                                    let sum = 0;
                                    let dataArr = ctx.dataset.data;
                                    dataArr.map(data => {
                                        sum += data;
                                    });
                                    let percentage = sum === 0? 0  + "%" : (value*100 / sum).toFixed(2) + "%";
                                    return percentage;
                                },
                            },
                        },

                }
            });

            this.chart_container[chart_id] = ksMyChart;
            if(chart_data && chart_data["datasets"].length>0) self.ksChartColors(item.ks_chart_item_color, ksMyChart, chart_type, chart_family,item.ks_bar_chart_stacked,item.ks_semi_circle_chart,item.ks_show_data_value,chart_data);
        },

        ksChartColors: function (palette, ksMyChart, ksChartType, ksChartFamily,stack, semi_circle,ks_show_data_value,chart_data) {
            var self = this;
            var currentPalette = "cool";
            if (!palette) palette = currentPalette;
            currentPalette = palette;

            /*Gradients
              The keys are percentage and the values are the color in a rgba format.
              You can have as many "color stops" (%) as you like.
              0% and 100% is not optional.*/
            var gradient;
            switch (palette) {
                case 'cool':
                    gradient = {
                        0: [255, 255, 255, 1],
                        20: [220, 237, 200, 1],
                        45: [66, 179, 213, 1],
                        65: [26, 39, 62, 1],
                        100: [0, 0, 0, 1]
                    };
                    break;
                case 'warm':
                    gradient = {
                        0: [255, 255, 255, 1],
                        20: [254, 235, 101, 1],
                        45: [228, 82, 27, 1],
                        65: [77, 52, 47, 1],
                        100: [0, 0, 0, 1]
                    };
                    break;
                case 'neon':
                    gradient = {
                        0: [255, 255, 255, 1],
                        20: [255, 236, 179, 1],
                        45: [232, 82, 133, 1],
                        65: [106, 27, 154, 1],
                        100: [0, 0, 0, 1]
                    };
                    break;

                case 'default':
                    var color_set = ['#F04F65', '#f69032', '#fdc233', '#53cfce', '#36a2ec', '#8a79fd', '#b1b5be', '#1c425c', '#8c2620', '#71ecef', '#0b4295', '#f2e6ce', '#1379e7']
            }

            //Find datasets and length
            var chartType = ksMyChart.config.type;

            switch (chartType) {
                case "pie":
                case "doughnut":
                case "polarArea":
                    var datasets = ksMyChart.config.data.datasets[0];
                    var setsCount = datasets.data.length;
                    break;
                case "bar":
                case "horizontalBar":
                case "line":
                    var datasets = ksMyChart.config.data.datasets;
                    var setsCount = datasets.length;
                    break;
            }

            //Calculate colors
            var chartColors = [];

            if (palette !== "default") {
                //Get a sorted array of the gradient keys
                var gradientKeys = Object.keys(gradient);
                gradientKeys.sort(function (a, b) {
                    return +a - +b;
                });
                for (var i = 0; i < setsCount; i++) {
                    var gradientIndex = (i + 1) * (100 / (setsCount + 1)); //Find where to get a color from the gradient
                    for (var j = 0; j < gradientKeys.length; j++) {
                        var gradientKey = gradientKeys[j];
                        if (gradientIndex === +gradientKey) { //Exact match with a gradient key - just get that color
                            chartColors[i] = 'rgba(' + gradient[gradientKey].toString() + ')';
                            break;
                        } else if (gradientIndex < +gradientKey) { //It's somewhere between this gradient key and the previous
                            var prevKey = gradientKeys[j - 1];
                            var gradientPartIndex = (gradientIndex - prevKey) / (gradientKey - prevKey); //Calculate where
                            var color = [];
                            for (var k = 0; k < 4; k++) { //Loop through Red, Green, Blue and Alpha and calculate the correct color and opacity
                                color[k] = gradient[prevKey][k] - ((gradient[prevKey][k] - gradient[gradientKey][k]) * gradientPartIndex);
                                if (k < 3) color[k] = Math.round(color[k]);
                            }
                            chartColors[i] = 'rgba(' + color.toString() + ')';
                            break;
                        }
                    }
                }
            } else {
                for (var i = 0, counter = 0; i < setsCount; i++, counter++) {
                    if (counter >= color_set.length) counter = 0; // reset back to the beginning

                    chartColors.push(color_set[counter]);
                }
            }

            var datasets = ksMyChart.config.data.datasets;
            var options = ksMyChart.config.options;

            options.legend.labels.usePointStyle = true;
            if (ksChartFamily == "circle") {
                if(ks_show_data_value){
                    options.legend.position = 'bottom';
                    options.layout.padding.top = 10;
                    options.layout.padding.bottom = 20;
                    options.layout.padding.left = 20;
                    options.layout.padding.right = 20;
                }else{
                    options.legend.position = 'top';
                }


                options.plugins.datalabels.align = 'center';
                options.plugins.datalabels.anchor = 'end';
                options.plugins.datalabels.borderColor = 'white';
                options.plugins.datalabels.borderRadius = 25;
                options.plugins.datalabels.borderWidth = 2;
                options.plugins.datalabels.clamp = true;
                options.plugins.datalabels.clip = false;

                options.tooltips.callbacks = {
                                              title: function(tooltipItem, data) {
                                                    var ks_self = self;
                                                    var k_amount = data.datasets[tooltipItem[0].datasetIndex]['data'][tooltipItem[0].index];
                                                    var ks_selection = chart_data.ks_selection;
                                                    if (ks_selection === 'monetary'){
                                                        var ks_currency_id = chart_data.ks_currency;
                                                        k_amount = KsGlobalFunction.ks_monetary(k_amount, ks_currency_id);
                                                        return data.datasets[tooltipItem[0].datasetIndex]['label']+" : " + k_amount
                                                    }
                                                    else if (ks_selection === 'custom'){
                                                        var ks_field = chart_data.ks_field;
//                                                        ks_type = field_utils.format.char(ks_field);
                                                        k_amount = field_utils.format.float(k_amount,Float64Array);
                                                        return data.datasets[tooltipItem[0].datasetIndex]['label']+" : " + k_amount+" "+ ks_field;
                                                    }
                                                    else {
                                                        k_amount = field_utils.format.float(k_amount,Float64Array);
                                                        return data.datasets[tooltipItem[0].datasetIndex]['label']+" : " + k_amount
                                                    }
                                              },
                                              label : function(tooltipItem, data) {
                                                         return data.labels[tooltipItem.index];
                                                       },
                                              }
                for (var i = 0; i < datasets.length; i++) {
                    datasets[i].backgroundColor = chartColors;
                    datasets[i].borderColor = "rgba(255,255,255,1)";
                }
                if(semi_circle && (chartType === "pie" || chartType === "doughnut")){
                    options.rotation = 1*Math.PI;
                    options.circumference = 1*Math.PI;
                }
            } else if (ksChartFamily == "square") {
                options.scales.xAxes[0].gridLines.display = false;
                options.scales.yAxes[0].ticks.beginAtZero = true;

                options.plugins.datalabels.align = 'end';

                options.plugins.datalabels.formatter = function(value, ctx) {
                    var ks_selection = chart_data.ks_selection;
                    if (ks_selection === 'monetary'){
                        var ks_currency_id = chart_data.ks_currency;
                        var ks_data = KsGlobalFunction.ksNumFormatter(value,1);
                        ks_data = KsGlobalFunction.ks_monetary(ks_data, ks_currency_id);
                        return ks_data;
                    }
                    else if (ks_selection === 'custom'){
                        var ks_field = chart_data.ks_field;
                        return KsGlobalFunction.ksNumFormatter(value,1) +' '+ ks_field;
                    }
                    else {
                        return KsGlobalFunction.ksNumFormatter(value,1);
                    }
                };

                if(chartType==="line"){
                    options.plugins.datalabels.backgroundColor= function(context) {
                                    return context.dataset.borderColor;
                                };
                }

                if(chartType === "horizontalBar"){
                    options.scales.xAxes[0].ticks.callback = function(value,index,values){
                        var ks_selection = chart_data.ks_selection;
                        if (ks_selection === 'monetary'){
                            var ks_currency_id = chart_data.ks_currency;
                            var ks_data = KsGlobalFunction.ksNumFormatter(value,1);
                            ks_data = KsGlobalFunction.ks_monetary(ks_data, ks_currency_id);
                            return ks_data;
                        }
                        else if (ks_selection === 'custom'){
                            var ks_field = chart_data.ks_field;
                            return KsGlobalFunction.ksNumFormatter(value,1) +' '+ ks_field;
                        }
                        else {
                            return KsGlobalFunction.ksNumFormatter(value,1);
                        }
                    }
                    options.scales.xAxes[0].ticks.beginAtZero = true;
                }
                else{
                    options.scales.yAxes[0].ticks.callback = function(value,index,values){
                        var ks_selection = chart_data.ks_selection;
                        if (ks_selection === 'monetary'){
                            var ks_currency_id = chart_data.ks_currency;
                            var ks_data = KsGlobalFunction.ksNumFormatter(value,1);
                            ks_data = KsGlobalFunction.ks_monetary(ks_data, ks_currency_id);
                            return ks_data;
                        }
                        else if (ks_selection === 'custom'){
                            var ks_field = chart_data.ks_field;
                            return KsGlobalFunction.ksNumFormatter(value,1) +' '+ ks_field;
                        }
                        else {
                            return KsGlobalFunction.ksNumFormatter(value,1);
                        }
                    }
                }

                options.tooltips.callbacks = {
                    label: function(tooltipItem, data) {
                        var ks_self = self;
                        var k_amount = data.datasets[tooltipItem.datasetIndex]['data'][tooltipItem.index];
                        var ks_selection = chart_data.ks_selection;
                        if (ks_selection === 'monetary'){
                            var ks_currency_id = chart_data.ks_currency;
                            k_amount = KsGlobalFunction.ks_monetary(k_amount, ks_currency_id);
                            return data.datasets[tooltipItem.datasetIndex]['label']+" : " + k_amount
                        }
                        else if (ks_selection === 'custom'){
                            var ks_field = chart_data.ks_field;
                           // ks_type = field_utils.format.char(ks_field);
                            k_amount = field_utils.format.float(k_amount,Float64Array);
                            return data.datasets[tooltipItem.datasetIndex]['label']+" : " + k_amount+" "+ ks_field;
                        }
                        else {
                            k_amount = field_utils.format.float(k_amount,Float64Array);
                            return data.datasets[tooltipItem.datasetIndex]['label']+" : " + k_amount
                        }
                    }
                }

                for (var i = 0; i < datasets.length; i++) {
                    switch (ksChartType) {
                        case "bar":
                        case "horizontalBar":
                            if (datasets[i].type && datasets[i].type=="line"){
                                datasets[i].borderColor = chartColors[i];
                                datasets[i].backgroundColor = "rgba(255,255,255,0)";
                                datasets[i]['datalabels'] = {
                                    backgroundColor: chartColors[i],
                                }
                            }
                            else{
                                datasets[i].backgroundColor = chartColors[i];
                                datasets[i].borderColor = "rgba(255,255,255,0)";
                                options.scales.xAxes[0].stacked = stack;
                                options.scales.yAxes[0].stacked = stack;
                            }
                            break;
                        case "line":
                            datasets[i].borderColor = chartColors[i];
                            datasets[i].backgroundColor = "rgba(255,255,255,0)";
                            break;
                        case "area":
                            datasets[i].borderColor = chartColors[i];
                            break;
                    }
                }
            }
            ksMyChart.update();
        },

        onChartCanvasClick : function(evt){
            var self = this;
            var item_id = evt.currentTarget.dataset.chartId;
            if (item_id in self.ksUpdateDashboard) {
                clearInterval(self.ksUpdateDashboard[item_id])
            }
            var myChart = self.chart_container[item_id];
            var activePoint = myChart.getElementAtEvent(evt)[0];
            if (activePoint){
                var item_data = self.ks_dashboard_data.ks_item_data[item_id];
                var groupBy = item_data.ks_chart_groupby_type==='relational_type'?item_data.ks_chart_relation_groupby_name:item_data.ks_chart_relation_groupby_name+':'+item_data.ks_chart_date_groupby;

                if (activePoint._chart.data.domains){
                    var sequnce = item_data.sequnce ? item_data.sequnce : 0;
                    var domain = activePoint._chart.data.domains[activePoint._index]
                    if (item_data.max_sequnce != 0 && sequnce < item_data.max_sequnce){
                        self._rpc({
                            model:'ks_dashboard_ninja.item',
                            method:'ks_fetch_drill_down_data',
                            args:[item_id, domain, sequnce]
                        }).then(function(result){
                            self.ks_dashboard_data.ks_item_data[item_id]['ks_chart_data'] = result.ks_chart_data;
                            self.ks_dashboard_data.ks_item_data[item_id]['sequnce'] = result.sequence;
                            self.ks_dashboard_data.ks_item_data[item_id]['ks_dashboard_item_type']  = result.ks_chart_type;
                            self.ks_dashboard_data.ks_item_data[item_id]['isDrill'] = true;

                            if ('domains' in self.ks_dashboard_data.ks_item_data[item_id]){
                                self.ks_dashboard_data.ks_item_data[item_id]['domains'][result.sequence] = JSON.parse(result.ks_chart_data).previous_domain;
                            }
                            else {
                                self.ks_dashboard_data.ks_item_data[item_id]['domains'] = {}
                                self.ks_dashboard_data.ks_item_data[item_id]['domains'][result.sequence] = JSON.parse(result.ks_chart_data).previous_domain;
                            }
                           $(self.$el.find(".grid-stack-item[data-gs-id="+item_id+"]").children()[0]).find(".ks_dashboard_item_drill_up").removeClass('d-none');
                           $(self.$el.find(".grid-stack-item[data-gs-id="+item_id+"]").children()[0]).find(".ks_dashboard_quick_edit_action_popup").removeClass('ks_quick_button');

                            $(self.$el.find(".grid-stack-item[data-gs-id="+item_id+"]").children()[0]).find(".card-body").empty();
                            var item_data = self.ks_dashboard_data.ks_item_data[item_id]
                            self._renderChart($(self.$el.find(".grid-stack-item[data-gs-id="+item_id+"]").children()[0]),item_data);;
                        });
                    } else {
                        if(item_data.action){
                            var action = Object.assign({}, item_data.action);
                            if (action.view_mode.includes('tree')) action.view_mode = action.view_mode.replace('tree','list');
                            for (var i=0; i < action.views.length; i++) action.views[i][1].includes('tree') ? action.views[i][1] = action.views[i][1].replace('tree', 'list') : action.views[i][1] ;
                            action['domain'] = domain || [];
                        } else {
                            var action = {
                                name: _t(item_data.name),
                                type: 'ir.actions.act_window',
                                res_model: item_data.ks_model_name,
                                domain: domain || [],
                                context: {
                                    'group_by':groupBy,
                                },
                                views: [
                                    [false, 'list'],
                                    [false, 'form']
                                ],
                                view_mode: 'list',
                                target: 'current',
                            }
                        }
                        self.do_action(action, {
                                    on_reverse_breadcrumb: self.on_reverse_breadcrumb,
                                });
                    }
                }
            }
        },

        ksOnDrillUp : function(e){
            var self = this;
            var item_id = e.currentTarget.dataset.itemId;
            var item_data = self.ks_dashboard_data.ks_item_data[item_id];
            var domain = item_data['domains'][item_data.sequnce -  1]
            var sequnce = item_data.sequnce - 2;

            if(sequnce >= 0){
                self._rpc({
                            model:'ks_dashboard_ninja.item',
                            method:'ks_fetch_drill_down_data',
                            args:[item_id, domain, sequnce]
                        }).then(function(result){
                            self.ks_dashboard_data.ks_item_data[item_id]['ks_chart_data'] = result.ks_chart_data;
                            self.ks_dashboard_data.ks_item_data[item_id]['sequnce'] = result.sequence;
                            self.ks_dashboard_data.ks_item_data[item_id]['ks_dashboard_item_type']  = result.ks_chart_type;
                            $(self.$el.find(".grid-stack-item[data-gs-id="+item_id+"]").children()[0]).find(".ks_dashboard_item_drill_up").removeClass('d-none');
                            $(self.$el.find(".grid-stack-item[data-gs-id="+item_id+"]").children()[0]).find(".card-body").empty();
                            var item_data = self.ks_dashboard_data.ks_item_data[item_id]
                            self._renderChart($(self.$el.find(".grid-stack-item[data-gs-id="+item_id+"]").children()[0]),item_data);

                        });
            }
            else {
                 $(self.$el.find(".grid-stack-item[data-gs-id="+item_id+"]").children()[0]).find(".ks_dashboard_item_drill_up").addClass('d-none');
                 $(self.$el.find(".grid-stack-item[data-gs-id="+item_id+"]").children()[0]).find(".ks_dashboard_quick_edit_action_popup").addClass('ks_quick_button');
                 self.ksFetchChartItem(item_id);
                var updateValue = self.ks_dashboard_data.ks_item_data[item_id]["ks_update_items_data"];
                if (updateValue){
                    var updateinterval = setInterval(function(){self.ksFetchChartItem(item_id)}, updateValue);
                    self.ksUpdateDashboard[item_id] = updateinterval;
                }
            }
        },

        ksFetchChartItem: function(id){
            var self = this;
            var item_data = self.ks_dashboard_data.ks_item_data[id];

            return self._rpc({
                    model: 'ks_dashboard_ninja.board',
                    method: 'ks_fetch_item',
                    args: [[item_data.id], self.ks_dashboard_id],
                    context: self.getContext(),
                }).then(function(new_item_data){
                    this.ks_dashboard_data.ks_item_data[id] = new_item_data[id];
                    $(self.$el.find(".grid-stack-item[data-gs-id="+id+"]").children()[0]).find(".card-body").empty();
                    var item_data = self.ks_dashboard_data.ks_item_data[id]
                    self._renderChart($(self.$el.find(".grid-stack-item[data-gs-id="+id+"]").children()[0]),item_data);
                }.bind(this));
        },

        onChartMoreInfoClick : function(evt){
            var self = this;
            var item_id = evt.currentTarget.dataset.itemId;
            var item_data = self.ks_dashboard_data.ks_item_data[item_id];
            var groupBy = item_data.ks_chart_groupby_type==='relational_type'?item_data.ks_chart_relation_groupby_name:item_data.ks_chart_relation_groupby_name+':'+item_data.ks_chart_date_groupby;
            var domain = JSON.parse(item_data.ks_chart_data).previous_domain;
            if(item_data.action){
                var action = Object.assign({}, item_data.action);
                if (action.view_mode.includes('tree')) action.view_mode = action.view_mode.replace('tree','list');
                for (var i=0; i < action.views.length; i++) action.views[i][1].includes('tree') ? action.views[i][1] = action.views[i][1].replace('tree', 'list') : action.views[i][1] ;
                action['domain'] = domain || [];
            } else {
                var action = {
                    name: _t(item_data.name),
                    type: 'ir.actions.act_window',
                    res_model: item_data.ks_model_name,
                    domain: domain || [],
                    context: {
                        'group_by':groupBy,
                    },
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    view_mode: 'list',
                    target: 'current',
                }
            }

            self.do_action(action, {
                                on_reverse_breadcrumb: self.on_reverse_breadcrumb,
                            });

        },


        _ksRenderNoItemView: function () {
            $('.ks_dashboard_items_list').remove();
            var self = this;
            $(QWeb.render('ksNoItemView')).appendTo(self.$el)
        },

        _ksRenderEditMode: function () {
            var self = this;
            self.ksDashboardEditMode = true;
            self.ks_remove_update_interval();
            $('#ks_dashboard_title_input').val(self.ks_dashboard_data.name);

            $('.ks_am_element').addClass("ks_hide");
            $('.ks_em_element').removeClass("ks_hide");

            self.$el.find('.ks_item_click').addClass('ks_item_not_click').removeClass('ks_item_click');
            self.$el.find('.ks_dashboard_item').removeClass('ks_dashboard_item_header_hover');
            self.$el.find('.ks_dashboard_item_header').removeClass('ks_dashboard_item_header_hover');

            self.$el.find('.ks_dashboard_item_l2').removeClass('ks_dashboard_item_header_hover');
            self.$el.find('.ks_dashboard_item_header_l2').removeClass('ks_dashboard_item_header_hover');

            self.$el.find('.ks_dashboard_item_l5').removeClass('ks_dashboard_item_header_hover');

            self.$el.find('.ks_dashboard_item_button_container').removeClass('ks_dashboard_item_header_hover');

            self.$el.find('.ks_dashboard_link').addClass("ks_hide")
            self.$el.find('.ks_dashboard_top_settings').addClass("ks_hide")
            self.$el.find('.ks_dashboard_edit_mode_settings').removeClass("ks_hide")

            // Adding Chart grab able cals
            self.$el.find('.ks_chart_container').addClass('ks_item_not_click');
            self.$el.find('.ks_list_view_container').addClass('ks_item_not_click');

            if (self.grid) {
                self.grid.enable();
            }
        },


        _ksRenderActiveMode: function () {
            var self = this
            self.ksDashboardEditMode = false;
            if (self.grid) {
                $('.grid-stack').data('gridstack').disable();
            }

            $('#ks_dashboard_title_label').text(self.ks_dashboard_data.name);

            $('.ks_am_element').removeClass("ks_hide");
            $('.ks_em_element').addClass("ks_hide");
            if (self.ks_dashboard_data.ks_item_data) $('.ks_am_content_element').removeClass("ks_hide");

            self.$el.find('.ks_item_not_click').addClass('ks_item_click').removeClass('ks_item_not_click')
            self.$el.find('.ks_dashboard_item').addClass('ks_dashboard_item_header_hover')
            self.$el.find('.ks_dashboard_item_header').addClass('ks_dashboard_item_header_hover')

            self.$el.find('.ks_dashboard_item_l2').addClass('ks_dashboard_item_header_hover')
            self.$el.find('.ks_dashboard_item_header_l2').addClass('ks_dashboard_item_header_hover')

            //      For layout 5
            self.$el.find('.ks_dashboard_item_l5').addClass('ks_dashboard_item_header_hover')


            self.$el.find('.ks_dashboard_item_button_container').addClass('ks_dashboard_item_header_hover');

            self.$el.find('.ks_dashboard_top_settings').removeClass("ks_hide")
            self.$el.find('.ks_dashboard_edit_mode_settings').addClass("ks_hide")

            self.$el.find('.ks_chart_container').removeClass('ks_item_not_click ks_item_click');
            self.ks_set_update_interval();
        },

        _ksToggleEditMode: function () {
            var self = this
            if (self.ksDashboardEditMode) {
                self._ksRenderActiveMode()
                self.ksDashboardEditMode = false
            } else if (!self.ksDashboardEditMode) {
                self._ksRenderEditMode()
                self.ksDashboardEditMode = true
            }

        },

        onAddItemTypeClick : function(e){
            var self = this;

            self.do_action({
                type: 'ir.actions.act_window',
                res_model: 'ks_dashboard_ninja.item',
                view_id: 'ks_dashboard_ninja_list_form_view',
                views: [
                    [false, 'form']
                ],
                target: 'current',
                context: {
                    'ks_dashboard_id': self.ks_dashboard_id,
                    'ks_dashboard_item_type':e.currentTarget.dataset.item,
                    'form_view_ref':'ks_dashboard_ninja.item_form_view',
                    'form_view_initial_mode': 'edit',
                     'ks_set_interval': self.ks_dashboard_data.ks_set_interval,
                },
            }, {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            });

        },

        _onKsAddLayoutClick: function () {
            var self = this;

            self.do_action({
                type: 'ir.actions.act_window',
                res_model: 'ks_dashboard_ninja.item',
                view_id: 'ks_dashboard_ninja_list_form_view',
                views: [
                    [false, 'form']
                ],
                target: 'current',
                context: {
                    'ks_dashboard_id': self.ks_dashboard_id,
                    'form_view_ref':'ks_dashboard_ninja.item_form_view',
                    'form_view_initial_mode': 'edit',
                },
            }, {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            });
        },

        _onKsEditLayoutClick: function () {
            var self = this;
            self._ksRenderEditMode();
        },

        //TODO: Remove this or Use this
        onKsSelectItemClick: function () {},

        _onKsSaveLayoutClick: function () {
            var self = this;
            //        Have  to save dashboard here
            var dashboard_title = $('#ks_dashboard_title_input').val();

            if (dashboard_title != false && dashboard_title != 0 && dashboard_title !== self.ks_dashboard_data.name) {
                self.ks_dashboard_data.name = dashboard_title;
                this._rpc({
                    model: 'ks_dashboard_ninja.board',
                    method: 'write',
                    args: [self.ks_dashboard_id, {
                        'name': dashboard_title
                    }],
                })
            }
            if(this.ks_dashboard_data.ks_item_data) self._ksSaveCurrentLayout();
            self._ksRenderActiveMode();

        },

        _onKsCancelLayoutClick: function () {
            var self = this;

             //        render page again
            $.when(self.ks_fetch_data()).then(function () {
                self.ksRenderDashboard();
                self.ks_set_update_interval();
            });
        },

        _onKsItemClick: function (e) {
            var self = this;

            // To Handle only allow item to open when not clicking on item
            if (self.ksAllowItemClick) {
                e.preventDefault();
                if (e.target.title != "Customize Item") {

                    var item_id = parseInt(e.currentTarget.firstElementChild.id);
                    if(!item_id) item_id = parseInt($($(e.currentTarget).parentsUntil('.grid-stack').slice(-1)[0]).attr('data-gs-id'));
                    var item_data = self.ks_dashboard_data.ks_item_data[item_id];

                    if(item_data.action){
                        var action = Object.assign(item_data.action, {});
                        if (action.view_mode.includes('tree')) action.view_mode = action.view_mode.replace('tree','list');
                        for (var i=0; i < action.views.length; i++) action.views[i][1].includes('tree') ? action.views[i][1] = action.views[i][1].replace('tree', 'list') : action.views[i][1] ;
                        action['domain'] = item_data.ks_domain || [];
                    } else {
                        var action = {
                            name: _t(item_data.name),
                            type: 'ir.actions.act_window',
                            res_model: item_data.ks_model_name,
                            domain: item_data.ks_domain || "[]",
                            views: [
                                [false, 'list'],
                                [false, 'form']
                            ],
                            view_mode: 'list',
                            target: 'current',
                        }
                    }
                    self.do_action(action, {
                        on_reverse_breadcrumb: self.on_reverse_breadcrumb,
                    });
                }
            } else {
                self.ksAllowItemClick = true;
            }
        },

       _onKsItemCustomizeClick: function (e) {
            var self = this;
            var id = parseInt($($(e.currentTarget).parentsUntil('.grid-stack').slice(-1)[0]).attr('data-gs-id'))

            self.ks_open_item_form_page(id);
            e.stopPropagation();
       },

       ks_open_item_form_page: function (id) {
           var self = this;
           self.do_action({
               type: 'ir.actions.act_window',
               res_model: 'ks_dashboard_ninja.item',
               view_id: 'ks_dashboard_ninja_list_form_view',
               views: [
                   [false, 'form']
               ],
               target: 'current',
               context: {
                   'form_view_ref':'ks_dashboard_ninja.item_form_view',
                   'form_view_initial_mode': 'edit',
               },
               res_id: id
           }, {
               on_reverse_breadcrumb: this.on_reverse_breadcrumb,
           });
       },

       ksFetchUpdateItem: function(id){
           var self = this;
           var item_data = self.ks_dashboard_data.ks_item_data[id];
           if(!item_data){
                if (id in self.ksUpdateDashboard){
                    clearInterval(self.ksUpdateDashboard[id]);
                }
           } else{
                return self._rpc({
                        model: 'ks_dashboard_ninja.board',
                        method: 'ks_fetch_item',
                        args: [[item_data.id], self.ks_dashboard_id],
                        context: self.getContext(),
                    }).then(function(new_item_data){
                        this.ks_dashboard_data.ks_item_data[item_data.id] = new_item_data[item_data.id];
                        this.ksUpdateDashboardItem([item_data.id]);
                    }.bind(this));
           }
       },

        _onKsDeleteItemClick: function (e) {
            var self = this;
            var item = $($(e.currentTarget).parentsUntil('.grid-stack').slice(-1)[0])
            var id = parseInt($($(e.currentTarget).parentsUntil('.grid-stack').slice(-1)[0]).attr('data-gs-id'));
            self.ks_delete_item(id, item);
            e.stopPropagation();
        },

        ks_delete_item: function (id, item) {
            var self = this;
            Dialog.confirm(this, (_t("Are you sure you want to remove this item?")), {
                confirm_callback: function () {

                    self._rpc({
                        model: 'ks_dashboard_ninja.item',
                        method: 'unlink',
                        args: [id],
                    }).then(function (data) {
                        self.grid.removeWidget(item);
                        self.ks_remove_update_interval();
                        delete self.ks_dashboard_data.ks_item_data[id]
                        self.ks_set_update_interval();
                        if(self.ks_dashboard_data.ks_item_data) self._ksSaveCurrentLayout();
                    });
                },
            });

        },

        _ksSaveCurrentLayout: function () {
            var self = this;
            if ($('.grid-stack').data('gridstack')){
                var items = $('.grid-stack').data('gridstack').grid.nodes;
                var grid_config = {}
                for (var i = 0; i < items.length; i++) {
                    grid_config[items[i].id] = {
                        'x': items[i].x,
                        'y': items[i].y,
                        'width': items[i].width,
                        'height': items[i].height
                    }
                }
                self.ks_dashboard_data.ks_gridstack_config = JSON.stringify(grid_config);
                this._rpc({
                    model: 'ks_dashboard_ninja.board',
                    method: 'write',
                    args: [self.ks_dashboard_id, {
                        "ks_gridstack_config": JSON.stringify(grid_config)
                    }],
                });
            }
        },

        _ksSaveCurrentLayoutLocally: function () {
            var self = this;
            if ($('.grid-stack').data('gridstack')){
                var items = $('.grid-stack').data('gridstack').grid.nodes;
                var grid_config = {}
                for (var i = 0; i < items.length; i++) {
                    grid_config[items[i].id] = {
                        'x': items[i].x,
                        'y': items[i].y,
                        'width': items[i].width,
                        'height': items[i].height
                    }
                }

                self.ks_dashboard_data.ks_gridstack_config = JSON.stringify(grid_config);
            }
        },

        _renderListView: function (item, grid) {
           var self = this;
            var list_view_data = JSON.parse(item.ks_list_view_data);
            var item_id = item.id,
                item_title = item.name;
           var $ksItemContainer = self.renderListViewData(item)
            var $ks_gridstack_container = $(QWeb.render('ks_gridstack_list_view_container', {
                ks_chart_title: item_title,
                ksIsDashboardManager: self.ks_dashboard_data.ks_dashboard_manager,
                ks_dashboard_list: self.ks_dashboard_data.ks_dashboard_list,
                item: item,
            })).attr("id", item_id).addClass('ks_dashboarditem_id');

            $ks_gridstack_container.find('.card-body').append($ksItemContainer);

            if (item_id in self.gridstackConfig) {
                grid.addWidget($ks_gridstack_container, self.gridstackConfig[item_id].x, self.gridstackConfig[item_id].y, self.gridstackConfig[item_id].width, self.gridstackConfig[item_id].height, false, 9, null, 3, null, item_id);
            } else {
                grid.addWidget($ks_gridstack_container, 0, 0, 13, 4, true, 9, null, 3, null, item_id);
            }
        },
        renderListViewData(item){
            var self = this;
            var list_view_data = JSON.parse(item.ks_list_view_data);
            var item_id = item.id,
                item_title = item.name;

            if(list_view_data){
                for (var i = 0; i < list_view_data.data_rows.length; i++){
                    for (var j = 0; j < list_view_data.data_rows[0]["data"].length; j++){
                        if(typeof(list_view_data.data_rows[i].data[j]) === "number" || list_view_data.data_rows[i].data[j]){
                            if(typeof(list_view_data.data_rows[i].data[j]) === "number"){
                                list_view_data.data_rows[i].data[j]  = field_utils.format.float(list_view_data.data_rows[i].data[j], Float64Array)
                            }
                        } else {
                            list_view_data.data_rows[i].data[j] = "";
                        }
                    }
                }
            }

            if(item.ks_list_view_type === "ungrouped" && list_view_data){
                var index_data = list_view_data.date_index;
                for (var i = 0; i < index_data.length; i++){
                    for (var j = 0; j < list_view_data.data_rows.length; j++){
                        var index = index_data[i]
                        var date = list_view_data.data_rows[j]["data"][index]
                        if (date) list_view_data.data_rows[j]["data"][index] = field_utils.format.datetime(moment(moment(date).utc(true)._d), {}, {timezone: false});
                        else list_view_data.data_rows[j]["data"][index] = "";
                    }
                }
            }



            var $ksItemContainer = $(QWeb.render('ks_list_view_table', {
                list_view_data: list_view_data,
                item_id:item.id,
            }));
            return $ksItemContainer
        },


        renderKpi : function(item){
            var self = this;
            var field =  item;
            var ks_date_filter_selection = field.ks_date_filter_selection;
            if (field.ks_date_filter_selection==="l_none") ks_date_filter_selection = self.ks_dashboard_data.ks_date_filter_selection;
            var ks_valid_date_selection = ['l_day','t_week','t_month','t_quarter','t_year'];
            var kpi_data = JSON.parse(field.ks_kpi_data);
            var count_1 = kpi_data[0].record_data;
            var count_2 = kpi_data[1]?kpi_data[1].record_data: undefined;
            var target_1 = kpi_data[0].target;
            var target_view = field.ks_target_view,
                pre_view =  field.ks_prev_view;
            var ks_rgba_background_color = self._ks_get_rgba_format(field.ks_background_color);
            var ks_rgba_font_color = self._ks_get_rgba_format(field.ks_font_color)
            if(field.ks_goal_enable){
                var diffrence = 0.0
                diffrence = count_1 - target_1
                var acheive = diffrence>=0 ? true : false;
                diffrence =  Math.abs(diffrence);
                var deviation = Math.round((diffrence/target_1)*100)
                if (deviation!==Infinity)  deviation = deviation? field_utils.format.integer(deviation) + '%' : 0 + '%';
            }
            if(field.ks_previous_period && ks_valid_date_selection.indexOf(ks_date_filter_selection)>=0){
                var previous_period_data = kpi_data[0].previous_period;
                var pre_diffrence = (count_1 - previous_period_data);
                var pre_acheive = pre_diffrence>0 ? true : false;
                pre_diffrence = Math.abs(pre_diffrence);
                var pre_deviation = previous_period_data ? field_utils.format.integer(parseInt((pre_diffrence/previous_period_data)*100)) + '%' : "100%"
            }
            var item = {
                ksIsDashboardManager : self.ks_dashboard_data.ks_dashboard_manager,
                id : field.id,
            }
            var ks_icon_url;
            if (field.ks_icon_select == "Custom") {
                if (field.ks_icon[0]) {
                    ks_icon_url = 'data:image/' + (self.file_type_magic_word[field.ks_icon[0]] || 'png') + ';base64,' + field.ks_icon;
                } else {
                    ks_icon_url = false;
                }
            }
            var ks_rgba_icon_color = self._ks_get_rgba_format(field.ks_default_icon_color)
            var item_info = {
                item : item,
                id: field.id,
                count_1 : self.ksNumFormatter(kpi_data[0]['record_data'], 1),
                count_1_tooltip: kpi_data[0]['record_data'],
                count_2 : kpi_data[1] ? String(kpi_data[1]['record_data']):false ,
                name : field.name ? field.name : field.ks_model_id.data.display_name,
                target_progress_deviation : Math.round((count_1/target_1)*100) && Math.round((count_1/target_1)*100) !== Infinity ?String(field_utils.format.integer(Math.round((count_1/target_1)*100))):"0",
                icon_select : field.ks_icon_select,
                default_icon: field.ks_default_icon,
                icon_color: ks_rgba_icon_color,
                target_deviation: deviation,
                target_arrow: acheive ? 'up':'down',
                ks_enable_goal: field.ks_goal_enable,
                ks_previous_period: ks_valid_date_selection.indexOf(ks_date_filter_selection)>=0 ? field.ks_previous_period: false,
                target: self.ksNumFormatter(target_1, 1),
                target_tooltip: target_1,
                previous_period_data: previous_period_data,
                pre_deviation: pre_deviation,
                pre_arrow : pre_acheive ? 'up':'down',
                target_view : field.ks_target_view,
                pre_view : field.ks_prev_view,
                ks_dashboard_list: self.ks_dashboard_data.ks_dashboard_list,
                ks_icon_url: ks_icon_url,
            }

            if (item_info.target_deviation===Infinity) item_info.target_arrow = false;

            var $kpi_preview;
            if(!kpi_data[1]){
                if(field.ks_target_view ==="Number" || !field.ks_goal_enable) {
                    $kpi_preview = $(QWeb.render("ks_kpi_template",item_info));
                }
                else if (field.ks_target_view === "Progress Bar" && field.ks_goal_enable){
                    $kpi_preview = $(QWeb.render("ks_kpi_template_3",item_info));
                    $kpi_preview.find('#ks_progressbar').val(parseInt(item_info.target_progress_deviation));

                }

                if(field.ks_goal_enable){
                    if(acheive){
                        $kpi_preview.find(".target_deviation").css({
                            "color" : "green",
                        });
                    }else{
                      $kpi_preview.find(".target_deviation").css({
                            "color" : "red",
                        });
                    }
                }
                if(field.ks_previous_period && String(previous_period_data) && ks_valid_date_selection.indexOf(ks_date_filter_selection)>=0){
                    if(pre_acheive){
                        $kpi_preview.find(".pre_deviation").css({
                            "color" : "green",
                        });
                    }else{
                      $kpi_preview.find(".pre_deviation").css({
                            "color" : "red",
                        });
                    }
                }
                if($kpi_preview.find('.ks_target_previous').children().length !== 2){
                    $($kpi_preview.find('.ks_target_previous').children()[0]).addClass('ks_text_center');
                    $kpi_preview.find('.ks_target_previous').children().css({"width": "100%"});
                }
            }
            else{
                switch(field.ks_data_comparison){
                    case "None":
                        var count_tooltip = String(count_1)+"/"+String(count_2);
                        var count = String(self.ksNumFormatter(count_1,1))+"/"+String(self.ksNumFormatter(count_2,1));
                        item_info['count'] = count;
                        item_info['count_tooltip'] = count_tooltip;
                        item_info['target_enable'] = false;
                         $kpi_preview = $(QWeb.render("ks_kpi_template_2",item_info));
                        break;
                    case "Sum":
                        var count = count_1 + count_2
                        item_info['count'] = self.ksNumFormatter(count, 1);
                        item_info['count_tooltip'] = count;
                        item_info['target_enable'] = field.ks_goal_enable;
                        var ks_color = (target_1-count)>0? "red" : "green";
                        item_info.pre_arrow = (target_1-count)>0? "down" : "up";
                        item_info['ks_comparison'] = true;
                        var target_deviation = (target_1-count)>0? Math.round(((target_1-count)/target_1)*100) : Math.round((Math.abs((target_1-count))/target_1)*100);
                        if (target_deviation!==Infinity)  item_info.target_deviation = field_utils.format.integer(target_deviation) + "%";
                        else {
                            item_info.target_deviation = target_deviation;
                            item_info.pre_arrow = false;
                        }
                        var target_progress_deviation = target_1 ? Math.round((count/target_1)*100) : 0;
                        item_info.target_progress_deviation = field_utils.format.integer(target_progress_deviation) + "%";
                        $kpi_preview = $(QWeb.render("ks_kpi_template_2",item_info));
                        $kpi_preview.find('.target_deviation').css({
                            "color":ks_color
                        });
                        if(field.ks_target_view === "Progress Bar"){
                            $kpi_preview.find('#ks_progressbar').val(target_progress_deviation)
                        }
                        break;
                    case "Percentage":
                        var count = parseInt((count_1/count_2)*100);
                        item_info['count'] = count ? field_utils.format.integer(count, 1)+"%" : "0%";
                        item_info['count_tooltip'] = count ? count+"%" : "0%";
                        item_info.target_progress_deviation = item_info['count']
                        target_1 = target_1 > 100 ? 100 : target_1;
                        item_info.target = target_1 + "%";
                        item_info.target_tooltip = target_1 + "%";
                        item_info.pre_arrow = (target_1-count)>0? "down" : "up";
                        var ks_color = (target_1-count)>0? "red" : "green";
                        item_info['target_enable'] = field.ks_goal_enable;
                        item_info['ks_comparison'] = false;
                        item_info.target_deviation = item_info.target > 100 ? 100 : item_info.target;
                         $kpi_preview = $(QWeb.render("ks_kpi_template_2",item_info));
                        $kpi_preview.find('.target_deviation').css({
                            "color":ks_color
                        });
                        if(field.ks_target_view === "Progress Bar"){
                            if(count) $kpi_preview.find('#ks_progressbar').val(count);
                            else $kpi_preview.find('#ks_progressbar').val(0);
                        }
                        break;
                    case "Ratio":
                        var gcd = self.ks_get_gcd(Math.round(count_1),Math.round(count_2));
                        item_info['count'] =  (isNaN(count_1/gcd)?0:self.ksNumFormatter(count_1/gcd, 1)) + ":" + (isNaN(count_2/gcd)?0:self.ksNumFormatter(count_2/gcd, 1));
                        item_info['count_tooltip'] =  (isNaN(count_1/gcd)?0:count_1/gcd) + ":" + (isNaN(count_2/gcd)?0:count_2/gcd);
                        item_info['target_enable'] = false;
                         $kpi_preview = $(QWeb.render("ks_kpi_template_2",item_info));
                        break;
                }
            }
            $kpi_preview.find('.ks_dashboarditem_id').css({
                "background-color" : ks_rgba_background_color,
                "color":ks_rgba_font_color,
            });
            return $kpi_preview
        },

        ks_get_gcd : function(a, b) {
            return (b == 0) ? a : this.ks_get_gcd(b, a%b);
        },

        _onKsInputChange: function (e) {
            this.ksNewDashboardName = e.target.value
        },

        onKsDuplicateItemClick: function (e) {
            $('.ks_dashboard_menu_container').hide();
            var self = this;
            var ks_item_id = $($(e.target).parentsUntil(".ks_dashboarditem_id").slice(-1)[0]).parent().attr('id')
            var dashboard_id = $($(e.target).parentsUntil(".ks_dashboarditem_id").slice(-1)[0]).find('.ks_dashboard_select option:selected').val()
            var dashboard_name = $($(e.target).parentsUntil(".ks_dashboarditem_id").slice(-1)[0]).find('.ks_dashboard_select option:selected').text()
            self.ks_remove_update_interval();
            this._rpc({
                model: 'ks_dashboard_ninja.item',
                method: 'copy',
                args: [parseInt(ks_item_id), {
                    'ks_dashboard_ninja_board_id': parseInt(dashboard_id)
                }],
            }).then(function (result) {
                self.do_notify(
                    _t("Item Duplicated"),
                    _t('Selected item is duplicated to '+dashboard_name+' .')
                );
                $.when(self.ks_fetch_data()).then(function () {
                    self.ksRenderDashboard();
                });
            })
        },

        ksOnListItemInfoClick: function (e) {
            var self = this;
            var item_id = e.currentTarget.dataset.itemId;
            var item_data = self.ks_dashboard_data.ks_item_data[item_id];
            var action = {
                    name: _t(item_data.name),
                    type: 'ir.actions.act_window',
                    res_model: e.currentTarget.dataset.model,
                    domain: item_data.ks_domain || [],
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    target: 'current',
                }
            if(e.currentTarget.dataset.listType==="none"){
                action['view_mode'] = 'form';
                action['views'] = [[false, 'form']];
                action['res_id'] = parseInt(e.currentTarget.dataset.recordId);
            }else if(e.currentTarget.dataset.listType==="date_type"){
                action['view_mode'] = 'list';
                action['context'] = {
                                        'group_by':e.currentTarget.dataset.groupby,
                                    };
            }else if(e.currentTarget.dataset.listType==="relational_type"){
                action['view_mode'] = 'list';
                action['context'] = {
                                        'group_by':e.currentTarget.dataset.groupby,
                                    };
                action['context']['search_default_'+e.currentTarget.dataset.groupby] = parseInt(e.currentTarget.dataset.recordId);
            }
            self.do_action(action,{
                    on_reverse_breadcrumb: this.on_reverse_breadcrumb,
                });

        },

        onKsMoveItemClick: function (e) {
            $('.ks_dashboard_menu_container').hide();
            var self = this;
            var ks_item_id = $($(e.target).parentsUntil(".ks_dashboarditem_id").slice(-1)[0]).parent().attr('id')
            var dashboard_id = $($(e.target).parentsUntil(".ks_dashboarditem_id").slice(-1)[0]).find('.ks_dashboard_select option:selected').val()
            var dashboard_name = $($(e.target).parentsUntil(".ks_dashboarditem_id").slice(-1)[0]).find('.ks_dashboard_select option:selected').text()

            this._rpc({
                model: 'ks_dashboard_ninja.item',
                method: 'write',
                args: [parseInt(ks_item_id), {
                    'ks_dashboard_ninja_board_id': parseInt(dashboard_id)
                }],
            }).then(function (result) {
                self.do_notify(
                    _t("Item Moved"),
                    _t('Selected item is moved to '+dashboard_name+' .')
                );
                 self.ks_remove_update_interval();
                $.when(self.ks_fetch_data()).then(function () {
                    self.ksRenderDashboard();
                    self.ks_set_update_interval();
                });
            })
        },

        _KsGetDateValues: function () {
            var self = this;

            //Setting Date Filter Selected Option in Date Filter DropDown Menu
            var date_filter_selected = self.ks_dashboard_data.ks_date_filter_selection;
            self.$el.find('#' + date_filter_selected).addClass("ks_date_filter_selected");
            self.$el.find('#ks_date_filter_selection').text(self.ks_date_filter_selections[date_filter_selected]);

            if (self.ks_dashboard_data.ks_date_filter_selection === 'l_custom') {
                self.$el.find('.ks_date_input_fields').removeClass("ks_hide");
                self.$el.find('.ks_date_filter_dropdown').addClass("ks_btn_first_child_radius");
            } else if (self.ks_dashboard_data.ks_date_filter_selection !== 'l_custom') {
                self.$el.find('.ks_date_input_fields').addClass("ks_hide");
            }

        },

        _onKsClearDateValues: function () {
            var self = this;

            self.ksDateFilterSelection = 'l_none';
            self.ksDateFilterStartDate = false;
            self.ksDateFilterEndDate = false;

           $.when(self.ks_fetch_data()).then(function () {
                self.ksRenderDashboard();
           });
        },


        _renderDateFilterDatePicker: function () {
            var self = this;
            self.$el.find(".ks_dashboard_link").removeClass("ks_hide");
            var startDate = self.ks_dashboard_data.ks_dashboard_start_date ? moment.utc(self.ks_dashboard_data.ks_dashboard_start_date).local() : moment();
            var endDate = self.ks_dashboard_data.ks_dashboard_end_date ? moment.utc(self.ks_dashboard_data.ks_dashboard_end_date).local() : moment();



            this.ksStartDatePickerWidget = new (datepicker.DateTimeWidget)(this);
            this.ksStartDatePickerWidget.appendTo(self.$el.find(".ks_date_input_fields")).then((function () {
                this.ksStartDatePickerWidget.$el.addClass("ks_btn_middle_child o_input");
                this.ksStartDatePickerWidget.$el.find("input").attr("placeholder", "Start Date");
                this.ksStartDatePickerWidget.setValue(startDate);
                this.ksStartDatePickerWidget.on("datetime_changed", this, function () {
                    self.$el.find(".apply-dashboard-date-filter").removeClass("ks_hide");
                    self.$el.find(".clear-dashboard-date-filter").removeClass("ks_hide");
                });
            }).bind(this));

            this.ksEndDatePickerWidget = new (datepicker.DateTimeWidget)(this);
            this.ksEndDatePickerWidget.appendTo(self.$el.find(".ks_date_input_fields")).then((function () {
                this.ksEndDatePickerWidget.$el.addClass("ks_btn_last_child o_input");
                this.ksStartDatePickerWidget.$el.find("input").attr("placeholder", "Start Date");
                this.ksEndDatePickerWidget.setValue(endDate);
                this.ksEndDatePickerWidget.on("datetime_changed", this, function () {
                    self.$el.find(".apply-dashboard-date-filter").removeClass("ks_hide");
                    self.$el.find(".clear-dashboard-date-filter").removeClass("ks_hide");
                });
            }).bind(this));

            self._KsGetDateValues();
        },

        _onKsApplyDateFilter: function (e) {
            var self = this;

            var start_date = self.ksStartDatePickerWidget.getValue();
            var end_date = self.ksEndDatePickerWidget.getValue();
            if (start_date === "Invalid date") {
                alert("Invalid Date is given in Start Date.")
            } else if (end_date === "Invalid date") {
                alert("Invalid Date is given in End Date.")
            } else if (self.$el.find('.ks_date_filter_selected').attr('id') !== "l_custom") {

                self.ksDateFilterSelection = self.$el.find('.ks_date_filter_selected').attr('id');

                $.when(self.ks_fetch_data()).then(function () {
                           self.ksUpdateDashboardItem(Object.keys(self.ks_dashboard_data.ks_item_data));
                        });
            } else {
                if (start_date && end_date) {
                    if (start_date <= end_date) {

                        self.ksDateFilterSelection = self.$el.find('.ks_date_filter_selected').attr('id');
                        self.ksDateFilterStartDate = start_date.add(-this.getSession().getTZOffset(start_date), 'minutes');
                        self.ksDateFilterEndDate = end_date.add(-this.getSession().getTZOffset(start_date), 'minutes');

                        $.when(self.ks_fetch_data()).then(function () {

                               self.ksRenderDashboard();
                        });
                    } else {
                        alert(_t("Start date should be less than end date"));
                    }
                } else {
                    alert(_t("Please enter start date and end date"));
                }
            }
        },

        _ksOnDateFilterMenuSelect: function (e) {
            if (e.target.id !== 'ks_date_selector_container') {
                var self = this;
                _.each($('.ks_date_filter_selected'), function ($filter_options) {
                    $($filter_options).removeClass("ks_date_filter_selected")
                });
                $(e.target.parentElement).addClass("ks_date_filter_selected");
                $('#ks_date_filter_selection').text(self.ks_date_filter_selections[e.target.parentElement.id]);

                if (e.target.parentElement.id !== "l_custom") {
                    $('.ks_date_input_fields').addClass("ks_hide");
                    $('.ks_date_filter_dropdown').removeClass("ks_btn_first_child_radius");
                    e.target.parentElement.id === "l_none" ? self._onKsClearDateValues() : self._onKsApplyDateFilter();
                } else if (e.target.parentElement.id === "l_custom") {
                    $("#ks_start_date_picker").val(null).removeClass("ks_hide");
                    $("#ks_end_date_picker").val(null).removeClass("ks_hide");
                    $('.ks_date_input_fields').removeClass("ks_hide");
                    $('.ks_date_filter_dropdown').addClass("ks_btn_first_child_radius");
                    self.$el.find(".apply-dashboard-date-filter").removeClass("ks_hide");
                    self.$el.find(".clear-dashboard-date-filter").removeClass("ks_hide");
                }
            }
        },

        ksChartExportXLS : function(e){
           var chart_id = e.currentTarget.dataset.chartId;
           var name = this.ks_dashboard_data.ks_item_data[chart_id].name;
           var data = {
                        "header":name,
                        "chart_data":this.ks_dashboard_data.ks_item_data[chart_id].ks_chart_data,
                      }
                framework.blockUI();
                this.getSession().get_file({
                    url: '/ks_dashboard_ninja/export/'+e.currentTarget.dataset.format,
                    data: {data:JSON.stringify(data)},
                    complete: framework.unblockUI,
                    error: crash_manager.rpc_error.bind(crash_manager),
                });
        },

        ksChartExportPdf : function(e){
            var chart_id = e.currentTarget.dataset.chartId;
            var name = this.ks_dashboard_data.ks_item_data[chart_id].name;
            var base64_image = this.chart_container[chart_id].toBase64Image();
            var doc = new jsPDF('p', 'mm');
            doc.addImage(base64_image, 'PNG', 5, 10, 200, 0);
            doc.save(name);
        },
    });

    core.action_registry.add('ks_dashboard_ninja', KsDashboardNinja);

    return KsDashboardNinja;
});