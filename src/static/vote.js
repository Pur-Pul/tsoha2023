function vote(post_id) {
    fetch("/post/"+post_id+"/vote", {
        method: "POST",
        credentials: "include",
        body: JSON.stringify({'id': post_id, 'value': 1}),
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