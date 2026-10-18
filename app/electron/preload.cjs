'use strict';

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('rcDesktop', {
  isDesktopShell: true,
  setWindowTheme(theme) {
    ipcRenderer.send('desktop:set-window-theme', theme);
  },
});
