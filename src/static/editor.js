//Sliders
var slider = {
    red: document.getElementById("red_slider"),
    green: document.getElementById("green_slider"),
    blue: document.getElementById("blue_slider"),
    value: {
        red: document.getElementById("red"),
        green: document.getElementById("green"),
        blue: document.getElementById("blue")
    }
}

slider.red.oninput = function() {
    slider.value.red.innerHTML = this.value
    updateColorPicker();
}
slider.green.oninput = function() {
    slider.value.green.innerHTML = this.value
    updateColorPicker();
}
slider.blue.oninput = function() {
    slider.value.blue.innerHTML = this.value
    updateColorPicker();
}

//Canvas
var canvas = document.getElementById("pixelCanvas");
var colorPicker = document.getElementById("colorPicker");
var color_code_entry = document.getElementById("color_code");
var ctx = canvas.getContext("2d");


let coordinates = { x: 0, y: 0 };
let scale = canvas.clientWidth / 32;
let CANVAS_WIDTH = 32;
let CANVAS_HEIGHT = 32;
let redo_state = undefined;
ctx.fillStyle = "white";
ctx.fillRect(0,0,CANVAS_WIDTH,CANVAS_HEIGHT);

//listeners
function setup() {
    document.addEventListener('mousedown', start);
    document.addEventListener('mousedown', draw);
    document.addEventListener('mouseup', stop);
}

function updateColorPicker() {
    colorCtx = colorPicker.getContext("2d");
    colorCtx.fillStyle = RGBtoHex()
    colorCtx.fillRect(0, 0, colorPicker.clientWidth, colorPicker.clientHeight);
}
updateColorPicker();

function toggleColorPickerTool() {
    if (canvas.classList.contains('colorPickerTool')) {
        document.removeEventListener('mousedown', pick);
        setup();
    }
    else {
        document.removeEventListener('mousedown', start);
        document.removeEventListener('mousedown', draw);
        document.removeEventListener('mouseup', stop);
        document.addEventListener('mousedown', pick);
    }
    canvas.classList.toggle('colorPickerTool')
}

function pick(event) {
    reposition(event);
    const data = ctx.getImageData(coordinates.x, coordinates.y, 1, 1).data;
    slider.red.value = data[0];
    slider.red.dispatchEvent(new Event('input', {bubbles:true, cancelable:true}));
    slider.green.value = data[1];
    slider.green.dispatchEvent(new Event('input', {bubbles:true, cancelable:true}));
    slider.blue.value = data[2];
    slider.blue.dispatchEvent(new Event('input', {bubbles:true, cancelable:true}));
    updateColorPicker();
    toggleColorPickerTool();
}

function RGBtoHex() {
    red = Number(slider.red.value).toString(16);
    red = red.length == 1 ? "0" + red : red;
   
    green = Number(slider.green.value).toString(16);
    green = green.length == 1 ? "0" + green : green;
    
    blue = Number(slider.blue.value).toString(16);
    blue = blue.length == 1 ? "0" + blue : blue;
    
    hex =  "#" + red + green + blue;
    return hex;
}

let stroke = {}
let pointer = 0

function add_to_stroke() {
    if (pointer == 0) {
        stroke["color"] = RGBtoHex();
    }
    if (pointer != 0 && stroke[pointer-1].x == coordinates.x && stroke[pointer-1].y == coordinates.y) {
        return
    }
    stroke[pointer] = {};
    stroke[pointer]["x"] = coordinates.x;
    stroke[pointer]["y"] = coordinates.y;
    pointer++;
}

function start(event) {
    document.addEventListener('mousemove', draw);
    reposition(event);
}

function reposition(event) {
    coordinates.x = Math.floor((event.pageX - canvas.offsetLeft)/scale);
    coordinates.y = Math.floor((event.pageY - canvas.offsetTop)/scale);
}

function save_stroke(stroke_to_save) {
    fetch("/editor", {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(stroke_to_save),
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
        }
    })
}

function stop() {
    document.removeEventListener('mousemove', draw);
    if (pointer == 0) {
        return
    }
    redo_state = undefined;
    save_stroke(stroke);
    pointer = 0
    for (i in stroke) {
        stroke[i] = undefined;
    }
}

function draw(event) {
    reposition(event);
    if (coordinates.x >= CANVAS_WIDTH || coordinates.x < 0 || coordinates.y >= CANVAS_HEIGHT || coordinates.y < 0) {
        return
    }
    ctx.fillStyle = RGBtoHex();
    ctx.fillRect(coordinates.x, coordinates.y, 1, 1);
    add_to_stroke();
}

function undo() {
    fetch("/editor", {
        method: "POST",
        credentials: "include",
        body: JSON.stringify({'undo':true,}),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json",
            "X-CSRFToken": csrf_token
        })
    })
    .then(
        function (response) {
            if (response.status != 200) {
                invoke_error(`Error: ${response.status}`);
                return;
            }
            response.json().then(
                function (data) {
                    redo_state = data.old_action;
                   
                    for (i in data.new_action) {
                        pixel = data.new_action[i];
                        if (pixel.color == null) ctx.fillStyle = 'white';
                        else ctx.fillStyle = pixel.color;
                        if (pixel == null) continue;
                        ctx.fillRect(pixel.row_number, pixel.col_number, 1, 1);
                    }
                    

                }
            )
        }
    )
}

function redo() {
    if (redo_state == undefined) return;
    let temp_stroke = {"color": redo_state[0].color};
    for (i in redo_state) {
        ctx.fillStyle = redo_state[0].color;     
        ctx.fillRect(redo_state[i].row_number, redo_state[i].col_number, 1, 1);
        temp_stroke[i] = {};
        temp_stroke[i]["x"] = redo_state[i].row_number;
        temp_stroke[i]["y"] = redo_state[i].col_number;
    }
    save_stroke(temp_stroke);
}
