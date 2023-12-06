// Obtén el enlace y el ícono de la campana
let enlaceNotificaciones = document.querySelector(".enlace_notificaciones");
let iconoCampana = enlaceNotificaciones.querySelector(".fa-bell");
let badge = enlaceNotificaciones.querySelector(".badge");

// Agrega un controlador de eventos de clic al enlace
enlaceNotificaciones.addEventListener("click", function () {
  // Elimina el badge
  if (badge) {
    badge.remove();
  }

  // Cambia el ícono de la campana
  iconoCampana.classList.remove("fa-shake");
});