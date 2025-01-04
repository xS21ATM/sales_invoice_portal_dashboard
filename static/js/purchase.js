document.getElementById('form_create_sale').addEventListener('submit', function (event) {
    event.preventDefault(); // Prevent default form submission

    const products = [];
    const rows = document.querySelectorAll('#product-details-body tr');

    rows.forEach(row => {
        const product = {
            product_id: row.querySelector('select[name="product[]"]').value,
            description: row.querySelector('input[name="name[]"]').value,
            product_uom_qty: row.querySelector('input[name="product_uom_qty[]"]').value,
            price_unit: row.querySelector('input[name="price_unit[]"]').value
        };
        products.push(product);
    });
    console.log(products);

    // Convert products array to JSON string
    const productsJson = JSON.stringify(products);

    // Add productsJson to a hidden input or send via AJAX
    const hiddenInput = document.createElement('input');
    hiddenInput.type = 'hidden';
    hiddenInput.name = 'products';
    hiddenInput.value = productsJson;
    this.appendChild(hiddenInput);

    // Now submit the form
    this.submit();
});
