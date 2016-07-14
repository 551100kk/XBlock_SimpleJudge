function runcode(runtime,element,hashvalue,codetime){
    $(element).find('.submission_status')[0].innerHTML='<pre class="alert alert-info" role="alert" style="min-width:0px; width:100%"><strong>Running...</strong></pre>';
    $.ajax({
        type: "POST",
        url: runtime.handlerUrl(element, 'runcode'),
        data: JSON.stringify({code: $(element).find('textarea[name=code]').val(),hash:hashvalue,time:codetime}),
        success: function(result) {
            console.log(result.result);
            console.log(result.comment);
            if(result.result=='ac'){
                $(element).find('.submission_status')[0].innerHTML='<pre class="alert alert-success" role="alert" style="min-width:0px; width:100%"><strong>Accepted!</strong></pre>';
            }
            else if(result.result=='re'){
                $(element).find('.submission_status')[0].innerHTML='<pre class="alert alert-danger" role="alert" style="min-width:0px; width:100%"><strong>Runtime Error!</strong><br><br>'
                +result.comment+'</pre>';
            }
            else if(result.result=='tle'){
                $(element).find('.submission_status')[0].innerHTML='<pre class="alert alert-danger" role="alert" style="min-width:0px; width:100%"><strong>Time Limit Exceed!</strong></pre>';
            }
            else{
                $(element).find('.submission_status')[0].innerHTML='<pre class="alert alert-danger" role="alert" style="min-width:0px; width:100%"><strong>Wrong Answer!</strong></pre>';
            }
        }
    });
}

function compile(runtime,element,hashvalue,codetime){
    $(element).find('.submission_status')[0].innerHTML='<pre class="alert alert-info" role="alert" style="min-width:0px; width:100%"><strong>Compiling...</strong></pre>';
    $.ajax({
        type: "POST",
        url: runtime.handlerUrl(element, 'compile_code'),
        data: JSON.stringify({code: $(element).find('textarea[name=code]').val(),hash:hashvalue,time:codetime}),
        success: function(result) {
            console.log(result.result);
            console.log(result.comment);
            if(result.result=='success'){
                runcode(runtime,element,hashvalue,codetime);
            }
            else{
                $(element).find('.submission_status')[0].innerHTML='<pre class="alert alert-danger" role="alert" style="min-width:0px; width:100%"><strong>Compilation Error!</strong><br><br>'
                +result.comment+'</pre>';
            }
        }
    });
}

function submit(runtime,element,hashvalue){
    //change status
    $(element).find('.submission_status')[0].innerHTML='<pre class="alert alert-info" role="alert" style="min-width:0px; width:100%"><strong>Submitting...</strong></pre>';
    console.log(hashvalue);
    $.ajax({
        type: "POST",
        url: runtime.handlerUrl(element, 'submit_code'),
        data: JSON.stringify({code: $(element).find('textarea[name=code]').val(),hash:hashvalue}),
        success: function(result) {
            console.log(result.result);
            if(result.result=='success'){
                compile(runtime,element,hashvalue,result.time);
            }
            else{
                $(element).find('.submission_status')[0].innerHTML='<pre class="alert alert-danger" role="alert" style="min-width:0px; width:100%"><strong>Submission Error!</strong></pre>';
            }
        }
    });
}

function main(runtime, element){
    //get hashvalue of the block
    var block=$(element)[0].getAttribute('data-usage-id');
    var hashvalue="",cnt=0;
    for(var i=0;i<block.length;i++){
        if(cnt==2){
            hashvalue+=block[i];
        }
        if(block[i]=='@') cnt++;
    }
    $(element).find('.clear-button').bind('click', function() {
        $(element).find('textarea[name=code]').val("");
    });
    $(element).find('.save-button').bind('click',function(){
        submit(runtime,element,hashvalue);
    });
}
