function reply(post_id) {
    content = window.prompt("Please enter your reply.","");
    if (content == null) {
        return;
    }
    fetch("/post/"+post_id+"/reply", {
        method: "POST",
        credentials: "include",
        body: JSON.stringify({'id': post_id, 'content': content}),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json",
            "X-CSRFToken": csrf_token
        })
    })
    .then(function (response) {
        if (response.status != 200) {
            invoke_error(`Error: ${response.status}`);
            return;
        } else {
            window.location.reload();
        }
    })
}

function generate_reply(id, content, username, time) {
    var paragraph = document.getElementById("reply_"+id);
    paragraph.innerHTML = content + "<p class='indent'>" +"- "+ username +" replied " + simplify_timestamp(time) + "</p>";
}