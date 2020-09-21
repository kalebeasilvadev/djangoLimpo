$(document).ready(function () {
    verificaLogin()
});

function chamaPage(path, conteiner) {
    path = path.split("/");
    $.ajax({
        url: 'web/' + path[path.length - 2],
        error: function () {
            $(conteiner).load("web/generico/generico.html");
        },
        success: function () {
            $(conteiner).load('web/' + path[path.length - 2]);
        }
    });
}

function deslogar() {
    sessionStorage.removeItem("token")
    sessionStorage.removeItem("token_level")
    sessionStorage.removeItem("user")
    sessionStorage.removeItem("login")
    $("#corpo").empty();
    $("#corpo").load("web/login");
}

function verificaLogin() {
    token = sessionStorage.getItem('token')
    if (token) {
        data = http.request({
            path: 'api/verify/',
            metodo: 'POST',
            data: { "token": token }
        })
        if (data?.data?.token == "ok") {
            $("#corpo").empty();
            $("#corpo").load("web/corpo");
        } else {
            deslogar()
        }
    }
    else {
        deslogar()
    }
}
function verificaAcesso() {
    token = sessionStorage.getItem('token')
    if (token) {
        data = http.request({
            path: 'api/verify/',
            metodo: 'POST',
            data: { "token": token }
        })
        if (data?.data?.token != "ok") {
            deslogar()
        }
    }
    else {
        deslogar()
    }
}

setTimeout(function(){ verificaAcesso(); }, 180000);

function alertas(text = null, title = null) {
    if (!title) {
        title = "PriceKey"
    }

    if (!text) {
        text = "PriceKey"
    }
    // $("#modal_msg").modal("show");
    BootstrapDialog.show({
        title: title,
        message: text,
        buttons: [{
            label: 'OK',
            action: function (dialog) {
                dialog.close();
            }
        }]
    });
}


function numberToReal(numero,casas) {
    var numero = numero.toFixed(casas).split('.');
    numero[0] = "R$ " + numero[0].split(/(?=(?:...)*$)/).join('.');
    return numero.join(',');
}
function numberToRealSem(numero,casas) {
    var numero = numero.toFixed(casas).split('.');
    return numero.join('.');
}
function numberToLitros(numero,casas) {
    var numero = numero.toFixed(casas).split('.');
    numero[0] = numero[0].split(/(?=(?:...)*$)/).join('.');
    return numero.join(',');
}
function numberToLitrosSem(numero,casas) {
    var numero = numero.toFixed(casas).split('.');
    return numero.join('.');
}