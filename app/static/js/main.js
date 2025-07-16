// JavaScript principal para el sistema de servicio técnico

// Import Bootstrap
var bootstrap = window.bootstrap

document.addEventListener("DOMContentLoaded", () => {
  // Inicializar tooltips de Bootstrap
  var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  var tooltipList = tooltipTriggerList.map((tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl))

  // Auto-ocultar alertas después de 5 segundos
  setTimeout(() => {
    var alerts = document.querySelectorAll(".alert")
    alerts.forEach((alert) => {
      var bsAlert = new bootstrap.Alert(alert)
      bsAlert.close()
    })
  }, 5000)

  // Confirmación para eliminaciones
  var deleteButtons = document.querySelectorAll("[data-confirm-delete]")
  deleteButtons.forEach((button) => {
    button.addEventListener("click", (e) => {
      if (!confirm("¿Está seguro de que desea eliminar este elemento? Esta acción no se puede deshacer.")) {
        e.preventDefault()
      }
    })
  })

  // Cálculo automático de totales en facturas
  var subtotalInput = document.getElementById("subtotal")
  var impuestosInput = document.getElementById("impuestos")
  var totalInput = document.getElementById("total")

  if (subtotalInput && impuestosInput && totalInput) {
    function calcularTotal() {
      var subtotal = Number.parseFloat(subtotalInput.value) || 0
      var impuestos = Number.parseFloat(impuestosInput.value) || 0
      var total = subtotal + impuestos
      totalInput.value = total.toFixed(2)
    }

    subtotalInput.addEventListener("input", calcularTotal)
    impuestosInput.addEventListener("input", calcularTotal)
  }

  // Filtros dinámicos en tablas
  var searchInputs = document.querySelectorAll("[data-table-search]")
  searchInputs.forEach((input) => {
    input.addEventListener("input", function () {
      var filter = this.value.toLowerCase()
      var table = document.querySelector(this.dataset.tableSearch)
      var rows = table.querySelectorAll("tbody tr")

      rows.forEach((row) => {
        var text = row.textContent.toLowerCase()
        row.style.display = text.includes(filter) ? "" : "none"
      })
    })
  })

  // Canvas para firma digital
  var canvas = document.getElementById("signature-canvas")
  if (canvas) {
    var ctx = canvas.getContext("2d")
    var isDrawing = false
    var lastX = 0
    var lastY = 0

    function startDrawing(e) {
      isDrawing = true
      var rect = canvas.getBoundingClientRect()
      lastX = (e.clientX || e.touches[0].clientX) - rect.left
      lastY = (e.clientY || e.touches[0].clientY) - rect.top
    }

    function draw(e) {
      if (!isDrawing) return

      var rect = canvas.getBoundingClientRect()
      var currentX = (e.clientX || e.touches[0].clientX) - rect.left
      var currentY = (e.clientY || e.touches[0].clientY) - rect.top

      ctx.beginPath()
      ctx.moveTo(lastX, lastY)
      ctx.lineTo(currentX, currentY)
      ctx.strokeStyle = "#000"
      ctx.lineWidth = 2
      ctx.lineCap = "round"
      ctx.stroke()

      lastX = currentX
      lastY = currentY
    }

    function stopDrawing() {
      isDrawing = false
    }

    // Eventos para mouse
    canvas.addEventListener("mousedown", startDrawing)
    canvas.addEventListener("mousemove", draw)
    canvas.addEventListener("mouseup", stopDrawing)
    canvas.addEventListener("mouseout", stopDrawing)

    // Eventos para touch (dispositivos móviles)
    canvas.addEventListener("touchstart", (e) => {
      e.preventDefault()
      startDrawing(e)
    })
    canvas.addEventListener("touchmove", (e) => {
      e.preventDefault()
      draw(e)
    })
    canvas.addEventListener("touchend", (e) => {
      e.preventDefault()
      stopDrawing()
    })

    // Botón para limpiar firma
    var clearButton = document.getElementById("clear-signature")
    if (clearButton) {
      clearButton.addEventListener("click", () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height)
        document.getElementById("firma_cliente").value = ""
      })
    }

    // Guardar firma como base64
    var saveButton = document.getElementById("save-signature")
    if (saveButton) {
      saveButton.addEventListener("click", () => {
        var dataURL = canvas.toDataURL()
        document.getElementById("firma_cliente").value = dataURL
      })
    }
  }

  // Cálculo automático de tiempo en reportes
  var horaInicioInput = document.getElementById("hora_inicio")
  var horaFinInput = document.getElementById("hora_fin")
  var tiempoTotalSpan = document.getElementById("tiempo_total")

  if (horaInicioInput && horaFinInput && tiempoTotalSpan) {
    function calcularTiempo() {
      var inicio = horaInicioInput.value
      var fin = horaFinInput.value

      if (inicio && fin) {
        var inicioMinutos = convertirAMinutos(inicio)
        var finMinutos = convertirAMinutos(fin)

        if (finMinutos > inicioMinutos) {
          var diferencia = finMinutos - inicioMinutos
          var horas = Math.floor(diferencia / 60)
          var minutos = diferencia % 60
          tiempoTotalSpan.textContent = horas + "h " + minutos + "m"
        }
      }
    }

    function convertirAMinutos(tiempo) {
      var partes = tiempo.split(":")
      return Number.parseInt(partes[0]) * 60 + Number.parseInt(partes[1])
    }

    horaInicioInput.addEventListener("change", calcularTiempo)
    horaFinInput.addEventListener("change", calcularTiempo)
  }

  // Validación de formularios
  var forms = document.querySelectorAll(".needs-validation")
  forms.forEach((form) => {
    form.addEventListener("submit", (event) => {
      if (!form.checkValidity()) {
        event.preventDefault()
        event.stopPropagation()
      }
      form.classList.add("was-validated")
    })
  })
})

// Función para mostrar notificaciones
function showNotification(message, type = "info") {
  var alertDiv = document.createElement("div")
  alertDiv.className = `alert alert-${type} alert-dismissible fade show`
  alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `

  var container = document.querySelector(".container-fluid") || document.body
  container.insertBefore(alertDiv, container.firstChild)

  setTimeout(() => {
    alertDiv.remove()
  }, 5000)
}

// Función para formatear números como moneda
function formatCurrency(amount) {
  return new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
  }).format(amount)
}

// Función para formatear fechas
function formatDate(date) {
  return new Intl.DateTimeFormat("es-CO", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date(date))
}
