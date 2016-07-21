function testdata(runtime, element){
    $.ajax({
        type: "POST",
        url: runtime.handlerUrl(element, 'show_testdata'),
        data: JSON.stringify({}),
        success: function(result) {
            html_str = "";
            for(var i = 0; i < result.name.length; i++){
                html_str += '<br><a href="#" class="btn btn-default data_in" role="button" style="width:100%">'+ result.name[i] +'.in</a><br>';
            }
            $(element).find('.display_in')[0].innerHTML = html_str;
            html_str = "";
            for(var i = 0; i < result.name.length; i++){
                html_str += '<br><a href="#" class="btn btn-primary data_out" role="button" style="width:100%">'+ result.name[i] +'.out</a><br>';
            }
            $(element).find('.display_out')[0].innerHTML = html_str;
            $(element).find('.data_in').bind('click', function() {
                var str = this.innerText;
                var num = result.name.indexOf(str.replace('.in', ''));
                location.href = ("data:text/csv;charset=utf-8," + encodeURIComponent(result.in[num]));
            });
            $(element).find('.data_out').bind('click', function() {
                var str = this.innerText;
                var num = result.name.indexOf(str.replace('.out', ''));
                location.href = ("data:text/csv;charset=utf-8," + encodeURIComponent(result.out[num]));
            });
        }
    }); 
}
function main(runtime, element) {
    $(element).find('.save-button').bind('click', function() {
        var handlerUrl = runtime.handlerUrl(element, 'studio_submit');
        var data = {
            Description: $(element).find('textarea[name=Description]').val(),
            pro_input: $(element).find('textarea[name=pro_input]').val(),
            pro_output: $(element).find('textarea[name=pro_output]').val(),
            sample_input: $(element).find('textarea[name=sample_input]').val(),
            sample_output: $(element).find('textarea[name=sample_output]').val(),
            display_name: $(element).find('input[name=display_name]').val(),
        };
        runtime.notify('save', {state: 'start'});
        $.post(handlerUrl, JSON.stringify(data)).done(function(response) {
        runtime.notify('save', {state: 'end'});
        location.reload();
        });
    });

    $(element).find('.cancel-button').bind('click', function() {
        runtime.notify('cancel', {});
    });
    $(element).find('.upload-status')[0].innerHTML=('<pre class="alert alert-info" role="alert" style="min-width:0px; width:100%"><strong>Select the file!</strong></pre>');
    $(element).find('.upload-button').bind('click', function() {
        var input = $(element).find("[id=data_in]")[0].files;
        if(!input.length){
            $(element).find('.upload-status')[0].innerHTML=('<pre class="alert alert-danger" role="alert" style="min-width:0px; width:100%"><strong>Please choose the file!</strong></pre>');
            return;
        }
        $(element).find('.upload-status')[0].innerHTML=('<pre class="alert alert-info" role="alert" style="min-width:0px; width:100%"><strong>Uploading...0%</strong></pre>');
        input=input[0];
        var reader=new FileReader();
        reader.onloadend = function () {
            console.log('loaded');
            function progress(e){
                if(e.lengthComputable){
                    var max = e.total;
                    var current = e.loaded;
                    var Percentage = (current * 100)/max;
                    $(element).find('.upload-status')[0].innerHTML=('<pre class="alert alert-info" role="alert" style="min-width:0px; width:100%"><strong>Uploading...'+ Percentage +'%</strong></pre>');
                    if(Percentage >= 100){
                        $(element).find('.upload-status')[0].innerHTML=('<pre class="alert alert-info" role="alert" style="min-width:0px; width:100%"><strong>Processing...</strong></pre>');
                    }
                }  
             }
            $.ajax({
                type: "POST",
                url: runtime.handlerUrl(element, 'upload_testdata'),
                data: JSON.stringify({zipdata:reader.result}),
                success: function(result) {
                    if(result.result == 'success'){
                        $(element).find('.upload-status')[0].innerHTML=('<pre class="alert alert-success" role="alert" style="min-width:0px; width:100%"><strong>Success!</strong></pre>');
                    }
                    else{
                        $(element).find('.upload-status')[0].innerHTML=('<pre class="alert alert-danger" role="alert" style="min-width:0px; width:100%"><strong>.in files does not match .out files!</strong></pre>');
                    }
                    testdata(runtime, element);
                    console.log('finished');
                },
                xhr: function() {
                    var myXhr = $.ajaxSettings.xhr();
                    if(myXhr.upload){
                        myXhr.upload.addEventListener('progress',progress, false);
                    }
                    return myXhr;
                },
                error: function(data){
                    console.log(data);
                }
            }); 
        }
        reader.readAsDataURL(input);        
    });
    testdata(runtime, element);
}