
document.addEventListener("DOMContentLoaded", () => {
  // Gráfico de Promedios por Categoría
  var ctxPromedios = document.getElementById("promediosCategorias").getContext("2d")
  var chartPromedios = new Chart(ctxPromedios, {
    type: "bar",
    data: {
      labels: categorias,
      datasets: [
        {
          label: "Promedio",
          data: promedios,
          backgroundColor: "rgba(7, 121, 228, 0.6)",
          borderColor: "rgba(7, 121, 228, 1)",
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          max: 10,
        },
      },
      plugins: {
        legend: {
          display: true,
          position: "top",
        },
        title: {
          display: true,
          text: "Promedios por Categoría",
        },
      },
    },
  })

  // Gráfico de Distribución General
  var ctxDistribucion = document.getElementById("distribucionGeneral").getContext("2d")
  var chartDistribucion = new Chart(ctxDistribucion, {
    type: "pie",
    data: {
      labels: distribucion_labels,
      datasets: [
        {
          data: distribucion_values,
          backgroundColor: [
            "rgba(255, 99, 132, 0.6)",
            "rgba(54, 162, 235, 0.6)",
            "rgba(255, 206, 86, 0.6)",
            "rgba(75, 192, 192, 0.6)",
            "rgba(153, 102, 255, 0.6)",
            "rgba(255, 159, 64, 0.6)",
            "rgba(201, 203, 207, 0.6)",
            "rgba(255, 205, 86, 0.6)",
            "rgba(75, 192, 192, 0.6)",
            "rgba(54, 162, 235, 0.6)",
          ],
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: "right",
        },
        title: {
          display: true,
          text: "Distribución por Categoría",
        },
      },
    },
  })

  // Gráfico de Progreso en el Tiempo
  var ctxProgreso = document.getElementById("progresoTiempo").getContext("2d")
  var chartProgreso = new Chart(ctxProgreso, {
    type: "line",
    data: {
      labels: progreso_fechas,
      datasets: [
        {
          label: "Promedio",
          data: progreso_valores,
          fill: false,
          borderColor: "rgb(75, 192, 192)",
          tension: 0.1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          max: 10,
        },
      },
      plugins: {
        legend: {
          display: true,
          position: "top",
        },
        title: {
          display: true,
          text: "Progreso en el Tiempo",
        },
      },
    },
  })

  // Filtro de categorías
  document.getElementById("filtroCategoria").addEventListener("change", function () {
    var categoria = this.value
    var formData = new FormData()
    formData.append("categoria", categoria)

    fetch("/admin/filtrar_datos", {
      method: "POST",
      body: formData,
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Error en la respuesta del servidor: " + response.status)
        }
        return response.json()
      })
      .then((data) => {
        // Actualizar el promedio general
        document.getElementById("promedioGeneral").textContent = data.promedio_general

        // Actualizar el gráfico de distribución
        chartDistribucion.data.labels = data.distribucion_labels
        chartDistribucion.data.datasets[0].data = data.distribucion_values

        // Actualizar el título del gráfico de distribución según la categoría seleccionada
        if (categoria === "todas") {
          chartDistribucion.options.plugins.title.text = "Distribución por Categoría"
        } else {
          chartDistribucion.options.plugins.title.text = "Distribución por Pregunta en " + categoria
        }

        chartDistribucion.update()

        // Actualizar el gráfico de progreso en el tiempo
        chartProgreso.data.labels = data.progreso_fechas
        chartProgreso.data.datasets[0].data = data.progreso_valores
        chartProgreso.update()
      })
      .catch((error) => {
        console.error("Error:", error)
        alert("Ocurrió un error al filtrar los datos: " + error.message)
      })
  })
})

