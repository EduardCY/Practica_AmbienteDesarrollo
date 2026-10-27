/**
 * Cliente JavaScript Fetch API para MiniWebApp (Usuarios y Productos).
 *
 * Referencia: 2024-01 Practica REST_MYSQL.pdf — Ejercicios 2 y 5.c.
 * Implementa las operaciones CRUD asíncronas contra los endpoints REST:
 * - /api/users    (getUsers, createUser, updateUser, deleteUser)
 * - /api/products (getProducts, createProduct, updateProduct, deleteProduct)
 */

// ============================================================================
// 1. GESTIÓN DE USUARIOS (/api/users)
// ============================================================================

function getUsers() {
    fetch('/api/users')
        .then(response => response.json())
        .then(data => {
            var userListBody = document.querySelector('#user-list tbody');
            if (!userListBody) return;
            userListBody.innerHTML = '';

            data.forEach(user => {
                var row = document.createElement('tr');

                // ID
                var idCell = document.createElement('td');
                idCell.textContent = user.id;
                row.appendChild(idCell);

                // Name
                var nameCell = document.createElement('td');
                nameCell.textContent = user.name;
                row.appendChild(nameCell);

                // Email
                var emailCell = document.createElement('td');
                emailCell.textContent = user.email;
                row.appendChild(emailCell);

                // Username
                var usernameCell = document.createElement('td');
                usernameCell.textContent = user.username;
                row.appendChild(usernameCell);

                // Actions
                var actionsCell = document.createElement('td');

                var editLink = document.createElement('a');
                editLink.href = `/edit/${user.id}`;
                editLink.textContent = 'Edit';
                editLink.className = 'btn btn-sm btn-primary mr-2';
                actionsCell.appendChild(editLink);

                var deleteLink = document.createElement('a');
                deleteLink.href = '#';
                deleteLink.textContent = 'Delete';
                deleteLink.className = 'btn btn-sm btn-danger';
                deleteLink.addEventListener('click', function(e) {
                    e.preventDefault();
                    deleteUser(user.id);
                });
                actionsCell.appendChild(deleteLink);

                row.appendChild(actionsCell);
                userListBody.appendChild(row);
            });
        })
        .catch(error => console.error('Error fetching users:', error));
}

function createUser() {
    var data = {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        username: document.getElementById('username').value,
        password: document.getElementById('password').value
    };

    fetch('/api/users', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error al crear usuario');
        }
        return response.json();
    })
    .then(() => {
        document.getElementById('add-user-form').reset();
        getUsers();
    })
    .catch(error => console.error('Error:', error));
}

function updateUser() {
    var userId = document.getElementById('user-id').value;
    var data = {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        username: document.getElementById('username').value,
        password: document.getElementById('password').value
    };

    fetch(`/api/users/${userId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error al actualizar usuario');
        }
        return response.json();
    })
    .then(() => {
        window.location.href = '/';
    })
    .catch(error => console.error('Error:', error));
}

function deleteUser(userId) {
    if (confirm('Are you sure you want to delete this user?')) {
        fetch(`/api/users/${userId}`, {
            method: 'DELETE',
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error al eliminar usuario');
            }
            return response.json();
        })
        .then(() => {
            getUsers();
        })
        .catch(error => console.error('Error:', error));
    }
}

// ============================================================================
// 2. GESTIÓN DE PRODUCTOS (/api/products) — EJERCICIO 5.c
// ============================================================================

function getProducts() {
    fetch('/api/products')
        .then(response => response.json())
        .then(data => {
            var productListBody = document.querySelector('#product-list tbody');
            if (!productListBody) return;
            productListBody.innerHTML = '';

            data.forEach(product => {
                var row = document.createElement('tr');

                // ID
                var idCell = document.createElement('td');
                idCell.textContent = product.id;
                row.appendChild(idCell);

                // Name
                var nameCell = document.createElement('td');
                nameCell.textContent = product.name;
                row.appendChild(nameCell);

                // Description
                var descCell = document.createElement('td');
                descCell.textContent = product.description;
                row.appendChild(descCell);

                // Price
                var priceCell = document.createElement('td');
                priceCell.textContent = `$${ Number(product.price).toFixed(2) }`;
                row.appendChild(priceCell);

                // Stock
                var stockCell = document.createElement('td');
                stockCell.textContent = product.stock;
                row.appendChild(stockCell);

                // Actions
                var actionsCell = document.createElement('td');

                var editLink = document.createElement('a');
                editLink.href = `/edit_product/${product.id}`;
                editLink.textContent = 'Edit';
                editLink.className = 'btn btn-sm btn-primary mr-2';
                actionsCell.appendChild(editLink);

                var deleteLink = document.createElement('a');
                deleteLink.href = '#';
                deleteLink.textContent = 'Delete';
                deleteLink.className = 'btn btn-sm btn-danger';
                deleteLink.addEventListener('click', function(e) {
                    e.preventDefault();
                    deleteProduct(product.id);
                });
                actionsCell.appendChild(deleteLink);

                row.appendChild(actionsCell);
                productListBody.appendChild(row);
            });
        })
        .catch(error => console.error('Error fetching products:', error));
}

function createProduct() {
    var data = {
        name: document.getElementById('prod-name').value,
        description: document.getElementById('prod-description').value,
        price: parseFloat(document.getElementById('prod-price').value) || 0.0,
        stock: parseInt(document.getElementById('prod-stock').value, 10) || 0
    };

    fetch('/api/products', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error al crear producto');
        }
        return response.json();
    })
    .then(() => {
        document.getElementById('add-product-form').reset();
        getProducts();
    })
    .catch(error => console.error('Error:', error));
}

function updateProduct() {
    var productId = document.getElementById('product-id').value;
    var data = {
        name: document.getElementById('prod-name').value,
        description: document.getElementById('prod-description').value,
        price: parseFloat(document.getElementById('prod-price').value) || 0.0,
        stock: parseInt(document.getElementById('prod-stock').value, 10) || 0
    };

    fetch(`/api/products/${productId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error al actualizar producto');
        }
        return response.json();
    })
    .then(() => {
        window.location.href = '/products';
    })
    .catch(error => console.error('Error:', error));
}

function deleteProduct(productId) {
    if (confirm('Are you sure you want to delete this product?')) {
        fetch(`/api/products/${productId}`, {
            method: 'DELETE',
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error al eliminar producto');
            }
            return response.json();
        })
        .then(() => {
            getProducts();
        })
        .catch(error => console.error('Error:', error));
    }
}
