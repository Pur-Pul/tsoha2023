function constuct_text(key, times) {
    if (times[key] == 1) {
        text = key;
    } else {
        text = key+"s";
    }
    return times[key] + " " + text + " ago.";
}

function simplify_timestamp(timestamp) {
    const second = 1000;
    const minute = second * 60;
    const hour = minute * 60;
    const day = hour * 24;
    const year = day * 365;
    let old_date = new Date(timestamp+"+02:00");
    const current_date = new Date();
    times = {
    "year" : Math.round((current_date.getTime() - old_date.getTime()) / year),
    "day" : Math.round((current_date.getTime() - old_date.getTime()) / day),
    "hour" : Math.round((current_date.getTime() - old_date.getTime()) / hour),
    "minute" : Math.round((current_date.getTime() - old_date.getTime()) / minute)
    };
    if (times['year']) {
        return constuct_text('year', times);
    } else if (times['day']) {
        return constuct_text('day', times);
    } else if (times['hour']) {
        return constuct_text('hour', times);
    } else if (times['minute']) {
        return constuct_text('minute', times);
    } else {
        return "right now.";
    }
}