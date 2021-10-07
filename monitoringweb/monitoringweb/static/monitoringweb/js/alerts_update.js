function update() {
    $.ajax({
        url: "/",
        // cache: false,
        success: function (data) {
            // $('.x_content').html(data.result);
            // console.log(data);
            $('.x_content').replaceWith($('.x_content', data));
        },
    });
}

let seconds = 60; // seconds, edit here

setInterval('update()', seconds * 1000);
