function SimpleVideoEditBlock(runtime, element) {
    $(element).find('.save-button').bind('click', function() {
        var handlerUrl = runtime.handlerUrl(element, 'studio_submit');
        var data = {
            href: $(element).find('input[name=href]').val(),
            maxwidth: $(element).find('input[name=maxwidth]').val(),
            maxheight: $(element).find('input[name=maxheight]').val(),
            Description: $(element).find('textarea[name=Description]').val(),
            pro_input: $(element).find('textarea[name=pro_input]').val(),
            pro_output: $(element).find('textarea[name=pro_output]').val(),
            sample_input: $(element).find('textarea[name=sample_input]').val(),
            sample_output: $(element).find('textarea[name=sample_output]').val(),
        };
        runtime.notify('save', {state: 'start'});
        $.post(handlerUrl, JSON.stringify(data)).done(function(response) {
        runtime.notify('save', {state: 'end'});
        });
    });

    $(element).find('.cancel-button').bind('click', function() {
        runtime.notify('cancel', {});
    });
    
    $(element).find('.upload-button').bind('click', function() {
        var input = $(element).find("[id=data_in]")[0].files;
        var output = $(element).find("[id=data_out]")[0].files;
        if(!input.length){
            var status=$(element).find('.upload-status');
            status[0].innerHTML=('<pre class="alert alert-danger" role="alert" style="min-width:0px; width:100%"><strong>Please upload the input file!</strong></pre>');
            return;
        }
        if(!output.length){
            var status=$(element).find('.upload-status');
            status[0].innerHTML=('<pre class="alert alert-danger" role="alert" style="min-width:0px; width:100%"><strong>Please upload the output file!</strong></pre>');
            return;
        }
        input=input[0];
        output=output[0];
        var flag=0;
        var reader1=new FileReader();
        var reader2=new FileReader();
        reader1.onloadend = function () {
            input=String(reader1.result);
            reader2.onloadend = function () {
                output=String(reader2.result);
                $.ajax({
                    type: "POST",
                    url: runtime.handlerUrl(element, 'upload_testdata'),
                    data: JSON.stringify({input_data:String(input),output_data:String(output)}),
                    success: function(result) {
                        var status=$(element).find('.upload-status');
                        status[0].innerHTML=('<pre class="alert alert-success" role="alert" style="min-width:0px; width:100%"><strong>Uploaded!</strong></pre>');  
                        location.reload();   
                    }
                });        
            }    
            reader2.readAsText(output);
        }
        reader1.readAsText(input);        
    });
}