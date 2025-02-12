$(document).ready(function() {
  $('#partsTable').DataTable({
    "language": {
      "url": "//cdn.datatables.net/plug-ins/1.10.20/i18n/Spanish.json"
    }
  });
});

// CNOT-related code
document.addEventListener("DOMContentLoaded", function() {
  CNOT.init({
    apiKey: "your-api-key-here",
    targetElement: "#hierarchyTree"
  });
});
