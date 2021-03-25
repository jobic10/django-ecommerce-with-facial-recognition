$(document).ready(function() {
    $(".update-cart").click(function() {
        var id = $(this).data("product");
        var action = $(this).data("action");
        make_ajax(id, action)
    })

    $(".edit-cart").click(function() {
        var id = $(this).data("product");
        var action = $(this).data("action");
        make_ajax(id, action)
        location.reload()
    })

    $("#form-button").click(function(event) {
        var address = $("[name='address']").val();
        var city = $("[name='city']").val();
        var phone = $("[name='phone']").val();
        var name = $("[name='name']").val();
        var email = $("[name='email']").val();

        $.ajax({
            url: '/validate_form/',
            data: {
                'csrfmiddlewaretoken': csrftoken,
                'address': address,
                'city': city,
                'phone': phone,
                'name': name? name: '',
                'email': email? email: '',
            },
            type: 'post',
            success: function(response) {
                $("#form-button").addClass('hidden');
                $("#payment-info").removeClass('hidden');
                $(".alert").addClass('hidden');
            },
            error: function(response) {
                var response = JSON.parse(JSON.stringify(response));
                var error = response.responseJSON.error;
                $(".alert").removeClass('hidden');
                $(".alert").text(error);
            }
        })
    })

    $("#make-payment").click(function(event) {
        console.log('make payment button')
    })

    function make_ajax(id, action) {
        $.ajax({
            url: '/update_item/',
            data: {
                'csrfmiddlewaretoken': csrftoken,
                'id': id,
                'action': action,
            },
            type: 'post',
            success: function(response) {
                if (action == 'add') {
                    var cart = $("#cart-total").text();
                    $("#cart-total").text(Number(cart) + 1);
                } else {
                    var cart = $("#cart-total").text();
                    $("#cart-total").text(Number(cart) - 1);
                }
                swal("Cart Updated", "Your cart has been updated successfully!", "success");
            },
            error: function(response) {
                console.log(response);
                var responseText = JSON.parse(response.responseText);

                var msg = responseText['error'];

                swal("Error", msg, "error");
            }
        })
    }

    //not used:
    function make_fetch(id, action) {
        var url = '/update_item/'
        fetch(url, {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrftoken},
            body: JSON.stringify({'id': id, 'action': action})
        })
        .then((response) => {
            return response.json()
        })
        .then((data) => {
            console.log(data);
        })
    }
})












