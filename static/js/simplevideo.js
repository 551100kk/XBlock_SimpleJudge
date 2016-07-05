function SimpleVideoBlock(runtime, element){
    var player= $('.simplevideo iframe')[0];
    var watched_status = $('.simplevideo .status .watched-count');
    console.log(player);
    function on_finish(){
        $.ajax({
            type: "POST",
            url: runtime.handlerUrl(element, 'mark_as_watched'),
            data: JSON.stringify({watched: true}),
            success: function(result) {
                watched_status.text(result.watched_count);
            }
        });
    }
    on_finish()
}