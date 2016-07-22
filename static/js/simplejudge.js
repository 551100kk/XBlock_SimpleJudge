function statistics(runtime, element){
    var ac=1, tle=2, re=3, wa=4, ce, totalusers = 6, acusers = 7;
    var arr=[1,2,3];
    $.ajax({
        type: "POST",
        url: runtime.handlerUrl(element, 'statistic'),
        data: JSON.stringify({}),
        success: function(result) {
            if(result.solved){
                $(element).find('.user_status')[0].innerHTML = "(Accepted)";
                $(element).find('.user_status')[0].style.color = "green";
            }
            else if(result.submited){
                $(element).find('.user_status')[0].innerHTML = "(Submitted)";
                $(element).find('.user_status')[0].style.color = "red";
            }
            else{
                $(element).find('.user_status')[0].innerHTML = "(No Submission)";
                $(element).find('.user_status')[0].style.color = "blue";
            }
            var dataSet = [
                { label: "Accepted", data: result.ac, color: "#00A36A" },
                { label: "Time Limit Exceed", data: result.tle, color: "#7D0096" },
                { label: "Runtime Error", data: result.re, color: "#992B00" },
                { label: "Wrong Answer", data: result.wa, color: "#DE000F" },
                { label: "Compilation Error", data: result.ce, color: "#ED7B00" }    
            ];
            $.plot($(element).find('.placeholder'), dataSet, {
                series: {
                    pie: {
                        show: true,     
                        radius: 0.7,   
                         
                        label: {
                            show:true,
                            radius: 1.0,
                            background: {
                                opacity: 0,
                                color: '#FFF'
                            }
                        }
                    }
                },  
                grid: {
                    hoverable: true,
                },
                legend: {
                    show: true,
                }
            });
            $(element).find('.totalusers')[0].innerText = result.totalusers;
            $(element).find('.acusers')[0].innerText = result.acusers; 

            var str = result.Language;
            if(str == 'JAVA') str += ' --- your class name must be "Main!"'
            $(element).find('.lang')[0].innerText = str;
        }
    });console.log(arr);
    
}

function history(runtime, element, hashvalue){
    $.ajax({
        type: "POST",
        url: runtime.handlerUrl(element, 'submission'),
        data: JSON.stringify({hash:hashvalue}),
        success: function(result) {
            html_str = "";
            for(var i = result.date.length - 1; i >= 0; i--){
                if(result.result[i]=='Accepted') html_str += '<tr class="success">\n';
                if(result.result[i]=='Wrong Answer') html_str += '<tr class="danger">\n';
                if(result.result[i]=='Runtime Error') html_str += '<tr class="danger">\n';
                if(result.result[i]=='Time Limit Exceed') html_str += '<tr class="danger">\n';
                if(result.result[i]=='Compilation Error') html_str += '<tr class="warning">\n';
                html_str += '   <th>' + (result.date.length - i)  + '</th>\n';
                html_str += '   <th>' + result.date[i]  + '</th>\n';
                html_str += '   <th>' + result.result[i]  + '</th>\n';
                html_str += '   <th class="opencode" value="' + i + '" style="cursor:pointer">Open</th>\n';
                html_str += '</tr>\n'
            }
            $(element).find('.submission_table')[0].innerHTML = html_str;
            $(element).find('.opencode').bind('click', function() {
                var tmp = this;
                tmp.innerText = "Waiting...";
                $.ajax({
                    type: "POST",
                    url: runtime.handlerUrl(element, 'codepad'),
                    data: JSON.stringify({code:result.code[tmp.getAttribute('value')]}),
                    success: function(result) {
                        var newwin = window.open(); 
                        newwin.location=result.url;
                        tmp.innerText = "Open";
                    }
                });
            });
        }
    });
    statistics(runtime, element);
}

function runcode(runtime, element, hashvalue, codetime){
    $(element).find('.submission_status')[0].innerHTML = '<pre class="alert alert-info" role="alert" style="min-width:0px; width:100%"><strong>Running...</strong></pre>';
    $.ajax({
        type: "POST",
        url: runtime.handlerUrl(element, 'runcode'),
        data: JSON.stringify({code: $(element).find('textarea[name=code]').val(), hash:hashvalue, time:codetime}),
        success: function(result) {
            if(result.result == 'ac'){
                $(element).find('.submission_status')[0].innerHTML = '<pre class="alert alert-success" role="alert" style="min-width:0px; width:100%"><strong>Accepted!</strong></pre>';
            }
            else if(result.result == 're'){
                $(element).find('.submission_status')[0].innerHTML = '<pre class="alert alert-danger" role="alert" style="min-width:0px; width:100%"><strong>Runtime Error!</strong></pre>';
            }
            else if(result.result == 'tle'){
                $(element).find('.submission_status')[0].innerHTML = '<pre class="alert alert-danger" role="alert" style="min-width:0px; width:100%"><strong>Time Limit Exceed!</strong></pre>';
            }
            else{
                $(element).find('.submission_status')[0].innerHTML = '<pre class="alert alert-danger" role="alert" style="min-width:0px; width:100%"><strong>Wrong Answer!</strong></pre>';
            }
            history(runtime, element, hashvalue);
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
                history(runtime, element, hashvalue);
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
    var block = $(element)[0].getAttribute('data-usage-id');
    var hashvalue = "", cnt = 0;
    for(var i=0; i<block.length; i++){
        if(cnt==2){
            hashvalue += block[i];
        }
        if(block[i] == '@') cnt++;
    }
    $(element).find('.clear-button').bind('click', function() {
        $(element).find('textarea[name=code]').val("");
    });
    $(element).find('.save-button').bind('click',function(){
        submit(runtime, element, hashvalue);
    });
    $(document).load(function (){
        alert(123);
    });
    history(runtime, element, hashvalue);
    //statistics(runtime, element);
}
