$(document).ready(function () {
    $("#lista_menu").load("web/menu")
    user = sessionStorage.getItem('user')
    login = sessionStorage.getItem('login')
    if (login && user != 'ial' && user != 'admin') {
        payload = {
            "user": user
        }
        data = http.request({
            path: 'api/licensa/',
            data: payload,
            body: payload,
            stringify: false
        })
        if (data?.data.licensa == "false") {
            kill = http.request({
                path: 'automacao/chave_preco/kill'
            })
            deslogar()
        }
    } else if (user != 'ial' && user != 'admin') {
        deslogar()
    }    

    level_token = sessionStorage.getItem('token_level')
    if (level_token >= 99) {
        chamaPage('reajuste/reajuste.html','#index-pages')    
    }else{
        chamaPage('dashboard/dashboard.html','#index-pages')
    }
})
