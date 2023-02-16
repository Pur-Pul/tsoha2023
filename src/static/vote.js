function vote(post_id, like) {
    if (like) score = 1;
    else score = -1;
    fetch("/post/"+post_id+"/vote", {
        method: "POST",
        credentials: "include",
        body: JSON.stringify({'id': post_id, 'value': score}),
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