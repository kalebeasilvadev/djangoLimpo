function loga() {
    user = $("#usuario").val();
    user = user.trim();
    senha = $("#password").val();
    senha = senha.trim();

    $("#alert-erro").hide()
    $("#alert-user").hide()
    $("#alert-pass").hide()
    $("#alert-validade").hide()
    if (user == '') {
        $("#alert-user").show()
    }
    if (senha == '') {
        $("#alert-pass").show()
    }

    if (user != "" && senha != "") {
        payload = {
            "username": user,
            "password": senha
        }
        data = http.request({
            metodo: 'POST',
            path: 'api/token/',
            data: payload
        })

        if (data?.status == "success") {
            data = data.data
            licensa = http.request({
                path: 'api/licensa/?user='+user
            })
            sessionStorage.setItem("token", data.access)
            sessionStorage.setItem("token_level", data.nivel)
            sessionStorage.setItem("user", data.username)
            sessionStorage.setItem("login", "true")
            $("#corpo").empty();
            location.reload()
        } else {
            data = http.request({
                path: 'api/config_user/',
                data: { "user": user },
                stringify: false
            })
            if (data?.data?.status == "ok") {
                data = http.request({
                    metodo: 'POST',
                    path: 'api/token/',
                    data: payload
                })

                if (data?.status == "success") {
                    data = data.data
                    sessionStorage.setItem("token", data.access)
                    sessionStorage.setItem("token_level", data.nivel)
                    sessionStorage.setItem("user", data.username)
                    sessionStorage.setItem("login", "true")
                    $("#corpo").empty();
                    location.reload()
                }
            }
            else {
                $('#alert_message').empty()
                $('#alert_message').append(`<span>${data?.message?.message}</span>`)
                $('#alert_message').show()
            }
        }
    }
}
$(document).keypress(function (e) {
    if (e.which == 13) $('#buttonLogin').click();
});