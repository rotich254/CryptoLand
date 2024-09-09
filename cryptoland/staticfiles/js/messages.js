               // Include the JavaScript from above
               document.addEventListener('DOMContentLoaded', function() {
                const messages = document.querySelectorAll('#message-container .alert');
                if (messages.length > 0) {
                    setTimeout(function() {
                        messages.forEach(function(message) {
                            message.style.transition = 'opacity 0.5s ease';
                            message.style.opacity = '0';
                            setTimeout(function() {
                                message.remove();
                            }, 500);
                        });
                    }, 3000);
                }
            });