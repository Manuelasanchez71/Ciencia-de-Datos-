document.addEventListener("DOMContentLoaded", () => {
    // Manejar los sliders
    document.querySelectorAll('input[type="range"]').forEach((slider) => {
      const output = slider.nextElementSibling
  
      // Función para actualizar la posición del output
      const updateOutputPosition = (slider, output) => {
        const min = slider.min ? Number.parseFloat(slider.min) : 0
        const max = slider.max ? Number.parseFloat(slider.max) : 100
        const newVal = Number(((slider.value - min) * 100) / (max - min))
        output.style.left = `calc(${newVal}% + (${8 - newVal * 0.15}px))`
      }
  
      // Inicializar la posición del output
      updateOutputPosition(slider, output)
  
      // Actualizar valor y posición cuando se mueve el slider
      slider.addEventListener("input", function () {
        output.textContent = this.value
        updateOutputPosition(this, output)
      })
    })
  
    document.getElementById("formulario").addEventListener("submit", (event) => {
      event.preventDefault()
  
      const respuestas = {
        nombre: document.getElementById("nombre").value,
        edad: Number.parseInt(document.getElementById("edad").value),
        sexo: document.getElementById("sexo").value,
        estado_civil: document.getElementById("estado_civil").value,
      }
  
      const inputs = document.querySelectorAll("input[type=range]")
      inputs.forEach((input) => {
        respuestas[input.name] = Number.parseInt(input.value) || 0
      })
  
      fetch("/guardar", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify(respuestas),
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
          }
          return response.json()
        })
        .then((data) => {
          console.log("Respuesta del servidor:", data)
          if (data.error) {
            throw new Error(data.error)
          } else {
            alert(data.mensaje || "Respuestas guardadas exitosamente.")
            // Redirigir a la página de "Mis Respuestas" después de guardar exitosamente
            window.location.href = "/mis_respuestas"
          }
        })
        .catch((error) => {
          console.error("Error en fetch:", error)
          alert("Ocurrió un error al enviar los datos: " + error.message)
        })
    })
  })
  
  