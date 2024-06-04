document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('.sidenav');
    var instances = M.Sidenav.init(elems);

    var tabs = document.querySelectorAll('.tabs');
    M.Tabs.init(tabs);

    // Animate total activities count
    animateCount('activity-number', 1000);

    // User profile card animation
    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.classList.add('hovered');
        });
        card.addEventListener('mouseleave', () => {
            card.classList.remove('hovered');
        });
    });

    // Smooth scroll for tabs
    document.querySelectorAll('.tabs .tab a').forEach(tab => {
        tab.addEventListener('click', function(e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Show/hide content based on tab selection
    document.querySelectorAll('.tabs .tab a').forEach(tab => {
        tab.addEventListener('click', function() {
            if (this.getAttribute('href') === '#about') {
                document.querySelector('#activities').style.display = 'none';
            } else if (this.getAttribute('href') === '#activities') {
                document.querySelector('#about').style.display = 'none';
            }
        });
    });
});

$(document).ready(function(){
    $('#startButton').click(function(){
        $('#status').text('Starting video capture...');
        $('#loader').show(); // Show loader
        $.ajax({
            url: '/process_video',
            method: 'POST',
            success: function(response) {
                $('#loader').hide(); // Hide loader
                if (response.message.includes('Category: Crime')) {
                    var parts = response.message.split('Description:');
                    var categoryPart = parts[0];
                    var descriptionPart = parts.length > 1 ? 'Description:' + parts[1] : '';

                    $('#status').html('<div class="alert alert-custom-danger">⚠️ ' + categoryPart + '</div>');
                    $('#status').append('<div>' + descriptionPart + '</div>');
                    $('#status').append('<a href="#" class="notify-link visible">Notify Contact</a>');
                } else {
                    $('#status').html('<div class="alert alert-custom">' + response.message + '</div>');
                }
            },
            error: function() {
                $('#loader').hide(); // Hide loader
                $('#status').html('<div class="alert alert-custom-danger">Error starting video capture.</div>');
            }
        });
    });
});

$(document).ready(function(){
    $('.modal').modal();

    $('#button1').click(function() {
        sendVideo('/static/images/Assault033_x264.mov');
    });
    
    $('#button2').click(function() {
        sendVideo('/static/images/Assault033_x264.mov');
    });
});

function sendVideo(hardcodedValue) {
    $('#loader').show(); // Show loader
    $.ajax({
        url: '/process_video_sent',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(hardcodedValue),
        success: function(response) {
            if (response.message.includes('Category: Crime')) {
                $('#loader').hide(); // Hide loader
                var parts = response.message.split('Description:');
                var categoryPart = parts[0];
                var descriptionPart = parts.length > 1 ? 'Description:' + parts[1] : '';

                $('#responseText').html('<div class="alert alert-custom-danger">⚠️ ' + categoryPart + '</div>');
                $('#responseText').append('<div>' + descriptionPart + '</div>');
                $('#responseText').append('<a href="#" class="notify-link visible">Notify Contact</a>');

            } else {
                $('#responseText').html('<div class="alert alert-custom">' + response.message + '</div>');
            }
            $('#modal1').modal('open');
        },
        error: function(error) {
            $('#responseText').html('<div class="alert alert-custom">' + error.responseText + '</div>');
            $('#modal1').modal('open');
        }
    });
}

// Initialize and add the map
function initMap() {
    // The location of the first marker
    var location1 = { lat: -25.344, lng: 131.036 };
    var location2 = { lat: -26.344, lng: 132.036 };
    var location3 = { lat: -27.344, lng: 133.036 };

    // The map, centered at the first marker
    var map = new google.maps.Map(
        document.getElementById('map'), { zoom: 4, center: location1 });

    // The markers, positioned at the locations
    var marker1 = new google.maps.Marker({ position: location1, map: map });
    var marker2 = new google.maps.Marker({ position: location2, map: map });
    var marker3 = new google.maps.Marker({ position: location3, map: map });
}

// Function to animate the count
function animateCount(id, endValue) {
    let startValue = 0;
    const element = document.getElementById(id);
    const duration = 2000;
    const increment = endValue / (duration / 60);

    function updateCount() {
        startValue += increment;
        if (startValue < endValue) {
            element.textContent = Math.floor(startValue);
            requestAnimationFrame(updateCount);
        } else {
            element.textContent = endValue;
        }
    }

    updateCount();
}