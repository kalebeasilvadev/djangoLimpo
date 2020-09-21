function carrega_dashboard() {

    data = http.request({
        path: 'api/abast/'
    })
    data_baixa = http.request({
        path: 'api/ascompare/'
    })
    if(data_baixa.status == "success"){
        if(data_baixa.data?.errosBaixa){
            erros = data_baixa.data.errosBaixa
            $("#errosBaixaText").empty()
            $("#errosBaixaText").append(`Total de baixas erradas ${erros}`)
            $("#errosBaixa").show()
        }        
    }
    data_semana = []

    if (data.data.mes.total) {
        total_mes = numberToReal(data.data.mes.total, 2)
    } else {
        total_mes = numberToReal(0, 2)
    }
    if (data.data.semana.total) {
        total_semana = numberToReal(data.data.semana.total, 2)
    } else {
        total_semana = numberToReal(0, 2)
    }
    if (data.data.dia.total) {
        total_dia = numberToReal(data.data.dia.total, 2)
    } else {
        total_dia = numberToReal(0, 2)
    }

    if (data.data.mes.total_quantidade) {
        total_mes_quantidade = numberToLitros(data.data.mes.total_quantidade, 2)
    } else {
        total_mes_quantidade = numberToLitros(0, 2)
    }
    if (data.data.semana.total_quantidade) {
        total_semana_quantidade = numberToLitros(data.data.semana.total_quantidade, 2)
    } else {
        total_semana_quantidade = numberToLitros(0, 2)
    }
    if (data.data.dia.total_quantidade) {
        total_dia_quantidade = numberToLitros(data.data.dia.total_quantidade, 2)
    } else {
        total_dia_quantidade = numberToLitros(0, 2)
    }


    $("#valor_mensal").html(total_mes)
    $("#valor_semana").html(total_semana)
    $("#valor_diario").html(total_dia)

    $("#valor_mensal_quantidade").html(`${total_mes_quantidade} Litros`)
    $("#valor_semana_quantidade").html(`${total_semana_quantidade} Litros`)
    $("#valor_diario_quantidade").html(`${total_dia_quantidade} Litros`)

    for (x in data.data.semana.vendas) {
        data_semana[x] = data.data.semana.vendas[x]
    }

    var config_semana = {
        type: 'line',
        data: {
            labels: ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sabado', 'Domingo'],
            datasets: [{
                label: 'Vendido R$ ',
                backgroundColor: 'rgb(54, 162, 235)',
                borderColor: 'rgb(54, 162, 235)',
                data: data_semana,
                fill: false,
            }]
        },
        options: {
            responsive: true,
            title: {
                display: true,
                text: 'Abastecimentos Da Semana'
            },
            tooltips: {
                mode: 'index',
                intersect: true,
            },
            hover: {
                mode: 'nearest',
                intersect: true
            },
            scales: {
                x: {
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Dias'
                    }
                },
                y: {
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Valor'
                    }
                }
            }
        }
    };

    var ctx = document.getElementById('canvas_semana').getContext('2d');
    $('#canvas_semana').html("");
    window.semana = new Chart(ctx, config_semana);

    data_dia = []
    for (x in data.data.dia.vendas) {
        data_dia[parseInt(x)] = parseInt(data.data.dia.vendas[x])
    }

    var config_dia = {
        type: 'line',
        data: {
            labels: ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00',
                '08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00',
                '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00'],
            datasets: [{
                label: 'Vendido R$ ',
                backgroundColor: 'rgb(54, 162, 235)',
                borderColor: 'rgb(54, 162, 235)',
                data: data_dia,
                fill: false,
            }]
        },
        options: {
            responsive: true,
            title: {
                display: true,
                text: 'Abastecimentos Do Dia'
            },
            tooltips: {
                mode: 'index',
                intersect: true,
            },
            hover: {
                mode: 'nearest',
                intersect: true
            },
            scales: {
                x: {
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Dias'
                    }
                },
                y: {
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Valor'
                    }
                }
            }
        }
    };

    var ctx = document.getElementById('canvas_dia').getContext('2d');
    $('#canvas_dia').html("");
    window.dia = new Chart(ctx, config_dia);


    function getRandomColor() {
        var letters = '0123456789ABCDEF';
        var color = '#';
        for (var i = 0; i < 6; i++) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    }




    labes_tipo = []
    data_tipo = []
    color_tipo = []
    tipo_cartao = http.request({
        path: 'api/tipo/'
    })
    for (x in data.data.tipo) {
        nome = tipo_cartao.data.find(codigo => codigo.codigo == data.data.tipo[x].tipo).nome
        labes_tipo[data.data.tipo[x].tipo] = nome + "  " + numberToReal(data.data.tipo[x].total, 2)
        data_tipo[data.data.tipo[x].tipo] = numberToRealSem(data.data.tipo[x].total, 2)
        color_tipo[data.data.tipo[x].tipo] = getRandomColor()
    }
    labes_tipo = labes_tipo.filter(function () { return true });
    data_tipo = data_tipo.filter(function () { return true });
    color_tipo = color_tipo.filter(function () { return true });

    var config_tipo = {
        type: 'pie',
        data: {
            labels: labes_tipo,
            datasets: [{
                backgroundColor: color_tipo,
                data: data_tipo,
            }]
        },
        options: {
            responsive: true,
            title: {
                display: true,
                text: 'Vendas por preço do dia'
            },
            legend: {
                display: true,
                position: 'right'
            }
        }
    };

    var ctx = document.getElementById('canvas_tipo_preco').getContext('2d');
    $('#canvas_tipo_preco').html("");
    window.dia_tipo = new Chart(ctx, config_tipo);

    
    labes_tipo_litros = []
    data_tipo_litros = []
    color_tipo_litros = []
    for (x in data.data.tipo) {
        nome = tipo_cartao.data.find(codigo => codigo.codigo == data.data.tipo[x].tipo).nome
        labes_tipo_litros[data.data.tipo[x].tipo] = nome + "  " + numberToLitros(data.data.tipo[x].quantidade, 2) + " Lts"
        data_tipo_litros[data.data.tipo[x].tipo] = numberToLitrosSem(data.data.tipo[x].quantidade, 2)
        color_tipo_litros[data.data.tipo[x].tipo] = getRandomColor()
    }
    labes_tipo_litros = labes_tipo_litros.filter(function () { return true });
    data_tipo_litros = data_tipo_litros.filter(function () { return true });
    color_tipo_litros = color_tipo_litros.filter(function () { return true });
    var config_tipo = {
        type: 'pie',
        data: {
            labels: labes_tipo_litros,
            datasets: [{
                backgroundColor: color_tipo_litros,
                data: data_tipo_litros,
            }]
        },
        options: {
            responsive: true,
            title: {
                display: true,
                text: 'Vendas por litros do dia'
            },
            legend: {
                display: true,
                position: 'right'
            }
        }
    };

    var ctx = document.getElementById('canvas_tipo_litros').getContext('2d');
    $('#canvas_tipo_litros').html("");
    window.dia_tipo = new Chart(ctx, config_tipo);


    labes_tipo_mes = []
    data_tipo_mes = []
    color_tipo_mes = []
    tipo_cartao = http.request({
        path: 'api/tipo/'
    })
    for (x in data.data.tipo_mes) {
        nome = tipo_cartao.data.find(codigo => codigo.codigo == data.data.tipo_mes[x].tipo).nome
        labes_tipo_mes[data.data.tipo_mes[x].tipo] = nome + "  " + numberToReal(data.data.tipo_mes[x].total, 2)
        data_tipo_mes[data.data.tipo_mes[x].tipo] = numberToRealSem(data.data.tipo_mes[x].total, 2)
        color_tipo_mes[data.data.tipo_mes[x].tipo] = getRandomColor()
    }
    labes_tipo_mes = labes_tipo_mes.filter(function () { return true });
    data_tipo_mes = data_tipo_mes.filter(function () { return true });
    color_tipo_mes = color_tipo_mes.filter(function () { return true });

    var config_tipo_mes = {
        type: 'pie',
        data: {
            labels: labes_tipo_mes,
            datasets: [{
                backgroundColor: color_tipo_mes,
                data: data_tipo_mes,
            }]
        },
        options: {
            responsive: true,
            title: {
                display: true,
                text: 'Vendas por preço do Mês'
            },
            legend: {
                display: true,
                position: 'right'
            }
        }
    };

    var ctx = document.getElementById('canvas_tipo_preco_mes').getContext('2d');
    $('#canvas_tipo_preco_mes').html("");
    window.dia_tipo_mes = new Chart(ctx, config_tipo_mes);

    labes_tipo_mes_litros = []
    data_tipo_mes_litros = []
    color_tipo_mes_litros = []
    for (x in data.data.tipo_mes) {
        nome = tipo_cartao.data.find(codigo => codigo.codigo == data.data.tipo_mes[x].tipo).nome
        labes_tipo_mes_litros[data.data.tipo_mes[x].tipo] = nome + "  " + numberToLitros(data.data.tipo_mes[x].quantidade, 2) + " Lts"
        data_tipo_mes_litros[data.data.tipo_mes[x].tipo] = numberToLitrosSem(data.data.tipo_mes[x].quantidade, 2)
        color_tipo_mes_litros[data.data.tipo_mes[x].tipo] = getRandomColor()
    }
    labes_tipo_mes_litros = labes_tipo_mes_litros.filter(function () { return true });
    data_tipo_mes_litros = data_tipo_mes_litros.filter(function () { return true });
    color_tipo_mes_litros = color_tipo_mes_litros.filter(function () { return true });
    var config_tipo = {
        type: 'pie',
        data: {
            labels: labes_tipo_mes_litros,
            datasets: [{
                backgroundColor: color_tipo_mes_litros,
                data: data_tipo_mes_litros,
            }]
        },
        options: {
            responsive: true,
            title: {
                display: true,
                text: 'Vendas por litros do Mês'
            },
            legend: {
                display: true,
                position: 'right'
            }
        }
    };

    var ctx = document.getElementById('canvas_tipo_litros_mes').getContext('2d');
    $('#canvas_tipo_litros_mes').html("");
    window.dia_tipo_mes = new Chart(ctx, config_tipo);


    labes_tipo_semana = []
    data_tipo_semana = []
    color_tipo_semana = []
    tipo_cartao = http.request({
        path: 'api/tipo/'
    })
    for (x in data.data.tipo_semana) {
        nome = tipo_cartao.data.find(codigo => codigo.codigo == data.data.tipo_semana[x].tipo).nome
        labes_tipo_semana[data.data.tipo_semana[x].tipo] = nome + "  " + numberToReal(data.data.tipo_semana[x].total, 2)
        data_tipo_semana[data.data.tipo_semana[x].tipo] = numberToRealSem(data.data.tipo_semana[x].total, 2)
        color_tipo_semana[data.data.tipo_semana[x].tipo] = getRandomColor()
    }
    labes_tipo_semana = labes_tipo_semana.filter(function () { return true });
    data_tipo_semana = data_tipo_semana.filter(function () { return true });
    color_tipo_semana = color_tipo_semana.filter(function () { return true });
    var config_tipo_semana = {
        type: 'pie',
        data: {
            labels: labes_tipo_semana,
            datasets: [{
                backgroundColor: color_tipo_semana,
                data: data_tipo_semana,
            }]
        },
        options: {
            title: {
                display: true,
                text: 'Vendas por preço da semana'
            },
            legend: {
                display: true,
                position: 'right'
            }
        }
    };

    var ctx = document.getElementById('canvas_tipo_preco_semana').getContext('2d');
    $('#canvas_tipo_preco_semana').html("");
    window.dia_tipo_semana = new Chart(ctx, config_tipo_semana);

    labes_tipo_semana_litros = []
    data_tipo_semana_litros = []
    color_tipo_semana_litros = []
    for (x in data.data.tipo_semana) {
        nome = tipo_cartao.data.find(codigo => codigo.codigo == data.data.tipo_semana[x].tipo).nome
        labes_tipo_semana_litros[data.data.tipo_semana[x].tipo] = nome + "  " + numberToLitros(data.data.tipo_semana[x].quantidade, 2) + " Lts"
        data_tipo_semana_litros[data.data.tipo_semana[x].tipo] = numberToLitrosSem(data.data.tipo_semana[x].quantidade, 2)
        color_tipo_semana_litros[data.data.tipo_semana[x].tipo] = getRandomColor()
    }
    labes_tipo_semana_litros = labes_tipo_semana_litros.filter(function () { return true });
    data_tipo_semana_litros = data_tipo_semana_litros.filter(function () { return true });
    color_tipo_semana_litros = color_tipo_semana_litros.filter(function () { return true });
    var config_tipo = {
        type: 'pie',
        data: {
            labels: labes_tipo_semana_litros,
            datasets: [{
                backgroundColor: color_tipo_semana_litros,
                data: data_tipo_semana_litros,
            }]
        },
        options: {
            responsive: true,
            title: {
                display: true,
                text: 'Vendas por litros da Semana'
            },
            legend: {
                display: true,
                position: 'right'
            }
        }
    };

    var ctx = document.getElementById('canvas_tipo_litros_semana').getContext('2d');
    $('#canvas_tipo_litros_semana').html("");
    window.dia_tipo_semana = new Chart(ctx, config_tipo);


    // Vendas produtos


    labes_produto = []
    data_produto = []
    color_produto = []
    produto_cartao = http.request({
        path: 'api/produto/'
    })
    for (x in data.data.produto) {
        nome = produto_cartao.data.find(codigo => codigo.codigo == data.data.produto[x].produto).nome
        codigo = parseInt(data.data.produto[x].produto) < 10 ? parseInt(data.data.produto[x].produto.charCodeAt(0)) : parseInt(data.data.produto[x].produto.charCodeAt(0)+data.data.produto[x].produto.charCodeAt(1))
        labes_produto[codigo] = nome + "  " + numberToReal(data.data.produto[x].total, 2)
        data_produto[codigo] = numberToRealSem(data.data.produto[x].total, 2)
        color_produto[codigo] = getRandomColor()
    }

    labes_produto = labes_produto.filter(function () { return true });
    data_produto = data_produto.filter(function () { return true });
    color_produto = color_produto.filter(function () { return true });
    var config_produto = {
        type: 'pie',
        data: {
            labels: labes_produto,
            datasets: [{
                backgroundColor: color_produto,
                data: data_produto,
            }]
        },
        options: {
            responsive: true,
            title: {
                display: true,
                text: 'Vendas por preço do dia'
            },
            legend: {
                display: true,
                position: 'right'
            }
        }
    };

    var ctx = document.getElementById('canvas_produto_preco').getContext('2d');
    $('#canvas_produto_preco').html("");
    window.dia_produto = new Chart(ctx, config_produto);

    
    labes_produto_litros = []
    data_produto_litros = []
    color_produto_litros = []
    for (x in data.data.produto) {
        nome = produto_cartao.data.find(codigo => codigo.codigo == data.data.produto[x].produto).nome
        codigo = parseInt(data.data.produto[x].produto) < 10 ? parseInt(data.data.produto[x].produto.charCodeAt(0)) : parseInt(data.data.produto[x].produto.charCodeAt(0)+data.data.produto[x].produto.charCodeAt(1))
        labes_produto_litros[codigo] = nome + "  " + numberToLitros(data.data.produto[x].quantidade, 2) + " Lts"
        data_produto_litros[codigo] = numberToLitrosSem(data.data.produto[x].quantidade, 2)
        color_produto_litros[codigo] = getRandomColor()
    }
    labes_produto_litros = labes_produto_litros.filter(function () { return true });
    data_produto_litros = data_produto_litros.filter(function () { return true });
    color_produto_litros = color_produto_litros.filter(function () { return true });
    var config_produto_mes = {
        type: 'pie',
        data: {
            labels: labes_produto_litros,
            datasets: [{
                backgroundColor: color_produto_litros,
                data: data_produto_litros,
            }]
        },
        options: {
            responsive: true,
            title: {
                display: true,
                text: 'Vendas por litros do dia'
            },
            legend: {
                display: true,
                position: 'right'
            }
        }
    };

    var ctx = document.getElementById('canvas_produto_litros').getContext('2d');
    $('#canvas_produto_litros').html("");
    window.dia_produto = new Chart(ctx, config_produto);


    labes_produto_mes = []
    data_produto_mes = []
    color_produto_mes = []
    for (x in data.data.produto_mes) {
        nome = produto_cartao.data.find(codigo => codigo.codigo == data.data.produto_mes[x].produto).nome
        codigo = parseInt(data.data.produto_mes[x].produto) < 10 ? parseInt(data.data.produto_mes[x].produto.charCodeAt(0)) : parseInt(data.data.produto_mes[x].produto.charCodeAt(0)+data.data.produto_mes[x].produto.charCodeAt(1))
        labes_produto_mes[codigo] = nome + "  " + numberToReal(data.data.produto_mes[x].total, 2)
        data_produto_mes[codigo] = numberToRealSem(data.data.produto_mes[x].total, 2)
        color_produto_mes[codigo] = getRandomColor()
    }
    labes_produto_mes = labes_produto_mes.filter(function () { return true });
    data_produto_mes = data_produto_mes.filter(function () { return true });
    color_produto_mes = color_produto_mes.filter(function () { return true });

    var config_produto_mes = {
        type: 'pie',
        data: {
            labels: labes_produto_mes,
            datasets: [{
                backgroundColor: color_produto_mes,
                data: data_produto_mes,
            }]
        },
        options: {
            responsive: true,
            title: {
                display: true,
                text: 'Vendas por preço do Mês'
            },
            legend: {
                display: true,
                position: 'right'
            }
        }
    };

    var ctx = document.getElementById('canvas_produto_preco_mes').getContext('2d');
    $('#canvas_produto_preco_mes').html("");
    window.dia_produto_mes = new Chart(ctx, config_produto_mes);

    labes_produto_mes_litros = []
    data_produto_mes_litros = []
    color_produto_mes_litros = []
    for (x in data.data.produto_mes) {
        nome = produto_cartao.data.find(codigo => codigo.codigo == data.data.produto_mes[x].produto).nome
        codigo = parseInt(data.data.produto_mes[x].produto) < 10 ? parseInt(data.data.produto_mes[x].produto.charCodeAt(0)) : parseInt(data.data.produto_mes[x].produto.charCodeAt(0)+data.data.produto_mes[x].produto.charCodeAt(1))
        labes_produto_mes_litros[codigo] = nome + "  " + numberToLitros(data.data.produto_mes[x].quantidade, 2) + " Lts"
        data_produto_mes_litros[codigo] = numberToLitrosSem(data.data.produto_mes[x].quantidade, 2)
        color_produto_mes_litros[codigo] = getRandomColor()
    }
    labes_produto_mes_litros = labes_produto_mes_litros.filter(function () { return true });
    data_produto_mes_litros = data_produto_mes_litros.filter(function () { return true });
    color_produto_mes_litros = color_produto_mes_litros.filter(function () { return true });
    var config_produto = {
        type: 'pie',
        data: {
            labels: labes_produto_mes_litros,
            datasets: [{
                backgroundColor: color_produto_mes_litros,
                data: data_produto_mes_litros,
            }]
        },
        options: {
            responsive: true,
            title: {
                display: true,
                text: 'Vendas por litros do Mês'
            },
            legend: {
                display: true,
                position: 'right'
            }
        }
    };

    var ctx = document.getElementById('canvas_produto_litros_mes').getContext('2d');
    $('#canvas_produto_litros_mes').html("");
    window.dia_produto_mes = new Chart(ctx, config_produto);


    labes_produto_semana = []
    data_produto_semana = []
    color_produto_semana = []
    for (x in data.data.produto_semana) {
        nome = produto_cartao.data.find(codigo => codigo.codigo == data.data.produto_semana[x].produto).nome
        codigo = parseInt(data.data.produto_semana[x].produto) < 10 ? parseInt(data.data.produto_semana[x].produto.charCodeAt(0)) : parseInt(data.data.produto_semana[x].produto.charCodeAt(0)+data.data.produto_semana[x].produto.charCodeAt(1))
        labes_produto_semana[codigo] = nome + "  " + numberToReal(data.data.produto_semana[x].total, 2)
        data_produto_semana[codigo] = numberToRealSem(data.data.produto_semana[x].total, 2)
        color_produto_semana[codigo] = getRandomColor()
    }
    labes_produto_semana = labes_produto_semana.filter(function () { return true });
    data_produto_semana = data_produto_semana.filter(function () { return true });
    color_produto_semana = color_produto_semana.filter(function () { return true });
    var config_produto_semana = {
        type: 'pie',
        data: {
            labels: labes_produto_semana,
            datasets: [{
                backgroundColor: color_produto_semana,
                data: data_produto_semana,
            }]
        },
        options: {
            title: {
                display: true,
                text: 'Vendas por preço da semana'
            },
            legend: {
                display: true,
                position: 'right'
            }
        }
    };

    var ctx = document.getElementById('canvas_produto_preco_semana').getContext('2d');
    $('#canvas_produto_preco_semana').html("");
    window.dia_produto_semana = new Chart(ctx, config_produto_semana);

    labes_produto_semana_litros = []
    data_produto_semana_litros = []
    color_produto_semana_litros = []
    for (x in data.data.produto_semana) {
        nome = produto_cartao.data.find(codigo => codigo.codigo == data.data.produto_semana[x].produto).nome
        codigo = parseInt(data.data.produto_semana[x].produto) < 10 ? parseInt(data.data.produto_semana[x].produto.charCodeAt(0)) : parseInt(data.data.produto_semana[x].produto.charCodeAt(0)+data.data.produto_semana[x].produto.charCodeAt(1))
        labes_produto_semana_litros[codigo] = nome + "  " + numberToLitros(data.data.produto_semana[x].quantidade, 2) + " Lts"
        data_produto_semana_litros[codigo] = numberToLitrosSem(data.data.produto_semana[x].quantidade, 2)
        color_produto_semana_litros[codigo] = getRandomColor()
    }
    labes_produto_semana_litros = labes_produto_semana_litros.filter(function () { return true });
    data_produto_semana_litros = data_produto_semana_litros.filter(function () { return true });
    color_produto_semana_litros = color_produto_semana_litros.filter(function () { return true });
    var config_produto = {
        type: 'pie',
        data: {
            labels: labes_produto_semana_litros,
            datasets: [{
                backgroundColor: color_produto_semana_litros,
                data: data_produto_semana_litros,
            }]
        },
        options: {
            responsive: true,
            title: {
                display: true,
                text: 'Vendas por litros da Semana'
            },
            legend: {
                display: true,
                position: 'right'
            }
        }
    };

    var ctx = document.getElementById('canvas_produto_litros_semana').getContext('2d');
    $('#canvas_produto_litros_semana').html("");
    window.dia_produto_semana = new Chart(ctx, config_produto);
}

carrega_dashboard()


function timeout() {
    setTimeout(function () {
        if ($('#canvas_semana').length) {
            carrega_dashboard();
            timeout();
        }
    }, 60000);
}
timeout()