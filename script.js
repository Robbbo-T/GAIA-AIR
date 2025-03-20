// Toggle tree visibility on click
document.querySelectorAll(".tree li > span").forEach(item => {
  item.addEventListener("click", function () {
    const parent = this.parentElement;
    parent.classList.toggle("expanded");
  });
});

// Search function
function searchTree() {
  const query = document.getElementById("searchInput").value.toLowerCase();
  const treeItems = document.querySelectorAll(".tree li");

  treeItems.forEach(item => {
    item.style.display = "none";
    item.classList.remove("highlight");
  });

  const matchingItems = Array.from(treeItems).filter(item => {
    const text = item.innerText.toLowerCase();
    return text.includes(query);
  });

  matchingItems.forEach(item => {
    item.style.display = "block";
    item.classList.add("highlight");

    // Expand parent nodes
    let parent = item.parentElement;
    while (parent && parent.tagName === "UL") {
      parent.style.display = "block";
      parent.parentElement.classList.add("expanded");
      parent = parent.parentElement.parentElement;
    }
  });
}

// CNOT-related code
document.addEventListener("DOMContentLoaded", function() {
  CNOT.init({
    apiKey: "your-api-key-here",
    targetElement: "#hierarchyTree"
  });
});
