function ingToggleHandler(el){
    el.labels[0].style.textDecoration = el.checked ? "line-through" : "solid"
    el.labels[0].style.opacity = el.checked ? "0.5" : "1.0";
    el.style.opacity = el.checked ? "0.5" : "1.0";
  }
function methToggleHandler(el){
    // el.labels[0].style.textDecoration = el.checked ? "line-through" : "solid"
    el.parentNode.style.textDecoration = el.checked ? "line-through" : "solid"
    el.parentNode.style.opacity = el.checked ? "0.5" : "1.0";
  }