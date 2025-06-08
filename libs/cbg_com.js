'use strict';
(function(win) {
    if (win.CBG) {
        return;
    }
    var CONSTANTS = {
        STORAGE_TYPE: {
            EQUIP: 1,
            PET: 2,
            MONEY: 3,
            ROLE: 4
        },
        EQUIP: {
            TAKE_BACK: 0,
            STORE: 1,
            SELLING: 2,
            BOOKING: 3,
            PAID: 4,
            TRADE_FINISH: 5,
            TAKE_AWAY: 6,
            PROBLEM_TRADE: 7
        },
        EQUIP_STATUS: {
            0: "卖家取回",
            1: "未上架",
            2: "上架中",
            3: "被下单",
            4: "已售出",
            5: "已售出",
            6: "买家取走",
            7: "问题物品"
        },
        ORDER: {
            NO_PAY: 1,
            PAIED: 2,
            CANCEL: 3,
            EXPIRED: 4,
            REFUNDMENT: 5,
            SUCCESS: 6,
            REFUNDMENT_FINISH: 7
        },
        ORDER_STATUS: {
            1: "待付款",
            2: "已付款",
            3: "已废除",
            4: "过期",
            5: "退款中",
            6: "已售出",
            7: "已退款"
        },
        INSTALMENT: {
            PENDING: 0,
            STARTED: 1,
            FINISHED: 2,
            FORFEITED_PENDING: 3,
            FORFEITED_FINISH: 4,
            ABORT_REFUND: 5,
            ABORT_REFUND_FINISH: 6,
            CANCELED: 7,
            SUCCESS: 8
        },
        INSTALMENT_STATUS: {
            0: "待付款",
            1: "待付尾款",
            2: "已付款",
            3: "订金扣除",
            4: "订金扣除",
            5: "退款中",
            6: "退款完成",
            7: "已取消分期付",
            8: "已付款"
        }
    };
    var AjaxConstants = {
        Failed: 0,
        Ok: 1,
        Error: 2
    };
    function fen2yuan(fen) {
        return (fen / 100).toFixed(2);
    }
    function yuan2fen(yuan) {
        return Math.round(parseFloat(yuan) * 100);
    }
    function noop() {}
    function htmlEncode(s) {
        var str = new String(s);
        str = str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
        return str;
    }
    function submitByForm(action, params, method) {
        var $form = new Element('form',{
            action: action,
            method: method || 'post'
        });
        params = params || {};
        for (var key in params) {
            if (params.hasOwnProperty(key)) {
                new Element('input',{
                    name: key,
                    value: params[key]
                }).inject($form);
            }
        }
        $form.inject(document.body).submit();
    }
    function clickLog(tid, text, extAttr) {
        if (window.cbg_tracer) {
            var config = cbg_tracer.get_common_trace_info();
            config.push(['kind', 'S_#kind_tree_panel ul .on:not(.off)']);
            var attrs = cbg_tracer.get_attrs(config);
            attrs.push(['tid', tid], ['text', text]);
            if (extAttr && extAttr.length) {
                extAttr.each(function(item) {
                    attrs.push(item);
                })
            }
            cbg_tracer.send_log('click_event', attrs);
        }
    }
    var limitInput = {
        _limit: function($input, selector, fnIsPass, options) {
            options = options || {};
            var min = options.min
              , max = options.max;
            var lastValue = '';
            var keydown = function(e) {
                var value = this.value.trim();
                if (fnIsPass(value, e) == true) {
                    lastValue = value;
                }
            };
            var keyup = function(e) {
                var value = this.value.trim();
                if (fnIsPass(value, e) == false) {
                    this.value = lastValue;
                }
                if (min != null && this.value < min) {
                    this.value = min + '';
                } else if (max != null && this.value > max) {
                    this.value = max + '';
                }
                this.value = this.value.trim();
            };
            if (selector) {
                var $root = $input;
                $root.addEvent('keydown:relay(' + selector + ')', keydown).addEvent('keyup:relay(' + selector + ')', keyup);
            } else {
                $input.addEvent('keydown', keydown).addEvent('keyup', keyup);
            }
        },
        onlyNumber: function($input, selector, options) {
            options = Object.merge({
                negative: false,
                decimallength: 6
            }, options || {});
            var decimallength = options.decimallength
              , negative = options.negative;
            this._limit($input, selector, function isPass(value) {
                var reg = new RegExp(['^', negative ? '-?' : '', '[0-9]*', decimallength ? '(\\.[0-9]{0,' + decimallength + '})?' : '', '$'].join(''));
                return reg.test(value);
            }, options);
        },
        onlyInt: function($input, selector, options) {
            this._limit($input, selector, function isPass(value) {
                return /^\d*$/.test(value);
            }, options);
        },
        onlyPrice: function($input, selector, options) {
            this._limit($input, selector, function isPass(value) {
                return value ? /^\d+(\.\d?\d?)?$/.test(value) : true;
            }, options);
        }
    };
    var localData = (function() {
        var hasStorage = false;
        var storage = window.localStorage;
        if (storage) {
            try {
                var key = '__test__'
                  , oldValue = storage.getItem(key);
                storage.setItem(key, 1);
                storage.getItem(key);
                storage.removeItem(key);
                if (oldValue !== null) {
                    storage.setItem(key, oldValue);
                }
                hasStorage = true;
            } catch (e) {}
        }
        if (!hasStorage) {
            var IELocalStorageType = new Class({
                initialize: function() {
                    var tagid = 'local_data_tag';
                    this.dataTag = $(tagid);
                    if (!this.dataTag) {
                        this.dataTag = new Element('div',{
                            id: tagid,
                            styles: {
                                display: 'none',
                                behavior: 'url(#default#userData)'
                            }
                        });
                        var dataTag = this.dataTag;
                        window.addEvent('domready', function() {
                            var $body = $(document.body || document.getElementsByTagName('body')[0]);
                            $body.grabBottom(dataTag);
                        });
                    }
                    this.filename = 'oXMLUserData';
                },
                getItem: function(key) {
                    this.dataTag.load(this.filename);
                    return this.dataTag.getAttribute(key);
                },
                setItem: function(key, value) {
                    this.dataTag.setAttribute(key, value);
                    this.dataTag.save(this.filename);
                },
                removeItem: function(key) {
                    this.dataTag.removeAttribute(key);
                    this.dataTag.save(this.filename);
                }
            });
            storage = new IELocalStorageType();
            try {
                var key = '__test__'
                  , oldValue = storage.getItem(key);
                storage.setItem(key, 1);
                storage.getItem(key);
                storage.removeItem(key);
                if (oldValue != null) {
                    storage.setItem(key, oldValue);
                }
                hasStorage = true;
            } catch (e) {}
        }
        if (!hasStorage) {
            storage = {
                getItem: function(key) {
                    return Cookie.read(key);
                },
                setItem: function(key, val) {
                    return Cookie.write(key, val, {
                        duration: 180
                    });
                },
                removeItem: function(key) {
                    Cookie.dispose(key);
                }
            }
        }
        return {
            getItem: function(key) {
                var value = storage.getItem(key);
                return value;
            },
            setItem: function(key, val) {
                storage.setItem(key, val);
            },
            removeItem: function(key) {
                storage.removeItem(key);
            }
        };
    }
    )();
    var Dialog = new Class({
        Implements: [Options, Events],
        options: {
            title: '提示',
            content: '',
            close: true,
            buttons: [],
            className: null,
            extClassName: null,
            width: null
        },
        initialize: function(options) {
            this.setOptions(options);
        },
        getContent: function() {
            var options = this.options;
            return ['<div class="d-mask"></div>', '<span class="d-holder"></span>', options.container ? options.container : ['<span class="d-container">', '<div class="d-title">', '<span class="title-txt">', options.title, '</span>', (options.close ? '<i class="icon icon-dialog-close" data-event="close"></i>' : ''), '</div>', '<div class="d-outer">', '<div class="d-wrap">', '<div class="d-cnt">', options.content, '</div>', this._buildButtons(), options.bottomContent ? options.bottomContent : '', '</div>', '</div>', '<div class="d-container-ft"></div>', '</span>'].join('')].join('');
        },
        show: function() {
            var options = this.options;
            var $root = this.$root = new Element('div',{
                'class': 'cbg-dialog ' + [options.className || '', options.extClassName || ''].join(' '),
                html: this.getContent()
            });
            if (options.width) {
                $root.getElements('.d-container').setStyle('width', options.width);
            }
            this._bindEvents();
            $root.inject(document.body);
            this.fireEvent('show');
            return this;
        },
        hide: function() {
            if (this.$root) {
                this.$root.dispose();
                this.$root = null;
            }
            this.fireEvent('close');
            return this;
        },
        toElement: function() {
            return this.$root;
        },
        _buildButtons: function() {
            var buttons = this.options.buttons;
            if (!buttons || !buttons.length) {
                return '';
            }
            var result = [];
            result.push('<div class="d-oper">');
            for (var i = 0, max = buttons.length; i < max; i++) {
                var btn = buttons[i];
                result.push(['<a href="javascript:;" class="d-btn ', (btn.className || ''), '" hidefocus="true" data-event="', btn.event, '">', btn.text, '</a>'].join(''));
            }
            result.push('</div>');
            return result.join('');
        },
        _bindEvents: function() {
            var ctx = this;
            ctx.$root.addEvent('click:relay([data-event])', function() {
                var dataEvent = this.get('data-event');
                if (dataEvent === 'close') {
                    ctx.hide();
                } else {
                    ctx.fireEvent(dataEvent, Array.prototype.slice.call(arguments));
                }
            });
        }
    });
    Dialog.alert = function(content, options) {
        if (!options && typeof content === 'object') {
            options = content;
            content = null;
        }
        options = options || {};
        options = Object.merge({
            className: 'cbg-dialog-alert',
            content: content,
            buttons: [{
                text: options.confirmText || '确定',
                event: 'confirm'
            }]
        }, options);
        var dialog = new Dialog(options);
        dialog.addEvent('confirm', function() {
            dialog.hide();
        });
        return dialog.show();
    }
    ;
    Dialog.confirm = function(content, options) {
        if (!options && typeof content === 'object') {
            options = content;
            content = null;
        }
        options = options || {};
        options = Object.merge({
            className: 'cbg-dialog-confirm',
            content: content,
            autoClose: true,
            buttons: [{
                text: options.confirmText || '确定',
                event: 'confirm'
            }, {
                text: options.cancelText || '取消',
                event: 'cancel'
            }]
        }, options);
        var dialog = new Dialog(options);
        dialog.addEvent('confirm', function() {
            if (options.autoClose) {
                dialog.hide();
            }
        });
        dialog.addEvent('cancel', function() {
            dialog.hide();
        });
        return dialog.show();
    }
    ;
    var indicator = {
        $instance: null,
        show: function() {
            if (this.$instance) {
                return;
            }
            var options = {
                className: 'cbg-dialog-indicator',
                close: false,
                title: '',
                container: ['<span class="d-indicator-container">', '<div class="d-indicator"></div>', '</span>'].join('')
            };
            var dialog = this.$instance = new Dialog(options);
            dialog.show();
            var $root = dialog.$root;
            if ($root) {
                noop($root.clientWidth);
                $root.addClass('cbg-dialog-indicator-ready');
            }
            return dialog;
        },
        hide: function() {
            if (this.$instance) {
                this.$instance.hide();
                this.$instance = null;
            }
        }
    };
    function toast(msg, timeout) {
        var tip = document.createElement('div');
        var body = document.body || document.getElementsByTagName('body')[0];
        tip.className = 'cbg-toast';
        tip.innerHTML = msg;
        body.appendChild(tip);
        tip.style.margin = '-' + tip.clientHeight / 2 + 'px 0 0 -' + tip.clientWidth / 2 + 'px';
        tip.className += ' cbg-toast-ready';
        setTimeout(function() {
            tip.className += ' cbg-toast-leave';
            setTimeout(function() {
                tip.remove ? tip.remove() : body.removeChild(tip);
            }, 500);
        }, timeout || 2000);
    }
    var Tooltip = new Class({
        Implements: [Options, Events],
        options: {
            container: false,
            delay: 0,
            placement: 'bottom',
            title: '',
            template: '<div class="cbg-tooltip"><div class="tooltip-arrow"></div><div class="tooltip-inner"></div></div>',
            className: null,
            width: 220,
            trigger: null,
            offset: 2,
            arrowSelector: '.tooltip-arrow',
            innerSelector: '.tooltip-inner',
            alignRight: false,
            arrowToCenter: false,
            arrowNearRight: false
        },
        initialize: function(reference, options) {
            if (!reference || reference.length === 0) {
                return;
            }
            if (reference.length) {
                reference = reference[0];
            }
            this.setOptions(options);
            this.reference = $(reference);
            var events = typeof this.options.trigger === 'string' ? this.options.trigger.split(' ') : [];
            this._isOpen = false;
            this._bindEvents(events);
        },
        show: function() {
            if (!this.reference) {
                return this;
            }
            return this._show();
        },
        hide: function() {
            if (!this.reference) {
                return this;
            }
            return this._hide();
        },
        toggle: function() {
            if (!this.reference) {
                return this;
            }
            if (this._isOpen) {
                return this.hide();
            } else {
                return this.show();
            }
        },
        destroy: function() {
            this._isOpening = false;
            if (!this.reference) {
                return this;
            }
            return this._destory();
        },
        toElement: function() {
            return this._root;
        },
        _events: [],
        _bindEvents: function(events) {
            var ctx = this
              , reference = ctx.reference
              , options = ctx.options
              , directEvents = []
              , oppositeEvents = [];
            events.forEach(function(event) {
                switch (event) {
                case 'hover':
                    directEvents.push('mouseenter');
                    oppositeEvents.push('mouseleave');
                    break;
                case 'focus':
                    directEvents.push('focus');
                    oppositeEvents.push('blur');
                    break;
                case 'click':
                    directEvents.push('click');
                    oppositeEvents.push('click');
                    break;
                }
            });
            var oppositeTimer;
            directEvents.forEach(function(event) {
                var func = function(evt) {
                    clearTimeout(oppositeTimer);
                    if (ctx._isOpen || ctx._isOpening) {
                        return ctx;
                    }
                    ctx._isOpening = true;
                    setTimeout(function() {
                        if (ctx._isOpening) {
                            ctx._isOpening = false;
                            ctx._show(reference, options);
                        }
                    }, options.delay);
                };
                ctx._events.push({
                    event: event,
                    func: func
                });
                reference.addEvent(event, func);
            });
            oppositeEvents.forEach(function(event) {
                var func = function(evt) {
                    if (ctx._isOpening) {
                        if (event === 'click') {
                            return ctx;
                        } else {
                            ctx._isOpening = false;
                        }
                    } else {
                        oppositeTimer = setTimeout(function() {
                            if (!ctx._isOpening) {
                                ctx._hide(reference, options);
                            }
                        }, options.delay);
                    }
                };
                ctx._events.push({
                    event: event,
                    func: func
                });
                reference.addEvent(event, func);
            });
            return ctx;
        },
        _unbindEvents: function() {
            var ctx = this
              , reference = ctx.reference;
            ctx._events.forEach(function(params) {
                reference.removeEvent(params.event, params.func);
            });
            ctx._events = [];
            return ctx;
        },
        _show: function() {
            var ctx = this
              , reference = ctx.reference
              , options = ctx.options;
            if (ctx._isOpen) {
                return ctx;
            }
            ctx._isOpen = true;
            var tooltipGenerator = window.document.createElement('div');
            tooltipGenerator.innerHTML = options.template;
            var root = this._root = $(tooltipGenerator.childNodes[0]);
            root.setStyles({
                width: options.width
            });
            if (options.className) {
                root.addClass(options.className);
            }
            root.getElement(this.options.innerSelector).innerHTML = this.options.title;
            root.addEvent('click:relay([data-hide])', function() {
                ctx.hide();
            });
            var container = this._getContainer();
            container.appendChild(root);
            this._updatePosition();
            this._resizeHandler = this._onResize.bind(this);
            window.addEvent('resize', this._resizeHandler);
            this.fireEvent('show');
            return this;
        },
        _hide: function() {
            if (!this._isOpen) {
                return this;
            }
            this._isOpen = false;
            window.removeEvent('resize', this._resizeHandler);
            if (this._root) {
                this._root.dispose();
                this._root = null;
            }
            this.fireEvent('hide');
            return this;
        },
        _onResize: function() {
            var ctx = this;
            clearTimeout(ctx._resizeTimer);
            ctx._resizeTimer = setTimeout(function() {
                ctx._updatePosition();
            }, 50);
        },
        _destory: function() {
            this._hide();
            this._unbindEvents();
            this.fireEvent('destroyed');
            return this;
        },
        _updatePosition: function() {
            if (!this._root) {
                return;
            }
            var ctx = this
              , $root = ctx._root;
            $root.setStyles({
                top: 0,
                left: 0
            });
            var options = ctx.options
              , placement = options.placement
              , winWidth = window.getScrollWidth()
              , $reference = ctx.reference
              , rootWidth = $root.clientWidth
              , $arrow = $root.getElement(options.arrowSelector)
              , referenceCoordinates = $reference.getCoordinates()
              , referenceCenterX = referenceCoordinates.left + referenceCoordinates.width / 2;
            $root.addClass('tooltip-placement-' + placement);
            var arrowLeft;
            if (options.arrowToCenter) {
                arrowLeft = rootWidth * .5;
            } else if (referenceCenterX < (winWidth / 2) && !options.arrowNearRight) {
                arrowLeft = rootWidth * .382;
            } else {
                arrowLeft = rootWidth * .618;
            }
            $arrow.setStyle('left', arrowLeft);
            var arrowCoordinates = $arrow.getCoordinates();
            var top = referenceCoordinates.bottom - arrowCoordinates.top + options.offset
              , left = (referenceCoordinates.left + referenceCoordinates.width / 2) - (arrowCoordinates.left + arrowCoordinates.width / 2);
            if (placement == 'top') {
                top = referenceCoordinates.top - arrowCoordinates.top - arrowCoordinates.height - options.offset;
            }
            if (options.alignRight) {
                left = referenceCoordinates.left + referenceCoordinates.width - rootWidth;
            }
            var deltaFixed;
            if (left < 0) {
                deltaFixed = -left + 4;
            } else if (left + rootWidth > winWidth) {
                deltaFixed = -((left + rootWidth) - winWidth + 4);
            }
            if (deltaFixed) {
                left += deltaFixed;
                $arrow.setStyle('left', arrowLeft - deltaFixed);
            }
            $root.setStyles({
                top: top,
                left: left
            });
        },
        _getContainer: function() {
            var ctx = this;
            return $$(ctx.options.container)[0] || ctx.reference.ownerDocument.body;
        }
    });
    var MobileAdm = {
        E: new Class({
            Implements: Events
        }),
        ajax: function(method, url, data, opts) {
            var res = new this.E();
            function warn() {
                res.fireEvent('error', [].slice.call(arguments, 0));
            }
            var req = new Request.JSON(Object.merge({
                url: url,
                method: method,
                noCache: true,
                onSuccess: function(data) {
                    res.fireEvent('success', [data]);
                },
                onError: warn,
                onFailure: warn
            }, opts || {}));
            req.send(data || {});
            res.ajax = req;
            return res;
        },
        valid: function(opts, autoBindOpts) {
            var ctx = this;
            var res = new ctx.E();
            opts = Object.merge({
                url: '',
                autoBind: true,
                validAction: function(result, done) {
                    var unknow = '未知错误';
                    if (!result) {
                        done({
                            error: unknow
                        });
                    } else {
                        if (result.status == AjaxConstants.Ok) {
                            if (result.mobile) {
                                done({
                                    value: result
                                });
                            } else {
                                done({
                                    nobind: true
                                });
                            }
                        } else {
                            done({
                                error: result.msg || unknow
                            });
                        }
                    }
                    return result && result.status == AjaxConstants.Ok && result.mobile;
                },
                autoBindOpts: {}
            }, opts || {});
            if (!opts.url) {
                throw new Error('should set "url"');
            }
            function nobind() {
                if (opts.autoBind) {
                    autoBindOpts = autoBindOpts || {};
                    ctx.showBindDialog(autoBindOpts, opts).addEvent('bind', function(data) {
                        res.fireEvent('bind', [data]);
                    }).addEvent('nobind', function() {
                        res.fireEvent('nobind');
                    }).addEvent('error', function(msg) {
                        res.fireEvent('error', [msg]);
                    });
                } else {
                    res.fireEvent('nobind');
                }
            }
            res.ajax = ctx.ajax('get', opts.url);
            res.ajax.addEvent('success', function(result) {
                opts.validAction(result, function(obj) {
                    if (obj.nobind) {
                        nobind();
                    } else if (obj.error) {
                        res.fireEvent('error', [obj.error]);
                    } else {
                        res.fireEvent('bind', [obj.value, result]);
                    }
                });
            }).addEvent('error', function() {
                res.fireEvent('error', ['访问出错']);
            });
            return res;
        },
        showBindDialog: function(opts, validOpts) {
            opts = Object.merge({
                closeAsNoBind: true,
                bindAction: function() {
                    window.open('https://epay.163.com/servlet/controller?operation=activateAccount');
                },
                updateText: '为了保障您的资金安全<br/>请绑定一张银行卡<div style="padding-top: 12px;">绑定后即可使用钱包余额继续支付</div>',
                bindText: '已完成网易支付手机的绑定<br>并继续支付验证？',
                validAction: null
            }, opts || {});
            var ctx = this;
            var res = new ctx.E();
            var width = 320;
            var evtNobind = 'nobind';
            var evtGiveup = 'giveup';
            if (opts.closeAsNoBind) {
                evtGiveup = evtNobind;
            }
            var dialog1 = Dialog.alert({
                title: '升级提示',
                content: opts.updateText,
                confirmText: '立即绑定'
            });
            dialog1.addEvent('confirm', function() {
                opts.bindAction();
                var dialog2 = Dialog.alert({
                    title: '升级提示',
                    content: opts.bindText,
                    buttons: [{
                        text: '已绑定并继续支付',
                        event: 'confirm',
                        className: 'd-btn-xl'
                    }]
                });
                dialog2.addEvent('confirm', function() {
                    var validAction = opts.validAction || function(done) {
                        validOpts = validOpts || {};
                        validOpts.autoBind = true;
                        ctx.valid(validOpts, opts).addEvent('bind', function(data) {
                            done({
                                value: data
                            });
                        }).addEvent('nobind', function() {
                            done({
                                nobind: true
                            });
                        }).addEvent('error', function(msg) {
                            done({
                                error: msg
                            });
                        });
                    }
                    ;
                    validAction(function(obj) {
                        obj = obj || {};
                        if (obj.error) {
                            res.fireEvent('error', [obj.error]);
                        } else if (obj.nobind) {
                            res.fireEvent(evtNobind);
                        } else {
                            res.fireEvent('bind', [obj.value]);
                        }
                    });
                }).addEvent('close', function() {
                    res.fireEvent(evtGiveup);
                });
            }).addEvent('close', function() {
                res.fireEvent(evtGiveup);
            });
            return res;
        },
        smsCode: function(opts) {
            opts = Object.merge({
                mobile: '',
                getSmsCode: function(done) {
                    done({
                        error: '请设置 getSmsCode 参数'
                    });
                },
                countdown: 60,
                showBtmTip: true,
                btmTip: ''
            }, opts || {});
            var html = ['<div class="d-body">', '<div class="d-sms-main">', '<p style="margin:6px 0;">验证码已发送至您的网易支付手机：<span class="sms-mobile">', opts.mobile, '</span></p>', '<p style="white-space:nowrap;">', '<input class="j_input_sms_code txt-verify-code" type="text" placeholder="请输入短信验证码" /> ', '<input class="j_sms_btn btn-get-verify-code" type="button" value="获取验证码" data-event="get_sms_code"/>', '</p>', '</div>', '<p class="color-red j_error_tip" style="margin:6px 0;">&nbsp;</p>', '<p class="d-oper">', '<a class="d-btn" data-event="confirm">确认支付</a>', '</p>', '</div>'];
            if (opts.showBtmTip) {
                html = html.concat(['<div class="d-footer">', (opts.btmTip || '更换手机号请前往<a href="https://epay.163.com/accountmobile/replace_mobile_choose.htm" target="_blank">网易支付&gt;</a>'), '</div>']);
            }
            var popup = new Dialog({
                title: '手机安全验证',
                content: html.join(''),
                className: 'cbg-dialog-verify-sms',
                width: 432
            });
            popup.show();
            var $root = $(popup);
            var res = new this.E();
            var $err = $root.getElement('.j_error_tip');
            function setError(err) {
                $err && $err.set('html', err || '&nbsp;');
            }
            var $btn = $root.getElement('.j_sms_btn');
            var btnTimer = null;
            function startCountdown() {
                var index = opts.countdown;
                var clear = function() {
                    clearInterval(btnTimer);
                    btnTimer = null;
                    $btn.removeClass('sms-disabled');
                };
                var check = function() {
                    if (index > 0) {
                        $btn.set('value', index + '秒后重新发送');
                        index--;
                    } else {
                        $btn.set('value', '重新发送');
                        clear();
                    }
                };
                clear();
                btnTimer = setInterval(function() {
                    check();
                }, 1000);
                $btn.addClass('sms-disabled');
                check();
            }
            var isGettingCode = false;
            popup.addEvent('get_sms_code', function() {
                if (isGettingCode || btnTimer) {
                    return;
                }
                isGettingCode = true;
                setError('');
                opts.getSmsCode(function(obj) {
                    isGettingCode = false;
                    obj = obj || {};
                    if (obj.error) {
                        setError(obj.error);
                    } else {
                        startCountdown();
                    }
                });
            });
            popup.fireEvent('get_sms_code');
            popup.addEvent('confirm', function() {
                var code = $root.getElement('.j_input_sms_code').get('value');
                setError('');
                if (code) {
                    res.fireEvent('code', [code, popup, setError]);
                } else {
                    setError('请输入验证码');
                }
            });
            popup.addEvent('close', function() {
                res.fireEvent('giveup');
            });
            res.popup = popup;
            return res;
        }
    };
    var WalletUtils = {
        WalletData: null,
        options: {
            serviceMobile: '95163555',
            walletTip: '提示：考察期余额72小时后方可进行购买。',
            whyLessThanBalance: ['卖出商品所得金额需经过72小时考察后方可提现，因此可提现余额有可能暂时少于钱包余额。', '在公示期间售出的商品，考察期从公示期结束后开始计算。'],
            whyLessThanBalanceHelpLink: '/help/wallet.html',
            CgiRootUrl: window.CgiRootUrl || ''
        },
        initWithHtml: function($root, WalletData, options) {
            if (!$root || !WalletData || Object.keys(WalletData || {}).length <= 0) {
                return;
            }
            var html = ['<span class="cbg-wallet">', '<a href="/cgi-bin/userinfo.py?act=cbg_wallet" class="j_walletBalance" tid="mine_9" data_trace_text="web_top">钱包余额：' + fen2yuan(WalletData.balance) + '元</a>', '<i class="cbg-icon-wallet-about j_walletTips"></i>', (WalletData.is_locked || WalletData.is_pay_freeze == '1') ? '<i class="cbg-icon-wallet-lock j_walletLocked"></i>' : '', '</span>', '<span class="cbg-withdraw">', '<a href="javascript:;" class="j_walletWithdraw">提现</a>', '</span>'].join('');
            $root.set('html', html);
            this.init(WalletData, options);
        },
        init: function(WalletData, options) {
            if (Object.keys(WalletData || {}).length <= 0) {
                return;
            }
            this.WalletData = WalletData;
            this.options = Object.merge(this.options, {
                CgiRootUrl: window.CgiRootUrl || ''
            }, options || {});
            this.init_wallet_tips();
            this.init_locked_tips();
            this.init_get_money();
            this.show_wallet_guide();
        },
        init_wallet_tips: function() {
            var options = this.options;
            $$('.j_walletTips').Tooltip({
                title: ['<div class="cbg-wallet-tip">', '<div class="tip-item">', '<span class="fl">可提现余额:</span>', '<span class="fr">', fen2yuan(Math.max(this.WalletData.free_balance, 0)), '元</span>', '</div>', '<div class="tip-item">', '<span class="fl">考察期余额:</span>', '<span class="fr">', fen2yuan(this.WalletData.checking_balance), '元</span>', '</div>', '</div>', '<div class="tip-desc clear">' + options.walletTip, window.is_alipay_avail ? '<br>钱包余额/优惠券暂不支持与支付宝合并付款' : '', '</div>'].join(''),
                className: 'cbg-wallet-balance-tip',
                width: 220,
                trigger: 'hover'
            });
        },
        init_locked_tips: function() {
            var $icon = $$('.j_walletLocked');
            var options = this.options;
            if ($icon.length) {
                var is_wallet_pay_freeze = WalletData.is_pay_freeze == '1';
                var freezekey = 'wallet_freeze_dialog_key';
                var is_user_wallet = (qs.search() || {}).act === 'cbg_wallet';
                if (is_wallet_pay_freeze) {
                    $icon.addEvent('click', function() {
                        show_wallet_freeze_dialog();
                    })
                    var lockedTipsHistory = CBG.localData.getItem(freezekey);
                    $$(".j_walletWithdraw").each(function(el) {
                        el.setStyle("color", "gray");
                        el.addEvent("click", function() {
                            show_wallet_freeze_dialog();
                        });
                    });
                    if (!lockedTipsHistory && is_user_wallet) {
                        show_wallet_freeze_dialog();
                        CBG.localData.setItem(freezekey, 1);
                    }
                    return;
                } else {
                    CBG.localData.removeItem(freezekey);
                }
                var tooltip = new CBG.Tooltip($icon[0],{
                    title: ['<p class="align-center">您的钱包已被锁定，请联系客服</p>', '<p class="gold align-center">电话：' + options.serviceMobile + '</p>'].join(''),
                    className: 'cbg-wallet-balance-tip',
                    trigger: 'hover'
                });
                if (!CBG.localData.getItem('WALLET_LOCKED_GUIDE')) {
                    CBG.localData.setItem('WALLET_LOCKED_GUIDE', 1);
                    setTimeout(function() {
                        tooltip.show();
                        $(tooltip).addEvent('click', function() {
                            tooltip.hide();
                        });
                        setTimeout(function() {
                            tooltip.hide();
                        }, 10000);
                    });
                }
            }
        },
        show_wallet_guide: function() {
            if (!this.WalletData.is_locked && !CBG.localData.getItem('WALLET_GUIDE')) {
                var tipsGuide = new CBG.Tooltip($$('.j_walletBalance'),{
                    title: ['<p>钱包更新啦！<br>考察期货款直接买，钱包余额付款不受限，还等啥？买买买！</p>', '<div class="tips-actions">', '<span class="action-btn" data-hide>我知道了</span>', '</div>'].join(''),
                    width: 240
                });
                tipsGuide.addEvent('hide', function() {
                    CBG.localData.setItem('WALLET_GUIDE', 1);
                });
                tipsGuide.show();
            }
        },
        init_get_money: function() {
            var WalletData = this.WalletData
              , options = this.options
              , dialog = null
              , timer = null;
            init();
            function init() {
                var is_wallet_pay_freeze = WalletData.is_pay_freeze == '1';
                if (WalletData.is_locked || is_wallet_pay_freeze) {
                    if (is_wallet_pay_freeze) {
                        return;
                    }
                    var tooltip = new CBG.Tooltip($$('.j_walletWithdraw'),{
                        title: ['<p class="align-center">您的钱包已被锁定，请联系客服</p>', '<p class="gold align-center">电话：' + options.serviceMobile + '</p>'].join(''),
                        className: 'cbg-wallet-balance-tip',
                        trigger: 'click'
                    });
                    tooltip.addEvent('show', function() {
                        $(tooltip).addEvent('click', function() {
                            tooltip.hide();
                        });
                    });
                } else {
                    $$('.j_walletWithdraw').addEvent("click", function() {
                        dialog = new CBG.Dialog({
                            title: '提现至网易支付',
                            content: getHtml(),
                            className: 'cbg-dialog-withdraw',
                            width: 438
                        });
                        dialog.show();
                        if (WalletData.free_balance <= 0) {
                            getElement('.j_withdrawCount').set("disabled", "disabled");
                        } else {
                            initEvents();
                        }
                    });
                }
            }
            function getHtml() {
                var why = options.whyLessThanBalance.reduce(function(arr, text) {
                    return arr.push('<li>' + text + '</li>'),
                    arr;
                }, []).join('');
                return ['<div>', '<div class="withdraw-main">', '<div>', '<span class="balance-item">钱包余额：<span class="color-red">￥', fen2yuan(WalletData.balance, 0), '</span></span>', '<span class="balance-item">可提现余额：<span class="color-red">￥', fen2yuan(Math.max(WalletData.free_balance, 0)), '</span></span>', '</div>', '<div class="input-wrap">', '请输入提现金额：<input type="text" placeholder="免手续费" class="txt-amount j_withdrawCount" hidefocus="true" /> 元', '</div>', '</div>', '<div class="d-oper">', '<a href="javascript:;" class="d-btn disabled j_submit">提现</a>', '</div>', '<div class="verify-tips">', '<span class="j_verifyTips tips-content" style="display:none;"></span>', '</div>', '<div class="d-footer">', '<div class="bold">可提现余额少于钱包余额？</div>', '<ul>', why, '<li><a href="' + options.whyLessThanBalanceHelpLink + '" target="_blank">提现有疑问？</a></li>', '</ul>', '</div>', '</div>'].join('');
            }
            function getElement(selector) {
                var $root = $(dialog);
                if ($root) {
                    return $root.getElement(selector);
                }
            }
            function initEvents() {
                getElement('.j_withdrawCount').addEvent("keyup", function() {
                    var value = this.value;
                    value = value.replace(/^\./, '0.').replace(/^0+/, '0').replace(/^0([1-9])/, '$1');
                    var reg = /^[0-9]*(\.[0-9]{0,2})?$/;
                    if (value && !reg.test(value)) {
                        value = value.replace(/^[\D]*/, '').replace(/.*?([0-9]*(\.[0-9]{0,2})?).*$/, '$1');
                    }
                    if (isValidedInput(value)) {
                        if (yuan2fen(value) > WalletData.free_balance) {
                            value = fen2yuan(WalletData.free_balance);
                        }
                        getElement('.j_submit').removeClass("disabled");
                    } else {
                        getElement('.j_submit').addClass("disabled");
                    }
                    this.value = value;
                });
                getElement('.j_submit').addEvent("click", function() {
                    var value = getElement('.j_withdrawCount').value;
                    if (!isValidedInput(value)) {
                        showTips("请检查输入提现金额");
                    } else if (!/^\d*(\.\d{1,2})?$/.test(value.trim())) {
                        showTips('抱歉，提现的最小单位是分');
                    } else {
                        var amount = yuan2fen(value);
                        if (amount > WalletData.free_balance) {
                            showTips("最多可提现" + fen2yuan(Math.max(WalletData.free_balance, 0)) + "元，您已超出，请修改金额");
                        } else {
                            showConfrim(amount);
                        }
                    }
                });
            }
            function isValidedInput(value) {
                value = value || getElement('.j_withdrawCount').value;
                return value && value.trim() !== '' && !isNaN(value) && parseFloat(value) >= 0.01;
            }
            function showTips(content) {
                var el_tips = getElement('.j_verifyTips');
                el_tips.set("html", content);
                el_tips.setStyle("display", "inline-block");
                timer && clearTimeout(timer);
                timer = setTimeout(function() {
                    el_tips.setStyle("display", "none");
                }, 3000);
            }
            function showConfrim(amount) {
                dialog.hide();
                CBG.alert({
                    'content': ['<p style="padding:6px 12px 6px 0" class="cbg-withdraw-ready-text">', '您提现至网易支付的金额为：', '<span class="color-red bold" style="margin-right:2px;">', fen2yuan(amount), '</span>', '元，是否确认提现？', '</p>'].join(''),
                    'confirmText': '确认提现'
                }).addEvent('confirm', function() {
                    submit(amount);
                });
            }
            function showAuthenticationTips() {
                CBG.alert({
                    'content': '抱歉，您还没有在网易支付进行实名认证，余额无法提现，请认证后再操作。',
                    'confirmText': '前往认证'
                }).addEvent('confirm', function() {
                    window.open('https://epay.163.com/i.htm?popup=1');
                });
            }
            function showSuccessTips() {
                CBG.alert({
                    'content': '<div style="margin-bottom: 24px;"><i class="icon icon-success cbg-icon-withdraw-success" style="margin-bottom: 12px;"></i><br>提现成功，您可以继续去网易支付提现到银行卡。</div>',
                    buttons: [{
                        text: '提现至银行卡',
                        event: 'confirm',
                        className: 'd-btn-l'
                    }],
                    width: 380
                }).addEvent('confirm', function() {
                    window.open('https://epay.163.com/servlet/controller?operation=drawCashView');
                }).addEvent('close', function() {
                    location.reload();
                });
            }
            function submit(amount) {
                var url = options.CgiRootUrl + "/usertrade.py?act=ajax_cbg_wallet_withdraw";
                var params = {
                    "amount_fen": amount
                };
                var req = new Request.JSON({
                    "url": url,
                    onSuccess: function(result) {
                        if (result.status != 1) {
                            if (result.need_guide_epay_identity) {
                                showAuthenticationTips();
                            } else {
                                CBG.alert(result.msg);
                            }
                        } else {
                            showSuccessTips();
                        }
                    },
                    onFailure: function() {
                        CBG.alert('访问出错');
                    },
                    "noCache": true,
                    "async": false
                });
                req.get(params);
            }
        }
    };
    function show_wallet_freeze_dialog() {
        if (WalletData.freeze_link) {
            CBG.confirm(WalletData.freeze_remind, {
                confirmText: '人工申诉',
                cancelText: '放弃'
            }).addEvent('confirm', function() {
                window.location.href = WalletData.freeze_link;
            }).addEvent('cancel', function() {})
        } else {
            CBG.alert(WalletData.freeze_remind);
        }
    }
    var NeCaptcha = {
        ID: 1,
        init: function(args, onFailure) {
            args = args || [];
            function init() {
                var params = Object.merge({
                    captchaId: 'e8079a8b61ab419e97693235b68a33f9',
                    width: '320px'
                }, args[0] || {});
                var fnInit = args[1] || function() {}
                ;
                var fnFailure = args[2] || onFailure || function() {}
                ;
                initNECaptcha(params, fnInit, fnFailure);
            }
            if (!window.initNECaptcha) {
                Asset.javascript('//cstaticdun.126.net/load.min.js', {
                    onLoad: function() {
                        if (window.initNECaptcha) {
                            init();
                        } else {
                            onFailure && onFailure();
                        }
                    }
                });
            } else {
                init();
            }
        },
        popup: function(opts, dialogOpts) {
            opts = Object.merge({
                url: (window.CgiRootUrl || '') + '/login.py',
                key: 'captcha_validate',
                params: {
                    act: 'ajax_do_netease_captcha_auth',
                    version: 'v3',
                    client_type: 'web'
                },
                callback: function() {}
            }, opts || {});
            dialogOpts = dialogOpts || {};
            var id = 'cbg-ne-capcha-' + this.ID++;
            var dialog = Dialog.alert('<div id="' + id + '"></div><input type="hidden" name="captcha_validate" />', Object.merge({
                close: false,
                buttons: [{
                    text: dialogOpts.confirmText || '确定',
                    event: 'check'
                }]
            }, dialogOpts || {}));
            var $input = dialog.$root.getElement('[name="captcha_validate"]');
            var captchaInstance = null;
            this.init([Object.merge({
                element: '#' + id,
                width: '300px',
                mode: 'embed',
                onReady: function(instance) {
                    captchaInstance = instance;
                },
                onVerify: function(err, data) {
                    if (data && data.validate.length > 0) {
                        $input.set('value', data.validate);
                        doReq();
                    }
                }
            }, opts)]);
            dialog.addEvent('check', function() {
                if (!$input.get('value')) {
                    return alert('请进行验证操作');
                }
                doReq();
            });
            function refresh() {
                captchaInstance && captchaInstance.refresh();
                $input.set('value', '');
            }
            function doReq() {
                var args = Object.merge({}, opts.params);
                args[opts.key] = $input.get('value');
                function warn(txt) {
                    alert(txt || '未知错误');
                    refresh();
                }
                var req = new Request.JSON(Object.merge({
                    url: opts.url,
                    noCache: true,
                    onSuccess: function(result) {
                        if (result.status == 0) {
                            opts.callback();
                            return dialog.hide();
                        } else {
                            warn(result.msg);
                        }
                    },
                    onError: warn,
                    onFailure: warn
                }, opts || {}));
                req.post(args || {});
            }
            return dialog;
        }
    };
    Element.implement({
        Tooltip: function(options) {
            return new Tooltip(this,options);
        }
    });
    function floatSub(arg1, arg2) {
        var r1, r2, m, n;
        try {
            r1 = arg1.toString().split(".")[1].length;
        } catch (e) {
            r1 = 0;
        }
        try {
            r2 = arg2.toString().split(".")[1].length;
        } catch (e) {
            r2 = 0;
        }
        m = Math.pow(10, Math.max(r1, r2));
        n = (r1 >= r2) ? r1 : r2;
        return Number(((arg1 * m - arg2 * m) / m).toFixed(n));
    }
    function createDispatcher() {
        var dispatcher = new (new Class({
            Implements: Events
        }));
        dispatcher.delayFire = function(evt, args, delay) {
            setTimeout(function() {
                dispatcher.fireEvent(evt, args);
            }, delay || 0);
            return dispatcher;
        }
        return dispatcher;
    }
    function isEmptyObject(obj) {
        for (var name in obj)
            return false;
        return true;
    }
    function proxyAjax(url, data, options) {
        options = Object.merge({
            method: 'get',
            successStatus: 1
        }, options || {});
        var dispatcher = createDispatcher();
        function warn() {
            dispatcher.fireEvent('complete');
            dispatcher.fireEvent('failure', {
                error: '异常错误，请重试'
            });
        }
        var ajax = new Request.JSON({
            url: url,
            noCache: true,
            onSuccess: function(result) {
                dispatcher.fireEvent('complete');
                if (result && result['status'] == options.successStatus) {
                    dispatcher.fireEvent('success', result);
                } else {
                    dispatcher.fireEvent('failure', {
                        data: result,
                        error: result && result['msg'] || '未知错误'
                    });
                }
            },
            onError: warn,
            onFailure: warn,
            onTimeout: warn
        });
        ajax[options.method](data || {});
        return {
            dispatcher: dispatcher,
            addEvent: function(event, fn, opts) {
                dispatcher.addEvent(event, fn, opts);
                return dispatcher;
            },
            ajax: ajax
        };
    }
    function checkUserIsAdult() {}
    function getUserShareId() {
        var Ajax = new Request.JSON({
            "url": CgiRootUrl + '/userinfo.py',
            "onSuccess": function(res) {
                if (res.status == 1 && res.from_shareid) {
                    window.from_shareid = res.from_shareid;
                    var nodes = $$('.jump2DetailAddShareId');
                    nodes.each(function(el, index) {
                        var url = el.getAttribute('href') + "&from_shareid=" + res.from_shareid;
                        el.setAttribute('href', url);
                    });
                    var shareInput = $('from_shareid');
                    var fromShareID = getPara('from_shareid');
                    if (shareInput && fromShareID) {
                        shareInput.set('value', fromShareID);
                    }
                }
            }
        });
        Ajax.get({
            "act": "get_share_data"
        });
    }
    var qs = (function() {
        function toQueryString(data, opts) {
            opts = Object.merge({
                keepEmpty: false
            }, opts || {});
            data = data || {};
            var res = [];
            for (var key in data) {
                if (data.hasOwnProperty(key)) {
                    var val = data[key];
                    if (val == null && !opts.keepEmpty) {
                        continue;
                    }
                    res.push(key + '=' + encodeURIComponent(decodeURIComponent(val)));
                }
            }
            return res.join('&');
        }
        function search(s, param1) {
            param1 = Object.merge({
                shouldHtmlEncode: true
            }, param1 || {});
            var map = {};
            if (s === '') {
                return map;
            }
            var url = s || location.search;
            var fnHtmlEncode = param1.shouldHtmlEncode ? htmlEncode : function(v) {
                return v;
            }
            ;
            url.replace(/.*?\?/, '').replace(/([^=&]+)=?([^&]*)/g, function(str, key, val) {
                if (key == url) {
                    return '';
                }
                map[key] = fnHtmlEncode(decodeURIComponent(val || ''));
                return '';
            });
            return map;
        }
        function addQueryString(url, data, opts) {
            opts = Object.merge({
                keepEmpty: false
            }, opts || {});
            data = typeof data === 'string' ? search(data, {
                shouldHtmlEncode: false
            }) : data;
            var qs = toQueryString(Object.merge(search(url, {
                shouldHtmlEncode: false
            }), data || {}), {
                keepEmpty: opts.keepEmpty
            }) || '';
            return url.replace(/\?.*/, '') + (qs && '?') + qs;
        }
        return {
            search: search,
            toQueryString: toQueryString,
            addQueryString: addQueryString
        };
    }
    )();
    win.CBG = {
        CONSTANTS: CONSTANTS,
        AjaxConstants: AjaxConstants,
        qs: qs,
        htmlEncode: htmlEncode,
        localData: localData,
        Dialog: Dialog,
        indicator: indicator,
        toast: toast,
        alert: Dialog.alert,
        confirm: Dialog.confirm,
        Tooltip: Tooltip,
        fen2yuan: fen2yuan,
        yuan2fen: yuan2fen,
        submitByForm: submitByForm,
        clickLog: clickLog,
        limitInput: limitInput,
        NeCaptcha: NeCaptcha,
        MobileAdm: MobileAdm,
        WalletUtils: WalletUtils,
        floatSub: floatSub,
        getUserShareId: getUserShareId,
        createDispatcher: createDispatcher,
        proxyAjax: proxyAjax,
        checkUserIsAdult: checkUserIsAdult,
        isEmptyObject: isEmptyObject
    };
}
)(window);
