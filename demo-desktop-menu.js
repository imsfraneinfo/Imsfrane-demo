const desktopMenu = document.querySelector('.atnav-desktop-demo');

if (desktopMenu) {
  const openDropdown = () => desktopMenu.querySelector('details[open]');

  document.addEventListener('click', (event) => {
    const dropdown = openDropdown();
    if (dropdown && !dropdown.contains(event.target)) dropdown.open = false;
  });

  desktopMenu.addEventListener('keydown', (event) => {
    const dropdown = openDropdown();
    if (event.key !== 'Escape' || !dropdown) return;
    event.preventDefault();
    dropdown.open = false;
    dropdown.querySelector('summary').focus();
  });

  matchMedia('(min-width: 1100px)').addEventListener('change', (event) => {
    if (event.matches && document.querySelector('#atnavDrawer.is-open')) {
      document.querySelector('#atnavClose').click();
      desktopMenu.querySelector('a').focus();
    }
    const dropdown = openDropdown();
    if (!event.matches && dropdown) dropdown.open = false;
  });
}
