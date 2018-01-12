/**
 * Generate an avatar image from letters
 */

function AvatarImage(letters, size) {
  var canvas = document.createElement('canvas');
  var context = canvas.getContext("2d");
  var size = size || 60;

  // Generate a random color every time function is called
  // var color =  "#" + (Math.random() * 0xFFFFFF << 0).toString(16);
  var color = "#51bfdb";

  // Set canvas with & height
  canvas.width = size;
  canvas.height = size;

  // Select a font family to support different language characters
  // like Arial
  context.font = Math.round(canvas.width / 2) + "px Arial";
  context.textAlign = "center";

  // Setup background and front color
  context.fillStyle = color;
  context.fillRect(0, 0, canvas.width, canvas.height);
  context.fillStyle = "#FFF";
  context.fillText(letters, size / 2, size / 1.5);

  // Set image representation in default format (png)
  dataURI = canvas.toDataURL();

  // Dispose canvas element
  canvas = null;

  return dataURI;
}

function generateAvatars() {
  var images = document.querySelectorAll('img[letters]');

  for (var i = 0, len = images.length; i < len; i++) {
    var img = images[i];
    img.src = AvatarImage(img.getAttribute('letters'), img.getAttribute('width'));
    img.removeAttribute('letters');
  }
}

// If jQuery is included in the page, adds a jQuery plugin to handle it as well
if ( typeof jQuery != "undefined" )
	jQuery.fn.generateAvatars = function(){
		return this.each(function(){
			var generate_avatars = generateAvatars(this.title);
			if ( generate_avatars )
				jQuery(this).text( generate_avatars );
		});
	};

