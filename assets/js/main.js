/* LIVE SEARCH ON MAIN PAGE START */
var suggest_count = 0;
var input_initial_value = '';
var suggest_selected = 0;

window.onload = isReload();
function isReload() {
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

                            if(data.vacancy || data.category) {
                                $("#search_advice_wrapper").html("").show();
                                var closeBtn = "<div class='btn__clean' ><a onClick=handleClick()>&#215;&nbsp;&nbsp;очистить</a></div>"
                                var list = data.vacancy;
                                var catList = data.category;
                                if(list.length > 0 || catList.length > 0){
                                     if(catList.length > 0){
                                        for(var i in catList){
                                        if(catList[i] != ''){
                                            var cat = catList[i]
                                            console.log('cat',cat)
                                            var html = `<div class="advice_variant"><a class="advice__variant__link"href="/catalog?search=${cat}">${cat}</a><b style="float:right;">категория</b></div>`

                                            $('#search_advice_wrapper').append(html);
                                        }
                                   };
                                     };

                                     $('#search_advice_wrapper').append("<hr>");

                                      if(list.length > 0){
                                        for(var i in list){
                                            if(list[i] != ''){
                                                // добавляем слою позиции
                                                var slug = list[i][1]
                                                var name = list[i][0]
                                                var salary = list[i][2]
                                                var html = '<div class="advice_variant"><a class="advice__variant__link" href="/vacancy/'+slug+'/">'+name+'</a><b style="float:right;">'+salary+'</b></div>'
                                                $('#search_advice_wrapper').append(html);
                                            }
                                       };
                                      };
                                } else {
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
$("#spinner").hide();

/* SCROLL LOADER */
function loaderScroll(){
   $('#spinner').show();
};
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
$('html').click(function(){
    $("#error").html('');
    $("#search_input").addClass('search_input');
    $("#search_input").removeClass('search_error');
});

$("#search_input").on('click keyup',function(){
    $("#error").html('');
    $("#search_input").addClass('search_input');
    $("#search_input").removeClass('search_error');
});

$("#search_submit").on('click', function(event) {
    event.preventDefault();
    var searchString = $("#search_input").val()
    if(searchString == '' ||  searchString == null) {
        $("#error").html('введите вакансию').css("color", "red");
        $("#search_input").removeClass('search_input');
        $("#search_input").addClass('search_error');
        return false
    }
    var urlSearch = $("form").serialize()
    searching(urlSearch);
});

//);

$(document).ready(function(){
    event.preventDefault();
    $("input.form-check-input").on("change", function() {
    var urlSearch = $("form").serialize();
    loadingUp();
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
function loadingUp() {
    $(".load").each(function() {
        $(this).addClass("loading");
    });
};
function loadingDown() {
    $(".load").each(function() {
        $(this).removeClass("loading");
    });
};

function searching(params) {
    $.ajax({
    url: '/filter/',
    method: 'get',
    data: {'params': params},
    success: function(data){
       loadingUp();
        setTimeout(function() {responseTemplate(data)}, 1500);
    },
});
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
     loadingDown();
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
    }  else {
    var notFound = '<div class="col-12 text-center m-5"><h2 style="color:var(--one-color); font-size:10rem; font-weigh:700;">404</h2><h4>Ничего не найдено</h4><h5><span class="btn btn__mine btn__dark" onclick="cleanCatalogInputSearch()">сбросить фильтр поиска</span></h5></div>'
       $('#vacancies').append(notFound);
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
                            var html = "<div class='accordion-body'><ul class='list-group list-group-flush'><li class='list-group-item sub__profession mb-3 py-2' style='background-color:var(--two-color);'><a class='link-dark' href='/catalog?search="+$(this).data('subtitle').toLowerCase()+"'>"+$(this).text()+"</a><span class='text-muted' style='float:right'>"+accordionName+"</span></li></div></ul>"
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



function cleanCatalogInputSearch() {
    $('body input:checkbox').prop('checked', false);
    $('#title').html('');
    $('.filter__bar').css('display', 'none');
    var searchString = $("#search_input").serialize();
    searching(searchString);
};

function cleanSearch() {
    $("#search_input").val('');
    window.location.search='';
    cleanCatalogInputSearch();
};

$('#group input:checkbox').click(function(){
if ($(this).is(':checked')) {
     $('#group input:checkbox').not(this).prop('checked', false);
}
});

function filterBord() {
$('#hide_filter').toggle();
$('#show_filter').toggle();
$('#filter').toggle(900);
};
