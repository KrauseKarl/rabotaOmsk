jQuery.noConflict()(function ($) {

    'use strict';

    var isMobile = {
  Android: function () {
    return navigator.userAgent.match(/Android/i);
  },
  BlackBerry: function () {
    return navigator.userAgent.match(/BlackBerry/i);
  },
  iPhone: function () {
    return navigator.userAgent.match(/iPhone/i);
  },
  iPad: function () {
    return navigator.userAgent.match(/iPad/i);
  },
  iPod: function () {
    return navigator.userAgent.match(/iPod/i);
  },
  iOS: function () {
    return navigator.userAgent.match(/iPhone|iPad|iPod/i);
  },
  Opera: function () {
    return navigator.userAgent.match(/Opera Mini/i);
  },
  Windows: function () {
    return navigator.userAgent.match(/IEMobile/i);
  },
  any: function () {
    return (isMobile.Android() || isMobile.BlackBerry() || isMobile.iOS() || isMobile.Opera() || isMobile.Windows());
  }
  };

    $(document).ready(function () {
//        getParams();
          checkBoxs();
//        liveSearch();
//        key_activate();
//        loaderScroll();
//        cleanInputSearch();
//        setLocation();
            searchSubmit();
            searching();
//        //filterBord();
//        cleanCatalogInputSearch();
//        cleanSearch();
//        showLoc();
//        parseUrlQuery();
//        responseTemplate();
    });

    /* LIVE SEARCH ON MAIN PAGE START */
    var suggest_count = 0;
    var input_initial_value = '';
    var suggest_selected = 0;

    window.onload = function() {
    var reloading = sessionStorage.getItem("reloading");
        if (reloading) {
            sessionStorage.removeItem("reloading");
            checkBoxs();
        }
    };

    function reloadP() {
        sessionStorage.setItem("reloading", "true");
        document.location.reload();
    };

    function getParams(){
        var searchPlus = window.location.search.substring(1);
        var search = window.location.search.replace(/\+/g, ' ').replace(/\?/g, '');
        var queryArray = decodeURIComponent(search).split('&')

        var paramDict = {}
        var result = queryArray.reduce((params, hash) => {
              let [key, val] = hash.split('=')
              if(paramDict[key]) {
              paramDict[key].push(val)
              } else {
               paramDict[key] = [val]
              }
              return Object.assign(params, {[key]:val})
          }, {})

        return paramDict
    };

    function checkBoxs(){
        var paramDict =  getParams()
        var paramArray = []
        $.each(paramDict, function(k, array){
           $.each(array, function(index, val) {
              paramArray.push(val)
           });
        });
        $('body input:checkbox').prop('checked', false);
         filterList(paramArray)
        $.each(paramArray, function(index, param) {
            var par = param;

            $("input.form-check-input").each(function() {
                var checkBox = $(this);
                var checkBoxValue = $(this).val();
                if(param == checkBoxValue){
                    $(this).prop('checked', true);
                    checkBox.checked = true;
                    $(this).attr('checked', 'checked')
                }
            });
        });
    };

    function handleClick() {
        $("#search_box").val("");
        $("#search_advice_wrapper").html("").hide();
    };

    function liveSearch(){
        // читаем ввод с клавиатуры
        $("#search_box").keyup(function(I){
            // определяем какие действия нужно делать при нажатии на клавиатуру
            switch(I.keyCode) {
                // игнорируем нажатия на эти клавишы
                case 13:  // enter
                case 27:  // escape
                case 38:  // стрелка вверх
                case 40:  // стрелка вниз
                break;

                default:
                    // производим поиск только при вводе более 2х символов
                    if($(this).val().length>2){

                        input_initial_value = $(this).val();
                        // производим AJAX запрос к /ajax/ajax.php, передаем ему GET query, в который мы помещаем наш запрос
                        var queryString = '?search='+ $(this).val()
                        $.ajax({
                            url: `/search/${queryString}`,
                            type: 'GET',
                            dataType: 'json',
                            data: queryString,
                            success: function (data) {
                                if(data.vacancy) {
                                    var list = data.vacancy;
                                    suggest_count = list.length;
                                    if(suggest_count > 0){
                                        var closeBtn = "<div class='btn__clean' ><a onClick=handleClick()>&#215;&nbsp;&nbsp;очистить</a></div>"
                                        // перед показом слоя подсказки, его обнуляем
                                        $("#search_advice_wrapper").html("").show();
                                         $('#search_advice_wrapper').append(closeBtn);

                                           for(var i in list){
                                                if(list[i] != ''){
                                                    // добавляем слою позиции
                                                    var slug = list[i][1]
                                                    var name = list[i][0]
                                                    var salary = list[i][2]
                                                    var html = '<div class="advice_variant"><a class="advice__variant__link" href="/vacancy/'+slug+'/">'+name+'</a><b style="float:right;">'+salary+'</b></div>'
                                                    $('#search_advice_wrapper').append(html);
                                                }
                                            }
                                        }
                                    else {
                                        $("#search_advice_wrapper").html("").show();
                                        var html = '<div class="advice_variant"> ничего не найдено </div>'
                                        $('#search_advice_wrapper').append(html);
                                    };
                                } else {
                                        var html = '<div class="advice_variant"> ничего не найдено </div>'
                                        $('#search_advice_wrapper').append(html);
                                };
                            },
                            error: function (jqXHR, exception) {
                                console.log(exception)
                            }
                        });
                    } else {
                        $("#search_advice_wrapper").html("").hide();
                    }
                break;
            }
        });

        //считываем нажатие клавишь, уже после вывода подсказки
        $("#search_box").keydown(function(I){
            switch(I.keyCode) {
                // по нажатию клавишь прячем подсказку
                case 13: // enter
                case 27: // escape
                    $('#search_advice_wrapper').hide();
                    return false;
                break;
                // делаем переход по подсказке стрелочками клавиатуры
                case 38: // стрелка вверх
                case 40: // стрелка вниз
                    I.preventDefault();
                    if(suggest_count){
                        //делаем выделение пунктов в слое, переход по стрелочкам
                        key_activate( I.keyCode-39 );
                    }
                break;
            }
        });

        // делаем обработку клика по подсказке
        $('.advice_variant').on('click',function(){
            // ставим текст в input поиска
            $('#search_box').val($(this).text());
            // прячем слой подсказки
            $('#search_advice_wrapper').fadeOut(350).html('');
        });

        // если кликаем в любом месте сайта, нужно спрятать подсказку
        $('html').click(function(){
            $('#search_advice_wrapper').hide();
        });
        // если кликаем на поле input и есть пункты подсказки, то показываем скрытый слой
        $('#search_box').click(function(event){
            //alert(suggest_count);
            if(suggest_count)
                $('#search_advice_wrapper').show();
            event.stopPropagation();
        });
    };

    function key_activate(n){
        $('#search_advice_wrapper div').eq(suggest_selected-1).removeClass('active');

        if(n == 1 && suggest_selected < suggest_count){
            suggest_selected++;
        }else if(n == -1 && suggest_selected > 0){
            suggest_selected--;
        }
        if( suggest_selected > 0){
            $('#search_advice_wrapper div').eq(suggest_selected-1).addClass('active');
            $("#search_box").val( $('#search_advice_wrapper div').eq(suggest_selected-1).text() );
        } else {
            $("#search_box").val( input_initial_value );
        }
    }
    /* LIVE SEARCH ON MAIN PAGE END */

    /* SCROLL LOADER */
    function loaderScroll(){
        var spinner = '<div class="d-flex justify-content-center"><div class="spinner-grow" role="status" style="color:var(--one-color);width: 5rem; height: 5rem;"><span class="visually-hidden">Loading...</span></div></div>'
        $('#vacancies').html('');
        $('#vacancies').html(spinner);
    }
    /* SCROLL LOADER */

    function cleanInputSearch(){
        $("#search_input_category").val('');
        $('#search_result').html('');
        $('.accordion-collapse').each(function() {
             $(this).removeClass('show');
        });
        $('.accordion-item').each(function() {
            $(this).show()}
        );
        $('.list-group > li').each(function() {
            $(this).css({'background-color': 'var(--two-color)'}).show();
        });
    };

    //$(document).ready(
    function searchSubmit(){
        $("#search_submit").on('click', function(event) {
        event.preventDefault();
        var urlSearch = $("form").serialize()
        searching(urlSearch);
        });
    };
    //);

    $(document).ready(function(){
        event.preventDefault();
        $("input.form-check-input").on("change", function() {
        var urlSearch = $("form").serialize();
        searching(urlSearch);
    })
    });

    function setLocation(curLoc){
        var currentUrl = location.search;
        if(currentUrl.split('?').length > 1) {
            var oldURL = currentUrl[1]
        };
        location.search = curLoc
    }

    function searching(params) {
        $.ajax({
        url: '/filter/',
        method: 'get',
        data: {'params': params},
        success: function(data){
            responseTemplate(data);
        },
        });
    };

    function filterBord() {
        $('#hide_filter').toggle();
        $('#show_filter').toggle();
        $('#filter').toggle(900);
    };

    function filterList(params) {
      $('.filter__bar').css('display', 'block');
        for(var i in params) {
            var subtitle = '<span class="mb-2">' + params[i]+ '</span>'
            $('#title').append(subtitle);
            };
        };

    function cleanCatalogInputSearch() {
        $('body input:checkbox').prop('checked', false);
        $('#title').html('');
        $('.filter__bar').css('display', 'none');
        searchingSubmit();
    };

    function cleanSearch() {
        $("#search_input").val('');
        window.location.search='';
        cleanCatalogInputSearch();
    };

    function showLoc() {
       var x = window.location;
       var t = ['Property - Typeof - Value',
                'window.location - ' + (typeof x) + ' - ' + x ];
       for (var prop in x){
         t.push(prop + ' - ' + (typeof x[prop]) + ' - ' +  (x[prop] || 'n/a'));
       }
    }

    function parseUrlQuery() {
        var data = {};
        if(location.search) {
            var pair = (location.search.substr(1)).split('&');
            for(var i = 0; i < pair.length; i ++) {
                var param = pair[i].split('=');
                data[param[0]] = param[1];
            }
        }
        return data;
    }

    function responseTemplate(data) {
        $('#vacancies').html('');
        $('.title_page h2').html('');
        var list = data.result;
        var title = data.title;
        if(list.length > 0) {
            for(var i in list){
                if(list[i] != ''){
                    var schedule  =  '<h6 class="text-muted">график работы&nbsp;&nbsp;<span style="float:right;">'+ list[i]["schedule"] +'</span></h6>'
                    var type     =  '<h6 class="text-muted">тип занятости&nbsp;&nbsp;<span style="float:right;">'+list[i]["types"] +'</span></h6>'
                    var experience = '<h6 class="text-muted">опыт&nbsp;&nbsp;<span style="float:right;">'+list[i]["experience"] +'</span></h6>'
                    var html = '<div class="col-12"><div class="card  card__mine card_vacancy  m-1"><div class="card-body"><h5 class="card-title" style="float:right;"><a class="catalog__link" href="/vacancy/'+list[i]["slug"]+'">'+ list[i]["vacancy"] +'</a></h5><h6>'+ list[i]["salary"] +'</h6></div><div class="card-body">'+schedule+type+experience+'</div></div></div>'

                    $('#vacancies').append(html);
                    var params = data.params;

                    $(".title_page h2").html(data.title);
                    $('#title').html('');
                    if(params.length > 0 && params[0] != '') {
                       $(".title_page > h4").html(data.title);
                       $('.search__string').html('поиск по:').addClass("card__vacancy__h").css("background-color:", "var(--four-color)");
                       $('.search__string').prepend('<div style="float:right;" class="text-muted search__clean"><a class="link-dark"  onclick="cleanCatalogInputSearch()">очистить</a></div>');
                    } else {
                       $('.search__string').html('').removeClass("card__vacancy__h");
                       $('.search__clean').html('');
                    };
                    filterList(params);

        }
                else {
                     $('#vacancies').append('<div class="col-12 text-center m-5"><h2 style="color:var(--one-color); font-weigh:700;">404</h2><h4>Ничего не найдено</h4></div>');
                };
            };
        };
    };

    /// CATEGORIES SEARCHING
    $(document).ready(function(){
        $("#search_input_category").on("change", function(event) {
            event.preventDefault();
            var searchCategory = $(this).val().toLowerCase();
            $('#search_result').html('');
            searchProfession(searchCategory);
        });
    });
    $(document).ready(function(){
        $("#search_button_category").on("submit", function(event) {
            event.preventDefault();
            var searchCategory = $(this).val().toLowerCase();
             $('#search_result').html('');
            searchProfession(searchCategory);
        });
    });
    function searchProfession(searchCategory) {
    if(searchCategory.length > 2) {
        $('.accordion-item').each(function() {
           $(this).hide()}
        );
        $('.sub__profession').each(function() {
            var sumTitle = $(this).data("subtitle").toLowerCase();
            var idParent =  $(this).data("id-parent");
            var idSubTitle = $(this).data("id");
            var matchString = "^"+searchCategory
            if(sumTitle.match(matchString)  != null) {
                $('.accordion-item').each(function() {
                    var accordionItem = $(this).data("title");
                    var accordionName = $(this).data("name");
                    var titleParent = $(this);
                    if(idParent == accordionItem ) {
                        $(this).find('li').each(function() {
                            if($(this).data('id') == idSubTitle){
                                var keyWord = $(this).data('subtitle');
                                var pattern = new RegExp("/((?:^|>)[^<]*)("+searchCategory+")/si");
                                var highLight = keyWord.replace(pattern)
                                var html = "<div class='accordion-body'><ul class='list-group list-group-flush'><li class='list-group-item sub__profession mb-3 py-2' style='background-color:var(--four-color); color:var(--three-color);'><a class='link-dark fs-4' href='/catalog?search="+$(this).data('subtitle')+"'>"+$(this).text()+"</a><span class='text-muted' style='float:right'>"+accordionName+"</span></li></div></ul>"

                                $('#search_result').append(html)
                            } else {
                                $(this).hide();
                            };
                        });
                    };
                });

            // }
            // else {
            // $('.accordion').html("<h3><b style='color:var(--one-color);'>404</b>&nbsp;Поиск не дал результата</h3>")
            };

        })
        $('#search_result').append('<hr>')
        $('.sub__profession').each(function() {
            var sumTitle = $(this).data("subtitle").toLowerCase();
            var idParent =  $(this).data("id-parent");
            var idSubTitle = $(this).data("id");
            var matchString = "^"+searchCategory
            if(sumTitle.search(searchCategory) != -1 && sumTitle.match(matchString)  == null) {
                $('.accordion-item').each(function() {
                    var accordionItem = $(this).data("title");
                    var accordionName = $(this).data("name");
                    var titleParent = $(this);
                    if(idParent == accordionItem ) {
                        $(this).find('li').each(function() {
                            if($(this).data('id') == idSubTitle){
                                var html = "<div class='accordion-body'><ul class='list-group list-group-flush'><li class='list-group-item sub__profession mb-3 py-2' style='background-color:var(--two-color);'><a class='link-dark' href='/catalog?search="+$(this).data('subtitle')+"'>"+$(this).text()+"</a><span class='text-muted' style='float:right'>"+accordionName+"</span></li></div></ul>"
                                $('#search_result').append(html)
                            } else {
                                $(this).hide();
                            };
                        });
                    };
                });

            // }
            // else {
            // $('.accordion').html("<h3><b style='color:var(--one-color);'>404</b>&nbsp;Поиск не дал результата</h3>")
            };

        })

    } else {
        $('#search_result').html('');
        $('.accordion-collapse').each(function() {
             $(this).removeClass('show');
        });
        $('.accordion-item').each(function() {
            $(this).show()}
        );
        $('.list-group > li').each(function() {
            $(this).css({'background-color': 'var(--two-color)'}).show();

        });
    };
};

});



jQuery('#group input:checkbox').click(function(){
	if (jQuery(this).is(':checked')) {
		 jQuery('#group input:checkbox').not(this).prop('checked', false);
	}
});