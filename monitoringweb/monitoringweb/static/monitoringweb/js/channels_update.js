function update() {
    $.ajax({
        url: "channels/",
        // cache: false,
        success: function (data) {
            // $('.x_content').html(data.result);
            // console.log(data);
            $('.update_channels').replaceWith($('.update_channels', data));
        },
    });
}

let seconds = 600; // seconds, edit here

setInterval('update()', seconds * 1000);
