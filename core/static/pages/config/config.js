function atualiza() {
  var id = $("#idconfig").val();
  var host = $("#config_host").val();
  var porta = $("#config_port").val();
  var host_app = $("#config_host_app").val();
  var porta_app = $("#config_port_app").val();
  var automacao = $("#config_automacao").val();
  var tempo_cmd = $("#config_tempo_cmd").val();
  var start_auto = $("#config_start_auto").val();
  var emulado = $("#config_emulado").val();
  if (host != "" && porta != "") {
    payload = {
      host: host,
      porta: porta,
      automacao: automacao,
      tempo_cmd: tempo_cmd,
      start_auto: start_auto,
      host_app: host_app,
      porta_app: porta_app,
      emulado: emulado,
    };
    data = http.request({
      metodo: "PATCH",
      path: "api/config/" + id + "/",
      data: payload,
    });
    if (data.status == "success") {
      alertas("Configuraçoes Salvas");
      carrega_config();
    }
  } else {
    if (host == "") {
      alert("Preencha o campo host");
    } else if (porta == "") {
      alert("Preencha o campo porta");
    } else if (automacao == "") {
      alert("Preencha o campo Automação");
    } else if (tempo_cmd == "") {
      alert("Preencha o campo Tempo CMD");
    } else if (start_auto == "") {
      alert("Preencha o campo Auto Start");
    }
  }
}

function carrega_config() {
  var id = $("#idconfig").val();
  data = http.request({
    path: "api/config/" + id + "/",
  });
  if (data.status == "success") {
    data = data.data;
    $("#idconfig").val(data.id);
    $("#config_host").val(data.host);
    $("#config_automacao").val(data.automacao);
    $("#config_tempo_cmd").val(data.tempo_cmd);
    $("#config_start_auto").val(Number(data.start_auto));
    $("#config_host_app").val(data.host_app);
    $("#config_port_app").val(data.porta_app);
    $("#config_emulado").val(Number(data.emulado));
    portaAuto(data.automacao)
    $("#config_port").val(data.porta);
  } else {
    payload = {
      host: "localhost",
      porta: "1771",
      automacao: 1,
      tempo_cmd: 0.5,
      start_auto: 0,
      host_app: "serversincronia.ddns.net",
      porta_app: 42124,
    };
    data = http.request({
      metodo: "Post",
      path: "api/config/",
      data: payload,
    });
  }
}
carrega_config();
$("#config_port").keypress(function () {
  return event.charCode >= 48 && event.charCode <= 57;
});
$("#config_port_app").keypress(function () {
  return event.charCode >= 48 && event.charCode <= 57;
});


function portaAuto(tipo){
  $("#config_port").empty()
  if(tipo == 0){
    $("#config_port").append('<option value="2001">2001</option>')
  }else if(tipo == 1){
    $("#config_port").append('<option value="2001">2001</option>')
    $("#config_port").append('<option value="1771">1771</option>')
    $("#config_port").append('<option value="771">771</option>')
    $("#config_port").append('<option value="857">857</option>')
  }else if(tipo == 2){
    $("#config_port").append('<option value="2001">2001</option>')
    $("#config_port").append('<option value="1771">1771</option>')
    $("#config_port").append('<option value="771">771</option>')
    $("#config_port").append('<option value="857">857</option>')
  }else if(tipo == 3){
    for (let index = 5120; index <= 5150; index++) {
      $("#config_port").append(`<option value="${index}">${index}</option>`)
    }
  }else if(tipo == 4){
    $("#config_port").append('<option value="2001">2001</option>')
    $("#config_port").append('<option value="1771">1771</option>')
    $("#config_port").append('<option value="771">771</option>')
    $("#config_port").append('<option value="857">857</option>')
  }
}