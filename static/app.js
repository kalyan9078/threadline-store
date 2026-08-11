const grid = document.querySelector('#productGrid');
const cart = JSON.parse(localStorage.getItem('threadline-cart') || '[]');
const money = n => `$${Number(n).toFixed(2)}`;

function saveCart() { localStorage.setItem('threadline-cart', JSON.stringify(cart)); renderCart(); }
function renderCart() {
  document.querySelector('#cartCount').textContent = cart.reduce((n, i) => n + i.quantity, 0);
  const holder = document.querySelector('#cartItems');
  holder.innerHTML = cart.length ? cart.map(item => `<article class="cart-item"><img src="${item.image_url}" alt=""><div><h3>${item.name}</h3><p>${money(item.price)} · Qty ${item.quantity}</p><button data-remove="${item.id}">Remove</button></div></article>`).join('') : '<p class="empty">Your bag is waiting for something good.</p>';
  document.querySelector('#cartTotal').textContent = money(cart.reduce((n, i) => n + i.price * i.quantity, 0));
}
function addToCart(product) { const found = cart.find(i => i.id === product.id); found ? found.quantity++ : cart.push({...product, quantity: 1}); saveCart(); openCart(); }
function openCart() { document.body.classList.add('cart-open'); document.querySelector('#cartPanel').setAttribute('aria-hidden', 'false'); }
function closeCart() { document.body.classList.remove('cart-open'); document.querySelector('#cartPanel').setAttribute('aria-hidden', 'true'); }
async function loadProducts(category = 'All') {
  grid.innerHTML = '<p class="loading">Curating the edit…</p>';
  const res = await fetch(`/api/products?category=${encodeURIComponent(category)}`); const products = await res.json();
  grid.innerHTML = products.map(p => `<article class="product"><div class="product-image"><img src="${p.image_url}" alt="${p.name}">${p.badge ? `<span>${p.badge}</span>` : ''}<button data-product='${JSON.stringify(p)}'>Add to bag</button></div><div class="product-meta"><div><h3>${p.name}</h3><p>${p.category}</p></div><strong>${money(p.price)}</strong></div></article>`).join('');
}
document.querySelector('#filters').addEventListener('click', e => { if (!e.target.dataset.category) return; document.querySelectorAll('.filters button').forEach(b => b.classList.toggle('active', b === e.target)); loadProducts(e.target.dataset.category); });
grid.addEventListener('click', e => { if (e.target.dataset.product) addToCart(JSON.parse(e.target.dataset.product)); });
document.querySelector('#cartButton').onclick = openCart; document.querySelector('#closeCart').onclick = closeCart; document.querySelector('#overlay').onclick = closeCart;
document.querySelector('#cartItems').onclick = e => { const id = Number(e.target.dataset.remove); if (!id) return; const idx = cart.findIndex(i => i.id === id); cart.splice(idx, 1); saveCart(); };
document.querySelector('#checkoutButton').onclick = () => { if (!cart.length) return; document.querySelector('#checkoutDialog').showModal(); };
document.querySelector('#closeDialog').onclick = () => document.querySelector('#checkoutDialog').close();
document.querySelector('#checkoutForm').addEventListener('submit', async e => { e.preventDefault(); const form = new FormData(e.target); const message = document.querySelector('#checkoutMessage'); const r = await fetch('/api/orders', {method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({name: form.get('name'), email: form.get('email'), items: cart})}); const data = await r.json(); if (r.ok) { cart.splice(0); saveCart(); e.target.reset(); message.textContent = `Thank you — order #${data.order_id} is confirmed.`; } else message.textContent = data.error; });
document.querySelector('#newsletterForm').addEventListener('submit', e => { e.preventDefault(); e.target.reset(); document.querySelector('#newsletterMessage').textContent = 'You’re on the list. Welcome in.'; });
renderCart(); loadProducts();
