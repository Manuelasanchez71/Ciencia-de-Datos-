document.addEventListener("DOMContentLoaded", () => {
  // Variables globales para almacenar las instancias de los gráficos
  let chartDistribucion
  let chartCategorias
  let chartEdad
  let chartSexo
  let chartRadar
  let chartTendencia
  let chartCorrelacion

  // Modificar la función getJsonData para manejar valores null
  function getJsonData(elementId) {
    try {
      const element = document.getElementById(elementId)
      if (!element) return null
      const jsonStr = element.getAttribute("data-json")
      const data = JSON.parse(jsonStr)

      // Si hay datos, asegurarse de que los valores NaN o null se manejen correctamente
      if (data && data.data) {
        data.data = data.data.map((val) => (val === null ? 0 : val))
      }

      return data
    } catch (error) {
      console.error(`Error al parsear JSON desde ${elementId}:`, error)
      return { labels: [], data: [] }
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
  const ctxDistribucion = document.getElementById("distribucionCalificaciones")
  if (ctxDistribucion) {
    chartDistribucion = new Chart(ctxDistribucion.getContext("2d"), {
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
  }

  // 2. Gráfico de calificaciones por categoría
  const ctxCategorias = document.getElementById("calificacionesCategorias")
  if (ctxCategorias) {
    chartCategorias = new Chart(ctxCategorias.getContext("2d"), {
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
  }

  // 3. Gráfico de calificaciones por grupo de edad
  const ctxEdad = document.getElementById("calificacionesEdad")
  if (ctxEdad) {
    // Verificar si hay datos de edad disponibles
    if (datosEdad.labels && datosEdad.labels.length > 0) {
      chartEdad = new Chart(ctxEdad.getContext("2d"), {
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
    } else {
      // Si no hay datos, mostrar un mensaje
      ctxEdad.height = 100
      const ctx = ctxEdad.getContext("2d")
      ctx.font = "16px Arial"
      ctx.fillStyle = "#666"
      ctx.textAlign = "center"
      ctx.fillText("No hay datos suficientes para mostrar este gráfico", ctxEdad.width / 2, ctxEdad.height / 2)
    }
  }

  // 4. Gráfico de calificaciones por sexo
  const ctxSexo = document.getElementById("calificacionesSexo")
  if (ctxSexo) {
    chartSexo = new Chart(ctxSexo.getContext("2d"), {
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
  }

  // 5. Gráfico de radar para el perfil
  const ctxRadar = document.getElementById("perfilRadar")
  if (ctxRadar) {
    chartRadar = new Chart(ctxRadar.getContext("2d"), {
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
  }

  // 6. Gráfico de tendencia temporal
  const ctxTendencia = document.getElementById("tendenciaTemporal")
  if (ctxTendencia) {
    if (datosTendencia.labels && datosTendencia.labels.length > 0) {
      chartTendencia = new Chart(ctxTendencia.getContext("2d"), {
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
    } else {
      // Si no hay datos, mostrar un mensaje
      ctxTendencia.height = 100
      const ctx = ctxTendencia.getContext("2d")
      ctx.font = "16px Arial"
      ctx.fillStyle = "#666"
      ctx.textAlign = "center"
      ctx.fillText(
        "No hay datos suficientes para mostrar este gráfico",
        ctxTendencia.width / 2,
        ctxTendencia.height / 2,
      )
    }
  }

  // 7. Gráfico de correlación entre categorías (heatmap)
  const ctxCorrelacion = document.getElementById("correlacionCategorias")
  if (ctxCorrelacion) {
    // Para el heatmap, usamos un enfoque diferente ya que Chart.js no tiene un tipo de gráfico heatmap nativo
    // Creamos una visualización simple de correlación
    if (datosCorrelacion.labels && datosCorrelacion.labels.length > 0) {
      chartCorrelacion = new Chart(ctxCorrelacion.getContext("2d"), {
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
    } else {
      // Si no hay datos, mostrar un mensaje
      ctxCorrelacion.height = 100
      const ctx = ctxCorrelacion.getContext("2d")
      ctx.font = "16px Arial"
      ctx.fillStyle = "#666"
      ctx.textAlign = "center"
      ctx.fillText(
        "No hay datos suficientes para mostrar este gráfico",
        ctxCorrelacion.width / 2,
        ctxCorrelacion.height / 2,
      )
    }
  }

  // Manejo de filtros
  document.getElementById("filtroCategoria").addEventListener("change", aplicarFiltros)
  document.getElementById("filtroEdad").addEventListener("change", aplicarFiltros)
  document.getElementById("filtroSexo").addEventListener("change", aplicarFiltros)

  // Modificar la función aplicarFiltros para manejar la respuesta JSON
  function aplicarFiltros() {
    // Mostrar indicador de carga
    const cargando = document.getElementById("cargando")
    if (cargando) cargando.style.display = "flex"

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
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Error en la respuesta del servidor: ${response.status}`)
        }
        return response.text() // Obtener como texto primero
      })
      .then((text) => {
        // Intentar parsear el texto como JSON
        try {
          return JSON.parse(text)
        } catch (e) {
          console.error("Error al parsear JSON:", e)
          console.log("Texto recibido:", text)
          throw new Error("Error al parsear la respuesta del servidor")
        }
      })
      .then((data) => {
        // Ocultar indicador de carga
        if (cargando) cargando.style.display = "none"

        // Actualizar estadísticas
        document.getElementById("promedioGeneral").textContent = data.promedio_general.toFixed(2)
        document.getElementById("desviacionEstandar").textContent = data.desviacion_estandar.toFixed(2)
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
        // Ocultar indicador de carga
        if (cargando) cargando.style.display = "none"

        console.error("Error al filtrar datos:", error)
        alert("Ocurrió un error al filtrar los datos: " + error.message)
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
    if (graficos.calificaciones && chartDistribucion) {
      actualizarDatosGrafico(chartDistribucion, graficos.calificaciones)
    }

    if (graficos.categorias && chartCategorias) {
      actualizarDatosGrafico(chartCategorias, graficos.categorias)
    }

    if (graficos.edad && chartEdad) {
      actualizarDatosGrafico(chartEdad, graficos.edad)
    } else if (chartEdad) {
      // Si no hay datos de edad, limpiar el gráfico
      chartEdad.data.labels = []
      chartEdad.data.datasets[0].data = []
      chartEdad.update()

      // Mostrar mensaje de no hay datos suficientes
      const ctxEdad = document.getElementById("calificacionesEdad")
      if (ctxEdad) {
        const ctx = ctxEdad.getContext("2d")
        ctx.clearRect(0, 0, ctxEdad.width, ctxEdad.height)
        ctx.font = "16px Arial"
        ctx.fillStyle = "#666"
        ctx.textAlign = "center"
        ctx.fillText("No hay datos suficientes para mostrar este gráfico", ctxEdad.width / 2, ctxEdad.height / 2)
      }
    }

    if (graficos.sexo && chartSexo) {
      actualizarDatosGrafico(chartSexo, graficos.sexo)
    }

    if (graficos.radar && chartRadar) {
      actualizarDatosGrafico(chartRadar, graficos.radar)
    }

    if (graficos.tendencia && chartTendencia) {
      actualizarDatosGrafico(chartTendencia, graficos.tendencia)
    } else if (chartTendencia) {
      // Si no hay datos de tendencia, limpiar el gráfico
      chartTendencia.data.labels = []
      chartTendencia.data.datasets[0].data = []
      chartTendencia.update()

      // Mostrar mensaje de no hay datos suficientes
      const ctxTendencia = document.getElementById("tendenciaTemporal")
      if (ctxTendencia) {
        const ctx = ctxTendencia.getContext("2d")
        ctx.clearRect(0, 0, ctxTendencia.width, ctxTendencia.height)
        ctx.font = "16px Arial"
        ctx.fillStyle = "#666"
        ctx.textAlign = "center"
        ctx.fillText(
          "No hay datos suficientes para mostrar este gráfico",
          ctxTendencia.width / 2,
          ctxTendencia.height / 2,
        )
      }
    }

    if (graficos.correlacion && chartCorrelacion) {
      // Para el gráfico de correlación, necesitamos un manejo especial
      actualizarGraficoCorrelacion(chartCorrelacion, graficos.correlacion)
    }
  }

  // Modificar la función actualizarDatosGrafico para manejar valores null
  function actualizarDatosGrafico(chart, nuevosDatos) {
    if (!chart || !nuevosDatos) return

    // Actualizar etiquetas si existen
    if (nuevosDatos.labels) {
      chart.data.labels = nuevosDatos.labels
    }

    // Actualizar datos, reemplazando null por 0
    if (nuevosDatos.data) {
      chart.data.datasets[0].data = nuevosDatos.data.map((val) => (val === null ? 0 : val))
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

