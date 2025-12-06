document.addEventListener("DOMContentLoaded", function () {
  console.log("Custom JS loaded!");

  // Example: alert on contact form submission
  const btn = document.querySelector("button.btn-primary");
  if (btn) {
    btn.addEventListener("click", function (e) {
      alert("Form submitted!");
    });
  }
});
