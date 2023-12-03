const toggle_sententree = document.getElementById("mostrar_ocultar_sententree");
const select_dataset = document.getElementById("select_dataset");
const eliminar_nodo = document.getElementById("eliminar_nodo");
const buscar_topico = document.getElementById("buscar_topico");
const mezclar_topico = document.getElementById("mezclar_topico");

toggle_sententree.addEventListener("click", () => {
  if (escogidos.length === 0) {
    alert("Debes escoger almenos un nodo.");
    return;
  }
  //console.log("ESCOGIDOS " + escogidos);
  $.ajax({
    type: "POST",
    url: "{{url_for('crearSententree')}}",
    data: { escogidos: escogidos },
    success: function (result) {
      graph = result;
      //console.log(graph);
      update();
      escogidos = [];
    },
  });
});
select_dataset.addEventListener("click", () => {
  var valor = document.querySelector("#select_dataset").value;
  if (dbName !== valor) {
    // console.log("cambiando bd")
    const loadingDom = document.getElementById("loader-container");
    limpiarPantalla();
    loadingDom.setAttribute("id", "loader");
    $.ajax({
      type: "POST",
      url: "{{url_for('cambiarDataset')}}",
      data: {
        dataSetName: valor,
      },
      success: function (result) {
        graph = result;
        loadingDom.setAttribute("id", "loader-container");

        update();
        escogidos = [];
      },
    });
    dbName = valor;
  }
});

eliminar_nodo.addEventListener("click", () => {
  if (escogidos.length === 0) {
    alert("Debes escoger almenos un nodo.");
    return;
  }
  $.ajax({
    type: "POST",
    url: "{{url_for('eliminarNodo')}}",
    data: { escogidos: escogidos },
    success: function (result) {
      graph = result;
      //console.log(graph);
      update();
      escogidos = [];
    },
  });
});

buscar_topico.addEventListener("click", () => {
  var valor = document.querySelector("#numTopic").value;
  if (escogidos.length === 0) {
    alert("Debes escoger almenos un nodo.");
    return;
  }
  console.log("enviando buscarTopicos");
  $.ajax({
    type: "POST",
    url: "{{url_for('buscarTopicos')}}",
    data: {
      escogidos: escogidos,
      numeroTopicos: valor,
    },
    success: function (result) {
      //console.log("GAAAAAAAAAA")
      //console.log(result);
      graph = result;
      //console.log(graph);
      update();
      escogidos = [];
    },
  });
});

mezclar_topico.addEventListener("click", () => {
  if (escogidos.length < 2) {
    alert("Debes escoger almenos 2 nodos.");
    return;
  }
  console.log("enviando mezclarTopicos");
  $.ajax({
    type: "POST",
    url: "{{url_for('mezclarTopicos')}}",
    data: {
      escogidos: escogidos,
    },
    success: function (result) {
      graph = result;
      update();
      escogidos = [];
    },
  });
});
