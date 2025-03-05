document.addEventListener("DOMContentLoaded", () => {
  // Variables globales para almacenar las instancias de los gráficos
  let chartDistribucion
  let chartCategorias
  let chartEdad
  let chartSexo
  let chartRadar
  let chartTendencia
  let chartCorrelacion

  // Función para obtener datos JSON de forma segura
  function getJsonData(elementId) {
    try {
      const element = document.getElementById(elementId)
      if (!element) return null
      const jsonStr = element.getAttribute("data-json")
      return JSON.parse(jsonStr)
    } catch (error) {
      console.error(`Error al parsear JSON desde ${elementId}:`, error)
      return null
    }
  }

  // Datos iniciales pasados desde el backend
  const datosCalificaciones = getJsonData("datos-calificaciones") || { labels: [], data: [] }
  const datosCategorias = getJsonData("datos-categorias") || { labels: [], data: [] }
  const datosEdad = getJsonData("datos-edad") || { labels: [], data: [] }
  const datosSexo = getJsonData("datos-sexo") || { labels: [], data: [] }
  const datosRadar = getJsonData("datos-radar") || { labels: [], data: [] }
  const datosTendencia = getJsonData("datos-tendencia") || { labels: [], data: [] }
  const datosCorrelacion = getJsonData("datos-correlacion") || { labels: [], datasets: [] }

  // Configuración de colores
  const coloresCategorias = [
    "rgba(255, 99, 132, 0.7)",
    "rgba(54, 162, 235, 0.7)",
    "rgba(255, 206, 86, 0.7)",
    "rgba(75, 192, 192, 0.7)",
    "rgba(153, 102, 255, 0.7)",
    "rgba(255, 159, 64, 0.7)",
    "rgba(199, 199, 199, 0.7)",
    "rgba(83, 102, 255, 0.7)",
    "rgba(40, 159, 64, 0.7)",
    "rgba(210, 99, 132, 0.7)",
  ]

  // 1. Gráfico de distribución de calificaciones
  const ctxDistribucion = document.getElementById("distribucionCalificaciones").getContext("2d")
  chartDistribucion = new Chart(ctxDistribucion, {
    type: "bar",
    data: {
      labels: datosCalificaciones.labels,
      datasets: [
        {
          label: "Frecuencia",
          data: datosCalificaciones.data,
          backgroundColor: "rgba(54, 162, 235, 0.7)",
          borderColor: "rgba(54, 162, 235, 1)",
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
        },
        x: {
          title: {
            display: true,
            text: "Calificación",
          },
        },
      },
      plugins: {
        title: {
          display: true,
          text: "Distribución de Calificaciones",
        },
        legend: {
          display: false,
        },
      },
    },
  })

  // 2. Gráfico de calificaciones por categoría
  const ctxCategorias = document.getElementById("calificacionesCategorias").getContext("2d")
  chartCategorias = new Chart(ctxCategorias, {
    type: "bar",
    data: {
      labels: datosCategorias.labels,
      datasets: [
        {
          label: "Calificación Promedio",
          data: datosCategorias.data,
          backgroundColor: coloresCategorias.slice(0, datosCategorias.labels.length),
          borderColor: coloresCategorias
            .slice(0, datosCategorias.labels.length)
            .map((color) => color.replace("0.7", "1")),
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
        title: {
          display: true,
          text: "Calificación Promedio por Categoría",
        },
      },
    },
  })

  // 3. Gráfico de calificaciones por grupo de edad
  const ctxEdad = document.getElementById("calificacionesEdad").getContext("2d")
  chartEdad = new Chart(ctxEdad, {
    type: "bar",
    data: {
      labels: datosEdad.labels,
      datasets: [
        {
          label: "Calificación Promedio",
          data: datosEdad.data,
          backgroundColor: "rgba(255, 159, 64, 0.7)",
          borderColor: "rgba(255, 159, 64, 1)",
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
        title: {
          display: true,
          text: "Calificación Promedio por Grupo de Edad",
        },
      },
    },
  })

  // 4. Gráfico de calificaciones por sexo
  const ctxSexo = document.getElementById("calificacionesSexo").getContext("2d")
  chartSexo = new Chart(ctxSexo, {
    type: "bar",
    data: {
      labels: datosSexo.labels,
      datasets: [
        {
          label: "Calificación Promedio",
          data: datosSexo.data,
          backgroundColor: ["rgba(54, 162, 235, 0.7)", "rgba(255, 99, 132, 0.7)", "rgba(75, 192, 192, 0.7)"].slice(
            0,
            datosSexo.labels.length,
          ),
          borderColor: ["rgba(54, 162, 235, 1)", "rgba(255, 99, 132, 1)", "rgba(75, 192, 192, 1)"].slice(
            0,
            datosSexo.labels.length,
          ),
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
        title: {
          display: true,
          text: "Calificación Promedio por Sexo",
        },
      },
    },
  })

  // 5. Gráfico de radar para el perfil
  const ctxRadar = document.getElementById("perfilRadar").getContext("2d")
  chartRadar = new Chart(ctxRadar, {
    type: "radar",
    data: {
      labels: datosRadar.labels,
      datasets: [
        {
          label: "Perfil Promedio",
          data: datosRadar.data,
          backgroundColor: "rgba(54, 162, 235, 0.2)",
          borderColor: "rgba(54, 162, 235, 1)",
          pointBackgroundColor: "rgba(54, 162, 235, 1)",
          pointBorderColor: "#fff",
          pointHoverBackgroundColor: "#fff",
          pointHoverBorderColor: "rgba(54, 162, 235, 1)",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          angleLines: {
            display: true,
          },
          suggestedMin: 0,
          suggestedMax: 10,
        },
      },
      plugins: {
        title: {
          display: true,
          text: "Perfil de la Ruleta de la Vida",
        },
      },
    },
  })

  // 6. Gráfico de tendencia temporal
  const ctxTendencia = document.getElementById("tendenciaTemporal").getContext("2d")
  chartTendencia = new Chart(ctxTendencia, {
    type: "line",
    data: {
      labels: datosTendencia.labels,
      datasets: [
        {
          label: "Calificación Promedio",
          data: datosTendencia.data,
          fill: false,
          backgroundColor: "rgba(75, 192, 192, 0.7)",
          borderColor: "rgba(75, 192, 192, 1)",
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
        title: {
          display: true,
          text: "Tendencia de Calificaciones en el Tiempo",
        },
      },
    },
  })

  // 7. Gráfico de correlación entre categorías (heatmap)
  const ctxCorrelacion = document.getElementById("correlacionCategorias").getContext("2d")

  // Para el heatmap, usamos un enfoque diferente ya que Chart.js no tiene un tipo de gráfico heatmap nativo
  // Creamos una visualización simple de correlación
  chartCorrelacion = new Chart(ctxCorrelacion, {
    type: "bar",
    data: {
      labels: datosCorrelacion.labels,
      datasets: [
        {
          label: "Correlación",
          data: datosCorrelacion.datasets.length > 0 ? datosCorrelacion.datasets[0].data.map((d) => d.v) : [],
          backgroundColor: "rgba(75, 192, 192, 0.7)",
          borderColor: "rgba(75, 192, 192, 1)",
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: "y",
      plugins: {
        title: {
          display: true,
          text: "Correlación entre Categorías",
        },
        legend: {
          display: false,
        },
      },
    },
  })

  // Manejo de filtros
  document.getElementById("filtroCategoria").addEventListener("change", aplicarFiltros)
  document.getElementById("filtroEdad").addEventListener("change", aplicarFiltros)
  document.getElementById("filtroSexo").addEventListener("change", aplicarFiltros)

  function aplicarFiltros() {
    const categoria = document.getElementById("filtroCategoria").value
    const edad = document.getElementById("filtroEdad").value
    const sexo = document.getElementById("filtroSexo").value

    // Crear FormData para enviar al servidor
    const formData = new FormData()
    formData.append("categoria", categoria)
    formData.append("edad", edad)
    formData.append("sexo", sexo)

    // Enviar solicitud al servidor
    fetch("/admin/filtrar_analisis", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        // Actualizar estadísticas
        document.getElementById("promedioGeneral").textContent = data.promedio_general
        document.getElementById("desviacionEstandar").textContent = data.desviacion_estandar
        document.getElementById("totalRespuestas").textContent = data.total_respuestas
        document.getElementById("usuariosUnicos").textContent = data.usuarios_unicos

        // Actualizar insights
        actualizarInsights(data.insights)

        // Actualizar gráficos
        if (data.graficos) {
          actualizarGraficos(data.graficos)
        }
      })
      .catch((error) => {
        console.error("Error al filtrar datos:", error)
        alert("Ocurrió un error al filtrar los datos.")
      })
  }

  function actualizarInsights(insights) {
    // Actualizar categorías destacadas
    const categoriasDestacadas = document.getElementById("categoriasDestacadas")
    categoriasDestacadas.innerHTML = ""
    if (insights.top_categorias && insights.top_categorias.length > 0) {
      insights.top_categorias.forEach((cat) => {
        const li = document.createElement("li")
        li.innerHTML = `<strong>${cat.nombre}:</strong> ${cat.valor.toFixed(2)}/10`
        categoriasDestacadas.appendChild(li)
      })
    } else {
      const li = document.createElement("li")
      li.textContent = "No hay datos suficientes para mostrar categorías destacadas."
      categoriasDestacadas.appendChild(li)
    }

    // Actualizar áreas de oportunidad
    const areasOportunidad = document.getElementById("areasOportunidad")
    areasOportunidad.innerHTML = ""
    if (insights.bottom_categorias && insights.bottom_categorias.length > 0) {
      insights.bottom_categorias.forEach((cat) => {
        const li = document.createElement("li")
        li.innerHTML = `<strong>${cat.nombre}:</strong> ${cat.valor.toFixed(2)}/10`
        areasOportunidad.appendChild(li)
      })
    } else {
      const li = document.createElement("li")
      li.textContent = "No hay datos suficientes para mostrar áreas de oportunidad."
      areasOportunidad.appendChild(li)
    }

    // Actualizar diferencias demográficas
    const diferenciasDemograficas = document.getElementById("diferenciasDemograficas")
    diferenciasDemograficas.innerHTML = ""
    if (insights.diferencias_demograficas && insights.diferencias_demograficas.length > 0) {
      insights.diferencias_demograficas.forEach((diff) => {
        const li = document.createElement("li")
        li.textContent = diff
        diferenciasDemograficas.appendChild(li)
      })
    } else {
      const li = document.createElement("li")
      li.textContent = "No se encontraron diferencias demográficas significativas."
      diferenciasDemograficas.appendChild(li)
    }

    // Actualizar correlaciones importantes
    const correlacionesImportantes = document.getElementById("correlacionesImportantes")
    correlacionesImportantes.innerHTML = ""
    if (insights.correlaciones_importantes && insights.correlaciones_importantes.length > 0) {
      insights.correlaciones_importantes.forEach((corr) => {
        const li = document.createElement("li")
        li.textContent = corr
        correlacionesImportantes.appendChild(li)
      })
    } else {
      const li = document.createElement("li")
      li.textContent = "No se encontraron correlaciones fuertes entre categorías."
      correlacionesImportantes.appendChild(li)
    }
  }

  function actualizarGraficos(graficos) {
    // Actualizar cada gráfico con los nuevos datos
    if (graficos.calificaciones) {
      actualizarDatosGrafico(chartDistribucion, graficos.calificaciones)
    }

    if (graficos.categorias) {
      actualizarDatosGrafico(chartCategorias, graficos.categorias)
    }

    if (graficos.edad) {
      actualizarDatosGrafico(chartEdad, graficos.edad)
    }

    if (graficos.sexo) {
      actualizarDatosGrafico(chartSexo, graficos.sexo)
    }

    if (graficos.radar) {
      actualizarDatosGrafico(chartRadar, graficos.radar)
    }

    if (graficos.tendencia) {
      actualizarDatosGrafico(chartTendencia, graficos.tendencia)
    }

    if (graficos.correlacion) {
      // Para el gráfico de correlación, necesitamos un manejo especial
      actualizarGraficoCorrelacion(chartCorrelacion, graficos.correlacion)
    }
  }

  function actualizarDatosGrafico(chart, nuevosDatos) {
    if (!chart || !nuevosDatos) return

    // Actualizar etiquetas si existen
    if (nuevosDatos.labels) {
      chart.data.labels = nuevosDatos.labels
    }

    // Actualizar datos
    if (nuevosDatos.data) {
      chart.data.datasets[0].data = nuevosDatos.data
    }

    // Si hay colores personalizados, actualizarlos
    if (nuevosDatos.backgroundColor) {
      chart.data.datasets[0].backgroundColor = nuevosDatos.backgroundColor
    }

    if (nuevosDatos.borderColor) {
      chart.data.datasets[0].borderColor = nuevosDatos.borderColor
    }

    // Actualizar el gráfico
    chart.update()
  }

  function actualizarGraficoCorrelacion(chart, nuevosDatos) {
    if (!chart || !nuevosDatos) return

    // Para el gráfico de correlación, necesitamos un manejo especial
    if (nuevosDatos.labels) {
      chart.data.labels = nuevosDatos.labels
    }

    if (nuevosDatos.datasets && nuevosDatos.datasets.length > 0) {
      // Simplificamos para mostrar solo la primera serie de datos
      chart.data.datasets[0].data = nuevosDatos.datasets[0].data.map((d) => d.v)
    }

    chart.update()
  }
})

