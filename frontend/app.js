async function cargarAprendices() {
  const tbody = document.getElementById("tabla-aprendices");
  try {
    const respuesta = await fetch("/api/aprendices");
    if (!respuesta.ok) throw new Error("Error " + respuesta.status);
    const aprendices = await respuesta.json();
    tbody.innerHTML = "";
    if (aprendices.length === 0) {
      tbody.innerHTML =
        '<tr><td colspan="5" class="text-center text-muted">No hay registros aún.</td></tr>';
      return;
    }
    aprendices.forEach((a) => {
      const fila = document.createElement("tr");
      fila.innerHTML =
        `<td>${a.id}</td>` +
        `<td>${a.nombre_completo}</td>` +
        `<td>${a.numero_documento}</td>` +
        `<td>${a.ficha}</td>` +
        `<td>${a.creado_en}</td>`;
      tbody.appendChild(fila);
    });
  } catch (error) {
    tbody.innerHTML =
      `<tr><td colspan="5" class="text-center text-danger">No se pudo conectar con la API: ${error.message}</td></tr>`;
  }
}

document.getElementById("form-registro").addEventListener("submit", async (e) => {
  e.preventDefault();
  const body = {
    nombre_completo: document.getElementById("nombre_completo").value.trim(),
    numero_documento: document.getElementById("numero_documento").value.trim(),
    ficha: document.getElementById("ficha").value.trim(),
  };
  const respuesta = await fetch("/api/registrar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (respuesta.ok) {
    document.getElementById("form-registro").reset();
    cargarAprendices();
  } else {
    alert("No se pudo registrar el aprendiz");
  }
});

cargarAprendices();
