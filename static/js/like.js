function like(user, nid, that) {
    $.ajax({
        url: "/like/" + user + "/" + nid + ".html",
        type: "post",
        dataType: "json",
        success: function (arg) {
            // console.log(arg);
            // $("#tb1").append(arg);
            if (arg.error) {
                alert(arg.data);

            }
            else {
                if (arg.status) {
                    $(that).find("i").attr("class", "fa fa-thumbs-up");
                    $(that).next().find("i").attr("class", "fa fa-thumbs-o-down");
                } else {
                    $(that).find("i").attr("class", "fa fa-thumbs-o-up");
                    $(that).next().find("i").attr("class", "fa fa-thumbs-o-down");
                }

                $(that).find("span").text(arg.up_count);
                $(that).next().find("span").text(arg.down_count)
            }
        }
    })
}

function dislike(user, nid, that) {
    $.ajax({
        url: "/dislike/" + user + "/" + nid + ".html",
        type: "post",
        dataType: "json",
        success: function (arg) {
            // console.log(arg);
            // $("#tb1").append(arg);
            if (arg.error) {
                alert(arg.data);

            }
            else {
                if (arg.status) {
                    $(that).find("i").attr("class", "fa fa-thumbs-down");
                    $(that).prev().find("i").attr("class", "fa fa-thumbs-o-up");
                } else {
                    $(that).find("i").attr("class", "fa fa-thumbs-o-down");
                    $(that).prev().find("i").attr("class", "fa fa-thumbs-o-up");
                }

                $(that).find("span").text(arg.down_count);
                $(that).prev().find("span").text(arg.up_count)
            }
        }
    })
}