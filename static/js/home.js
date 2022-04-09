$(function() {
  /* NOTE: hard-refresh the browser once you've updated this */
  $(".typed").typed({
    strings: [
      "stat jess.human<br/>" +
      "><span class='caret'>$</span> skills: fullstack development, python, Django, React, REST API <br/> ^100" +
      "><span class='caret'>$</span> hobbies: coding, basketball ,football, travel, writing <br/> ^300" +
      "><span class='caret'>$</span> highlights:  <a href='https://jessiecodes-reminderapp.herokuapp.com/'>task tracker app using REACT, Django REST and celery </a><br/>"
    ],
    showCursor: true,
    cursorChar: '_',
    autoInsertCss: true,
    typeSpeed: 0.001,
    startDelay: 50,
    loop: false,
    showCursor: false,
    onStart: $('.message form').hide(),
    onStop: $('.message form').show(),
    onTypingResumed: $('.message form').hide(),
    onTypingPaused: $('.message form').show(),
    onComplete: $('.message form').show(),
    onStringTyped: function(pos, self) {$('.message form').show();},
  });
  $('.message form').hide()
});