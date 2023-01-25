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
ctx.fillStyle = "white";
ctx.fillRect(0,0,CANVAS_WIDTH,CANVAS_HEIGHT);

//listeners
document.addEventListener('mousedown', start);
document.addEventListener('mousedown', draw)
document.addEventListener('mouseup', stop);

function updateColorPicker() {
    colorCtx = colorPicker.getContext("2d");
    colorCtx.fillStyle = RGBtoHex()
    colorCtx.fillRect(0, 0, colorPicker.clientWidth, colorPicker.clientHeight);
}
updateColorPicker();

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

function start(event) {
    document.addEventListener('mousemove', draw);
    reposition(event);
}

function reposition(event) {
    coordinates.x = Math.floor((event.clientX - canvas.offsetLeft)/scale);
    coordinates.y = Math.floor((event.clientY - canvas.offsetTop)/scale);
}

function stop() {
    document.removeEventListener('mousemove', draw);
}

function draw(event) {
    ctx.beginPath();
    ctx.fillStyle = RGBtoHex();
    reposition(event);
    ctx.fillRect(coordinates.x, coordinates.y, 1, 1);
    ctx.fill();
}
