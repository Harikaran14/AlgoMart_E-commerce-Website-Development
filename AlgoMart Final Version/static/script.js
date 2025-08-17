var blk = document.querySelector(".overlay")
var cart = document.querySelector(".overover")
var cartbutton = document.getElementById("cartbutton")
var back = document.getElementById("back")

// Define functions
function showCart() {
    blk.style.display = "block"
    cart.style.display = "block"
    sessionStorage.setItem("cartVisible", "true")
}

function hideCart() {
    blk.style.display = "none"
    cart.style.display = "none"
    sessionStorage.setItem("cartVisible", "false")
}

// Event listeners
cartbutton.addEventListener("click", showCart)
back.addEventListener("click", hideCart)

// Restore state on page load
window.addEventListener("load", function() {
    if (sessionStorage.getItem("cartVisible") === "true") {
        showCart()
    } else {
        hideCart()
    }
})

// Save scroll position before leaving
window.addEventListener("beforeunload", function () {
    localStorage.setItem("scrollY", window.scrollY);
});

// Restore scroll position when coming back
window.addEventListener("load", function () {
    if (localStorage.getItem("scrollY") !== null) {
        window.scrollTo(0, localStorage.getItem("scrollY"));
    }
});