const nav = document.querySelector('.nav');
const menu = document.querySelector('.nav__menu');
const menuOpen = document.querySelector('.nav__menu--open');
const menuClose = document.querySelector('.nav__menu--close');

nav.addEventListener('click', () => {
  if (menu.classList.contains('nav__menu--open')) {
    menu.classList.remove('nav__menu--open');
    menu.classList.add('nav__menu');
  } else {
    menu.classList.add('nav__menu--open');
    menu.classList.remove('nav__menu');
  }
});
