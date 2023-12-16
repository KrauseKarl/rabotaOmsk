var suggest_count = 0;
var input_initial_value = '';
var suggest_selected = 0;

function handleClick() {
    $("#search_box").val("");
    $("#search_advice_wrapper").html("").hide();
};

$(window).load(function(){
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
                    console.log($(this).val())
					input_initial_value = $(this).val();
					// производим AJAX запрос к /ajax/ajax.php, передаем ему GET query, в который мы помещаем наш запрос
					var queryString = '?query='+ $(this).val()
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
$("input.form-check-input").on("change", function() {
    var params = $(this).val();
    var arr = $(this).is(":checked");
    if(!arr) params = null;
    console.log(params)
    console.log(arr)
    $.ajax({
	url: '/filter/',
	method: 'get',
	data: {'param': params},
	success: function(data){
	    console.log(data.result);
		$('#vacancies').html('')
		var list = data.result
		for(var i in list){
            if(list[i] != ''){
                // добавляем слою позиции
                var html = '<div class="card  card__mine card_vacancy  m-1"><div class="card-body"><h5>' +  list[i]["title"] +'</h5><h6>'+  list[i]["schedule"] + list[i]["salary"] +'</h6></div></div>'
                $('#vacancies').append(html);
            }
        }
	    }
    });
})
