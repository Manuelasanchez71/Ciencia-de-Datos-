document.getElementById("formulario").addEventListener("submit", function(event) {
    event.preventDefault();

    let respuestas = {
        nombre: document.getElementById("nombre").value,
        edad: parseInt(document.getElementById("edad").value),
        sexo: document.getElementById("sexo").value,
        estado_civil: document.getElementById("estado_civil").value
    };

    let inputs = document.querySelectorAll("input[type=number]");
    inputs.forEach((input) => {
        respuestas[input.name] = parseInt(input.value) || 0;
    });

    fetch("/guardar", {
        method: "POST",
        headers: { 
            "Content-Type": "application/json",
            "Accept": "application/json" 
        },
        body: JSON.stringify(respuestas)
    })
    .then(response => response.json())
    .then(data => {
        console.log("Respuesta del servidor:", data);
        if (data.error) {
            alert("Error: " + data.error);
        } else {
            alert(data.mensaje || "Respuestas guardadas exitosamente.");
            document.getElementById("btnDescargarExcel").style.display = "block";
        }
    })
    .catch(error => {
        console.error("Error en fetch:", error);
        alert("Ocurrió un error al enviar los datos.");
    });
});

document.getElementById("btnDescargarExcel").addEventListener("click", function() {
    window.location.href = "/descargar_excel";
});