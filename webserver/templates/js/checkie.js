function isIE()
{
  return /msie/i.test(navigator.userAgent) && !/opera/i.test(navigator.userAgent);
}

if( isIE() ) {
    alert("Sorry, this site does not work in Internet Explorer.");
}

