document.addEventListener("DOMContentLoaded", () => {
    // Load products into the catalog
    fetch('/api/products')
      .then(response => response.json())
      .then(products => {
        const catalog = document.getElementById('product-catalog');
        products.forEach(product => {
          catalog.innerHTML += `
            <div class="product-card">
              <img src="${product.image_url}" alt="${product.name}">
              <h3>${product.name}</h3>
              <p>${product.price}</p>
              <button onclick="addToCart(${product.id})">Add to Cart</button>
            </div>
          `;
        });
      });
  
    // Load recommendations into the dashboard
    fetch(`/recommendations/${currentUserId}`)
      .then(response => response.json())
      .then(recommendations => {
        const recContainer = document.getElementById('recommendations');
        recommendations.forEach(rec => {
          recContainer.innerHTML += `
            <div class="recommendation-card">
              <img src="${rec.image_url}" alt="${rec.name}">
              <h3>${rec.name}</h3>
              <p>${rec.price}</p>
              <button onclick="addToCart(${rec.id})">Add to Cart</button>
            </div>
          `;
        });
      });
  });
  fetch('/recommendations/1')
  .then(response => {
    if (response.status === 401) {
      // Redirect to login page
      window.location.href = '/login';
    }
    return response.json();
  })
  .then(data => {
    console.log(data); // Handle recommendations
  });

  // Simulated add-to-cart functionality
  function addToCart(productId) {
    alert(`Product ID ${productId} added to cart!`);
  }
  // Add to cart
function addToCart(productId) {
  fetch('/cart', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ productId })
  })
  .then(response => response.json())
  .then(data => {
    alert(data.message);
  });
}

// Load cart items
function loadCart() {
  fetch('/cart')
    .then(response => response.json())
    .then(cart => {
      const cartContainer = document.getElementById('cart-items');
      cartContainer.innerHTML = '';
      cart.forEach(item => {
        cartContainer.innerHTML += `
          <div class="cart-item">
            <p>Product ID: ${item.productId}</p>
          </div>
        `;
      });
    });
}

  // Simulated logout
  function logout() {
    fetch('/logout', { method: 'POST' })
      .then(() => location.reload());
  }
  