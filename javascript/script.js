

var button = function(){
	$(".button-create").mouseenter(function(){
        $(".create").animate({opacity: '0.5'});
        });
    $(".button-create").mouseleave(function(){
        $(".create").animate({opacity: '1'});
    });

    $(".button-view").mouseenter(function(){
        $(".view").animate({opacity: '0.5'});
        });
    $(".button-view").mouseleave(function(){
        $(".view").animate({opacity: '1'});
    });

     $(".button-update").mouseenter(function(){
        $(".update").animate({opacity: '0.5'});
        });
    $(".button-update").mouseleave(function(){
        $(".update").animate({opacity: '1'});

    });
}
$(document).ready(button)

$(function(){
    console.log("Jquery Working");
    var list = {};

    function onFormSubmit(event) {

        var data = $(event.target).serializeArray();
        var thesis_data = {};

        for (var i = 0; i < data.length; i++) {
            var key = data[i].name;
            var value = data[i].value;
            thesis_data[key] = value; 
        }

        var thesis_create_api = '/api/handler';
        $.post(thesis_create_api, thesis_data, function(response)
        {
            if (response.status = 'OK')
            {
                var full_data = response.data.yearlist + "   |   " + response.data.thesis_title + "   |   " + response.data.author_fname + " " + response.data.author_lname;
                $('ul.thesis-list').prepend('<li>'+full_data+' <a class="mybtn" href=\'thesis/edit/'+response.data.self_id+'\'>Edit</a><a class=\'mybtn\' href=\'thesis/delete/'+response.data.self_id+'\'>delete</a></li>');
                $('form#form1 input[type=text], textarea').val("");
                $('form#form1 input[type=textarea], textarea').val("");
            }
            else alert('Error 192.168.1.10, Database error');
        })
        
        return false;
    }

    function onRegFormSubmit(event) {
        var data = $(event.target).serializeArray();
        var user_data = {};

        for (var i = 0; i < data.length; i++) {
            var key = data[i].name;
            var value = data[i].value;
            user_data[key] = value; 
        }

        
        var register_api = '/api/user';
        $.post(register_api, user_data, function(response)
        {   
            if (response.status = 'OK')
            {
                $(location).attr('href', 'http://localhost:8080/');
                return false;
            }
            else alert('Error 192.168.1.10, Database error');
        })
        return false;
    }

    loadAllThesis();
    $('form#form1').submit(onFormSubmit);
    $('form#registration').submit(onRegFormSubmit);

    $(document).on('click', '.mybtn',function(){
        $(this).closest('li').remove();
    });

    function loadAllThesis() 
    {
        var thesis_list_api = '/api/handler';
        $.get(thesis_list_api,{},function(response){
            response.data.forEach(function(thesis) {
                var thesis_info = thesis.yearlist + "   |   " + thesis.thesis_title + "   |   " + thesis.author_fname + " " + thesis.author_lname;
                $('ul.thesis-list').append('<li>'+thesis_info+' <a class="mybtn" href=\'thesis/edit/'+thesis.self_id+'\'>Edit</a><a class=\'mybtn\' href=\'thesis/delete/'+thesis.self_id+'\'>delete</a></li>');
                return false;       
            })
        })
    }
    
});
